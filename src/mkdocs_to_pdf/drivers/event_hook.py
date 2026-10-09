"""Load an optional user-provided PDF rendering event hook module."""

import importlib
import pathlib
import sys
from collections.abc import Callable
from logging import Logger
from types import ModuleType
from typing import cast

from bs4 import BeautifulSoup
from mkdocs.config.base import Config
from mkdocs.livereload import LiveReloadServer
from mkdocs.structure.pages import Page


class EventHookHandler:
    """Event hook on PDF generate sequence."""

    _module_name = "pdf_event_hook"

    @classmethod
    def on_serve(
        cls,
        server: LiveReloadServer,
        builder: Callable[[], None],
        logger: Logger,
    ) -> None:
        """
        Watch the event hook module while serving, if present.

        Args:
            server: The live-reload server.
            builder: The rebuild callback.
            logger: The logger.

        """
        path = f"./{cls._module_name}.py"
        if pathlib.Path(path).is_file():
            logger.warning("watch %s", path)
            server.watch(path, builder)  # type: ignore[arg-type]  # ty: ignore[invalid-argument-type]

    def __init__(self, options: object, config: Config, logger: Logger) -> None:
        """
        Store the options/config and load the hook module if present.

        Args:
            options: The plugin options.
            config: The MkDocs config.
            logger: The logger.

        """
        self._options = options
        self._config = config
        self._logger = logger.getChild("HOOK")

        self._module = self._load_module()

    def _load_module(self) -> ModuleType | None:
        cwd = str(pathlib.Path.cwd())
        if cwd not in sys.path:  # pragma: no cover
            sys.path.append(cwd)

        try:
            module = __import__(self._module_name)
            importlib.reload(module)
            self._logger.info("Found PDF rendering event hook module.")
        except ModuleNotFoundError:
            module = None

        return module

    def inject_link(
        self,
        output_content: str,
        pdf_path: str,
        page: Page,
        theme_handler: ModuleType,
    ) -> str:
        """
        Inject the PDF download link, preferring the hook module.

        Args:
            output_content: The rendered page HTML.
            pdf_path: The PDF href.
            page: The page being rendered.
            theme_handler: The fallback theme handler.

        Returns:
            The modified HTML.

        """
        if self._module and hasattr(self._module, "inject_link"):
            return str(
                self._module.inject_link(
                    output_content,
                    pdf_path,
                    page,
                    self._logger,
                ),
            )
        return str(
            theme_handler.inject_link(output_content, pdf_path, page, self._logger),
        )

    def pre_js_render(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Run the hook's `pre_js_render` step, if present.

        Args:
            soup: The document.

        Returns:
            The (possibly modified) document.

        """
        if self._module and hasattr(self._module, "pre_js_render"):
            return cast("BeautifulSoup", self._module.pre_js_render(soup, self._logger))
        return soup

    def pre_pdf_render(self, html_string: str) -> str:
        """
        Run the hook's `pre_pdf_render` step, if present.

        Args:
            html_string: The document HTML.

        Returns:
            The (possibly modified) HTML.

        """
        if self._module and hasattr(self._module, "pre_pdf_render"):
            soup = BeautifulSoup(html_string, "html.parser")
            soup = self._module.pre_pdf_render(soup, self._logger)
            return str(soup)
        return html_string
