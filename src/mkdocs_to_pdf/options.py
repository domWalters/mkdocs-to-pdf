"""Resolve the plugin configuration into runtime options."""

from logging import Logger

from mkdocs.config import config_options
from mkdocs.config.base import Config

from .drivers.event_hook import EventHookHandler
from .drivers.headless_chrome import HeadlessChromeDriver
from .drivers.relaxedjs import RelaxedJSRenderer
from .templates.template import Template


class Options:
    """The resolved plugin options."""

    config_scheme = (
        ("enabled_if_env", config_options.Type(str)),
        ("verbose", config_options.Type(bool, default=False)),
        ("debug_html", config_options.Type(bool, default=False)),
        ("show_anchors", config_options.Type(bool, default=False)),
        ("output_path", config_options.Type(str, default="pdf/document.pdf")),
        ("html_path", config_options.Type(str, default=None)),
        ("theme_handler_path", config_options.Type(str, default=None)),
        ("author", config_options.Type(str, default="")),
        ("copyright", config_options.Type(str, default="")),
        ("cover", config_options.Type(bool, default=True)),
        ("back_cover", config_options.Type(bool, default=False)),
        ("cover_title", config_options.Type(str, default="")),
        ("cover_subtitle", config_options.Type(str, default="")),
        ("cover_logo", config_options.Type(str, default=None)),
        ("custom_template_path", config_options.Type(str, default="templates")),
        ("toc_title", config_options.Type(str, default="Table of contents")),
        ("heading_shift", config_options.Type(bool, default=True)),
        ("toc_level", config_options.Type(int, default=2)),
        ("ordered_chapter_level", config_options.Type(int, default=3)),
        ("excludes_children", config_options.Type(list, default=[])),
        ("exclude_pages", config_options.Type(list, default=[])),
        ("convert_iframe", config_options.Type(list, default=[])),
        ("two_columns_level", config_options.Type(int, default=0)),
        ("render_js", config_options.Type(bool, default=False)),
        ("headless_chrome_path", config_options.Type(str, default="chromium-browser")),
        ("relaxedjs_path", config_options.Type(str, default=None)),
    )

    def __init__(
        self,
        local_config: Config,
        config: Config,
        logger: Logger,
    ) -> None:
        """
        Resolve the options from the plugin and MkDocs configs.

        Args:
            local_config: The plugin configuration.
            config: The MkDocs configuration.
            logger: The logger.

        """
        self.strict = bool(config["strict"])

        self.verbose = local_config["verbose"]
        self.debug_html = local_config["debug_html"]
        self.show_anchors = local_config["show_anchors"]

        self.output_path = local_config["output_path"]
        self.html_path = local_config.get("html_path", None)
        self.theme_handler_path = local_config.get("theme_handler_path", None)

        # Author and Copyright
        self._author = str(local_config["author"] or config["site_author"] or "")
        self._copyright = str(local_config["copyright"] or config["copyright"] or "")

        # Cover
        self.cover = local_config["cover"]
        self.back_cover = local_config["back_cover"]
        self._cover_title = ""
        self._cover_subtitle = ""
        self._cover_logo = ""
        if self.cover or self.back_cover:
            self._cover_title = str(local_config["cover_title"] or config["site_name"])
            self._cover_subtitle = str(local_config["cover_subtitle"])
            self._cover_logo = str(local_config["cover_logo"] or "")

        # path to custom template 'cover.html' and custom scss 'styles.scss'
        self.custom_template_path = local_config["custom_template_path"]

        # TOC and Chapter heading
        self.toc_title = local_config["toc_title"]
        self.heading_shift = local_config["heading_shift"]
        self.toc_level = local_config["toc_level"]
        self.ordered_chapter_level = local_config["ordered_chapter_level"]
        self.excludes_children = local_config["excludes_children"]

        # Page
        self.exclude_pages = local_config["exclude_pages"]
        self.convert_iframe = local_config["convert_iframe"]

        self.two_columns_level = local_config["two_columns_level"]

        # ...etc.
        self.js_renderer = None
        self.relaxed_js = None
        if local_config["render_js"]:
            if local_config["headless_chrome_path"]:
                self.js_renderer = HeadlessChromeDriver.setup(
                    local_config["headless_chrome_path"],
                    logger,
                )
            if local_config["relaxedjs_path"]:
                self.relaxed_js = RelaxedJSRenderer.setup(
                    local_config["relaxedjs_path"],
                    logger,
                )

        # Theming
        self.theme_name = config["theme"].name
        self.theme_handler_path = local_config.get("theme_handler_path", None)
        if not self.theme_handler_path:
            # Read from global config only if plugin config is not set
            self.theme_handler_path = config.get("theme_handler_path", None)

        # Template handler(Jinja2 wrapper)
        self._template = Template(self, config)

        self._hook = EventHookHandler(self, config, logger)

        # for system
        self._logger = logger

    @property
    def author(self) -> str:
        """The document author."""
        return self._author

    @property
    def copyright(self) -> str:
        """The document copyright statement."""
        return self._copyright

    @property
    def cover_title(self) -> str:
        """The cover page title."""
        return self._cover_title

    @property
    def cover_subtitle(self) -> str:
        """The cover page subtitle."""
        return self._cover_subtitle

    @property
    def cover_logo(self) -> str:
        """The cover page logo."""
        return self._cover_logo

    @property
    def logger(self) -> Logger:
        """The logger."""
        return self._logger

    @property
    def template(self) -> Template:
        """The template handler."""
        return self._template

    @property
    def hook(self) -> EventHookHandler:
        """The event hook handler."""
        return self._hook
