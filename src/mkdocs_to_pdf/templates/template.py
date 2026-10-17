"""Jinja2 template loading and keyword assembly."""

import contextlib
import html
import pathlib
from collections.abc import Callable
from datetime import datetime
from pprint import pformat
from typing import TYPE_CHECKING, cast

import jinja2
from mkdocs.config.base import Config

from .filters.datetime import strftime, strptime
from .filters.url import URLFilter

if TYPE_CHECKING:
    from mkdocs_to_pdf.options import Options

Barcode: type | None = None
with contextlib.suppress(ModuleNotFoundError):
    from .filters.barcode import Barcode

QRCode: type | None = None
with contextlib.suppress(ModuleNotFoundError):
    from .filters.qrcode import QRCode


def _missing_filter(name: str, package: str) -> Callable[..., str]:
    """Return a filter stub that fails with an actionable message when used."""

    def _unavailable(*_args: object, **_kwargs: object) -> str:
        msg = (
            f"The `{name}` template filter requires the `{package}` package, "
            f"which is not installed."
        )
        raise RuntimeError(msg)

    return _unavailable


Keyword = object
KeywordsList = list[Keyword]
KeywordsMap = dict[str, Keyword]


class Template:
    """Pickups key-value from `mkdocs.yml`."""

    __KEYS = frozenset(
        {
            "author",
            "copyright",
            "cover_title",
            "cover_subtitle",
            "cover_logo",
            "back_cover_qrcode",
            "back_cover_qr_url",
            "back_cover_barcode",
            "back_cover_barcode_value",
            "back_cover_barcode_kind",
            "site_url",
            "repo_url",
        },
    )

    def __init__(self, options: "Options", config: Config) -> None:
        """
        Store the plugin options and MkDocs config.

        Args:
            options: The plugin options.
            config: The MkDocs config.

        """
        self._options = options
        self._config = config

        self._keywords: KeywordsMap | None = None
        self._jinja_env: jinja2.Environment | None = None

    @property
    def _env(self) -> jinja2.Environment:
        def generate() -> jinja2.Environment:
            base_path = pathlib.Path(__file__).resolve().parent
            template_paths = [str(base_path)]

            if pathlib.Path(self._options.custom_template_path).exists():
                template_paths.append(self._options.custom_template_path)

            file_loader = jinja2.FileSystemLoader(template_paths)
            logging_undefined = jinja2.make_logging_undefined(
                logger=self._options.logger,
                base=jinja2.Undefined,
            )
            env = jinja2.Environment(
                autoescape=True,
                loader=file_loader,
                lstrip_blocks=True,
                trim_blocks=True,
                undefined=logging_undefined,
            )

            env.filters["strptime"] = strptime
            env.filters["strftime"] = strftime

            env.filters["to_url"] = URLFilter(self._options, self._config)

            env.filters["barcode"] = (
                Barcode(self._options, self._config)
                if Barcode is not None
                else _missing_filter("barcode", "python-barcode")
            )
            env.filters["qrcode"] = (
                QRCode(self._options, self._config)
                if QRCode is not None
                else _missing_filter("qrcode", "qrcode")
            )

            return env

        if not self._jinja_env:
            self._jinja_env = generate()
        return self._jinja_env

    @property
    def qrcode_available(self) -> bool:
        """Whether the `qrcode` package (and its filter) is available."""
        return QRCode is not None

    @property
    def barcode_available(self) -> bool:
        """Whether the `python-barcode` package (and its filter) is available."""
        return Barcode is not None

    @property
    def keywords(self) -> KeywordsMap:  # ruff: ignore[complex-structure]
        """Keywords to pass when rendering the template."""

        def unescape_html_in_list(values: KeywordsList) -> KeywordsList:
            new_values: KeywordsList = []
            for v in values:
                if isinstance(v, str):
                    new_values.append(html.unescape(v))
                elif isinstance(v, list):
                    new_values.append(unescape_html_in_list(v))
                elif isinstance(v, dict):
                    unescape_html(v)
                    new_values.append(v)
                else:
                    new_values.append(v)
            return new_values

        def unescape_html(variables: KeywordsMap) -> None:
            for k, v in variables.items():
                if isinstance(v, str):
                    variables[k] = html.unescape(v)
                elif isinstance(v, list):
                    variables[k] = unescape_html_in_list(v)
                elif isinstance(v, dict):
                    unescape_html(v)
                else:
                    variables[k] = v

        def build_keywords() -> KeywordsMap:
            keywords = cast("KeywordsMap", self._config["extra"])

            for key in self.__KEYS:
                if hasattr(self._options, key):
                    keywords[key] = getattr(self._options, key)
                elif hasattr(self._options, f"_{key}"):
                    keywords[key] = getattr(self._options, f"_{key}")
                elif key in self._config:
                    keywords[key] = self._config[key]

            unescape_html(keywords)

            now = datetime.now()  # ruff: ignore[call-datetime-now-without-tzinfo]
            keywords["now"] = now

            if self._options.verbose or self._options.debug_html:
                self._options.logger.info("Template variables:")
                for line in pformat(keywords).split("\n"):
                    self._options.logger.info("  %s", line)

            return keywords

        if self._keywords is None:
            self._keywords = build_keywords()

        return self._keywords

    def render_string(self, source: str) -> str:
        """
        Render a template given as a string with the plugin keywords.

        Args:
            source: The template source.

        Returns:
            The rendered string.

        """
        template = self._env.from_string(source)
        return template.render(self.keywords)

    def select(
        self,
        names: list[str],
        parent: str | None = None,
        jinja_globals: dict[str, object] | None = None,
    ) -> jinja2.Template:
        """Find and load a template by names of given."""
        real_names: list[str] = []
        for name in names:
            real_names.extend(
                name + ext for ext in [".html.j2", ".html.jinja2", ".html", ".htm"]
            )

        return self._env.select_template(
            real_names,
            parent=parent,
            globals=jinja_globals,
        )
