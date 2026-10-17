"""The `mkdocs-to-pdf` plugin entry point."""

import logging
import os
import pathlib
from collections.abc import Callable
from timeit import default_timer as timer
from typing import TextIO

from mkdocs.config.base import Config
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page
from weasyprint.logger import LOGGER

from .drivers.event_hook import EventHookHandler
from .generator import Generator
from .options import Options

logging.getLogger(__name__)

_DISABLED_MSG = "without generate PDF(set environment variable %s to 1 to enable)"


class _WeasyPrintLogHandler(logging.StreamHandler[TextIO]):
    """
    Console handler for WeasyPrint's logger.

    WeasyPrint attaches a ``NullHandler`` to its logger and MkDocs never adds
    one, so without this its records (for example images that fail to load)
    are silently discarded.
    """


def _mkdocs_formatter() -> logging.Formatter:
    """Return MkDocs' console formatter, or a plain fallback."""
    for handler in logging.getLogger("mkdocs").handlers:
        if handler.formatter is not None:
            return handler.formatter
    return logging.Formatter("%(levelname)-8s-  %(message)s")


def _setup_weasyprint_logging() -> None:
    """Route WeasyPrint's logs to the console, exactly once."""
    if any(isinstance(handler, _WeasyPrintLogHandler) for handler in LOGGER.handlers):
        return

    handler = _WeasyPrintLogHandler()
    handler.setFormatter(_mkdocs_formatter())
    LOGGER.addHandler(handler)


class _ErrorAndWarningCountFilter(logging.Filter):
    """Counts all ERROR and WARNING level log messages."""

    _error_count = 0
    _warning_count = 0

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Count the record if it is an error or warning.

        Args:
            record: The log record.

        Returns:
            Always True, so the record is not filtered out.

        """
        if record.levelno == logging.ERROR:
            self._error_count += 1
        elif record.levelno == logging.WARNING:
            self._warning_count += 1
        return True

    def counts(self) -> tuple[int, int]:
        """Return the counted number of errors and warnings."""
        return (self._error_count, self._warning_count)


class _CaptureWarnings:
    """Capture bs4 warnings onto the given log filter."""

    def __init__(self, log_filter: logging.Filter) -> None:
        """
        Start capturing warnings and attach the filter.

        Args:
            log_filter: The filter that counts warnings.

        """
        logging.captureWarnings(True)  # ruff: ignore[boolean-positional-value-in-call]
        self._logger = logging.getLogger("py.warnings")
        self._logger.addFilter(log_filter)
        self._filter = log_filter

    def __del__(self) -> None:
        """Stop capturing warnings."""
        logging.captureWarnings(False)  # ruff: ignore[boolean-positional-value-in-call]
        self._logger.removeFilter(self._filter)


class WithPdfPlugin(BasePlugin):  # type: ignore[type-arg,no-untyped-call]  # ty: ignore[missing-type-argument]
    """Generate a single PDF from an MkDocs repository."""

    config_scheme = Options.config_scheme

    def __init__(self) -> None:
        """Initialise the plugin state."""
        self._logger = logging.getLogger("mkdocs.to-pdf")
        self._logger.setLevel(logging.INFO)

        self.generator: Generator | None = None
        self.enabled = False

        self._options: Options | None = None

        self._num_pages = 0
        self._total_time: float = 0

        self._error_counter: _ErrorAndWarningCountFilter | None = None

    def on_serve(
        self,
        server: LiveReloadServer,
        config: Config,  # ruff: ignore[unused-method-argument]
        builder: Callable[[], None],
        **kwargs: object,  # ruff: ignore[unused-method-argument]
    ) -> LiveReloadServer:
        """
        Watch the event hook module while serving.

        Args:
            server: The live-reload server.
            config: The MkDocs config.
            builder: The rebuild callback.
            **kwargs: Ignored.

        Returns:
            The live-reload server.

        """
        EventHookHandler.on_serve(server, builder, self._logger)

        return server

    def on_config(self, config: Config) -> None:
        """
        Resolve options and prepare the generator.

        Args:
            config: The MkDocs config.

        """
        if "enabled_if_env" in self.config:
            env_name = self.config["enabled_if_env"]
            if env_name:
                self.enabled = os.environ.get(env_name) == "1"
                if not self.enabled:
                    self._logger.info(_DISABLED_MSG, env_name)
                    return
            else:
                self.enabled = True
        else:
            self.enabled = True

        self._options = Options(self.config, config, self._logger)

        _setup_weasyprint_logging()

        if self._options.verbose:
            LOGGER.setLevel(logging.DEBUG)
            self._logger.setLevel(logging.DEBUG)
        else:
            LOGGER.setLevel(logging.ERROR)

        if self._options.strict:
            self._error_counter = _ErrorAndWarningCountFilter()
            LOGGER.addFilter(self._error_counter)
            self._logger.addFilter(self._error_counter)

        self.generator = Generator(options=self._options)

    def on_nav(
        self,
        nav: Navigation,
        config: Config,  # ruff: ignore[unused-method-argument]
        files: Files,  # ruff: ignore[unused-method-argument]
    ) -> Navigation:
        """
        Prepare the generator with the navigation.

        Args:
            nav: The navigation.
            config: The MkDocs config.
            files: The files collection.

        Returns:
            The navigation.

        """
        if not self.enabled or self.generator is None:
            return nav

        _ = _CaptureWarnings(self._error_counter) if self._error_counter else None
        self.generator.on_nav(nav)
        return nav

    def on_post_page(
        self,
        output_content: str,
        page: Page,
        config: Config,  # ruff: ignore[unused-method-argument]
    ) -> str:
        """
        Collect the page article and inject the PDF link.

        Args:
            output_content: The rendered page HTML.
            page: The page.
            config: The MkDocs config.

        Returns:
            The modified page HTML.

        """
        if not self.enabled or self.generator is None:
            return output_content

        _ = _CaptureWarnings(self._error_counter) if self._error_counter else None

        self._num_pages += 1
        start = timer()
        pdf_path = self._get_path_to_pdf_from(page.file.dest_path)
        modified = self.generator.on_post_page(output_content, page, pdf_path)
        end = timer()
        self._total_time += end - start
        return modified

    def on_post_build(self, config: Config) -> None:
        """
        Render the collected pages to a single PDF.

        Args:
            config: The MkDocs config.

        Raises:
            RuntimeError: If errors or warnings occurred in strict mode.

        """
        if not self.enabled or self.generator is None:
            return

        _ = _CaptureWarnings(self._error_counter) if self._error_counter else None

        start = timer()
        self.generator.on_post_build(config, self.config["output_path"])
        end = timer()
        self._total_time += end - start
        self._logger.info(
            "Converting %s articles to PDF took %.1fs",
            self._num_pages,
            self._total_time,
        )

        if self._error_counter:
            errors, warns = self._error_counter.counts()
            if errors > 0 or warns > 0:
                msg = (
                    f"{errors} error(s) and/or {warns} warning(s)"
                    " occurred while generating PDF."
                )
                raise RuntimeError(
                    msg,
                )

    def _get_path_to_pdf_from(self, start: str) -> str:
        dirname, filename = os.path.split(self.config["output_path"])
        if not dirname:
            dirname = "."
        start_dir = os.path.split(start)[0]
        relative = pathlib.PurePosixPath(
            pathlib.Path(os.path.relpath(dirname, start_dir)).as_posix(),
        )
        return str(relative / filename)
