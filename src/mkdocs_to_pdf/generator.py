"""Assemble and render the combined document into a PDF."""

import logging
import pathlib
import re
from datetime import UTC, datetime
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from types import ModuleType
from typing import cast
from urllib.parse import urlparse

from bs4 import BeautifulSoup, PageElement, Tag
from bs4.element import AttributeValueList
from mkdocs.config.base import Config
from mkdocs.structure.nav import Navigation, Section
from mkdocs.structure.pages import Page
from weasyprint import HTML, urls

from .cover import make_cover
from .options import Options
from .preprocessor import get_combined as prep_combined
from .styles import style_for_print
from .themes import generic as generic_theme
from .toc import make_indexes
from .utils.emoji_util import fix_twemoji
from .utils.iframe_util import convert_iframe
from .utils.image_util import fix_image_alignment
from .utils.layout_util import convert_for_two_columns
from .utils.linenums_util import convert_linenums_tables
from .utils.metadata_util import prepend_producer, set_pdf_metadata
from .utils.script_util import collect_page_scripts
from .utils.section import get_section_path
from .utils.soup_util import clone_element, get_attribute
from .utils.tabbed_set_util import wrap_tabbed_set_content


class Generator:
    """Collect pages and render them into a single PDF."""

    def __init__(self, options: Options) -> None:
        """
        Store the options and load the theme handler.

        Args:
            options: The resolved plugin options.

        """
        self._options = options

        self._theme = self._load_theme_handler()
        self._nav: Navigation | None = None
        self._head: Tag | None = None

        self._scraped_scripts: list[Tag] = []
        self._scraped_srcs: set[str] = set()
        self._mixed_script = ""
        self._articles: dict[int, Tag] = {}

        def to_pattern(s: str) -> re.Pattern[str]:
            if s.startswith("^"):
                return re.compile(s)
            return re.compile(f"^{s}")

        self._exclude_page_patterns = list(map(to_pattern, self._options.exclude_pages))
        self._options.logger.debug(
            "Exclude page patterns: %s",
            self._exclude_page_patterns,
        )

    def on_nav(self, nav: Navigation) -> None:
        """
        Store the navigation.

        Args:
            nav: The navigation.

        """
        self._nav = nav
        if nav:
            self._options.logger.debug("theme: %s", self._theme)

    def on_post_page(self, output_content: str, page: Page, pdf_path: str) -> str:
        """
        Collect the page article and inject the PDF link.

        Args:
            output_content: The rendered page HTML.
            page: The page.
            pdf_path: The PDF href to inject.

        Returns:
            The modified page HTML.

        """

        def is_excluded(url: str) -> bool:
            return any(p.match(url) for p in self._exclude_page_patterns)

        if is_excluded(page.url):
            self.logger.info("Page skipped: [%s](%s)", page.title, page.url)
            return output_content
        self.logger.debug(" (post: [%s](%s)", page.title, page.url)

        soup = self._soup_from_content(output_content, page)

        self._remove_empty_tags(soup)

        if self._head is None:
            self._head = soup.find("head")

        article: Tag | None = soup.find("article")
        if article is not None:
            # for 'material'
            article = clone_element(article)
        else:
            # for 'mkdocs' theme
            main = soup.find("div", attrs={"role": "main"})
            if main is not None:
                article = soup.new_tag("article")
                for child in main.contents:
                    article.append(clone_element(child))

        if article is not None:
            for a in article.select("a.headerlink"):
                a.decompose()
            for a in article.select("a.md-content__button"):
                a.decompose()
            self._fix_missing_id_for_h1(article, page)
            self._articles[id(page)] = article
            self._scrap_scripts(soup, page)
        else:
            self.logger.warning("Missing article: [%s](%s)", page.title, page.url)

        return self._options.hook.inject_link(
            output_content,
            pdf_path,
            page,
            self._theme,
        )

    def on_post_build(self, config: Config, output_path: str) -> None:
        """
        Assemble the collected pages and render the PDF.

        Args:
            config: The MkDocs config.
            output_path: The PDF path relative to the site directory.

        Raises:
            ValueError: If `html_path` escapes the site directory.

        """
        if self._head is not None:
            soup = BeautifulSoup("<html><body></body></html>", "html.parser")
            cast("Tag", soup.html).insert(0, self._head)
        else:
            soup = BeautifulSoup(
                "<html><head></head><body></body></html>",
                "html.parser",
            )

        now = datetime.now(UTC)
        set_pdf_metadata(
            soup,
            author=self._options.author,
            description=self._options.description,
            keywords=self._options.keywords,
            created=now,
        )

        def add_stylesheet(stylesheet: str | None) -> None:
            if stylesheet is not None:
                style_tag = soup.new_tag("style")
                style_tag.string = stylesheet
                cast("Tag", soup.head).append(style_tag)

        add_stylesheet(style_for_print(self._options))
        add_stylesheet(self._theme.get_stylesheet(self._options.debug_html))

        for page in self._nav or []:
            content = self._get_content(soup, page)
            if content is not None:
                cast("Tag", soup.body).append(content)

        make_indexes(soup, self._options)
        make_cover(soup, self._options)

        wrap_tabbed_set_content(soup, self._options.logger)
        convert_linenums_tables(soup, self._options.logger)
        fix_image_alignment(soup, self._options.logger)
        convert_iframe(soup, self._options.convert_iframe, self._options.logger)
        convert_for_two_columns(
            soup,
            self._options.two_columns_level,
            self._options.logger,
        )
        self._normalize_link_anchors(soup)

        site_dir = pathlib.Path(config["site_dir"])

        html_string = (
            str(soup) if self._options.relaxed_js else self._render_js(soup, site_dir)
        )

        html_string = self._options.hook.pre_pdf_render(html_string)

        if self._options.debug_html:
            print(f"{html_string}")  # ruff: ignore[print]

        if self._options.html_path:
            abs_html_path = (site_dir / self._options.html_path).resolve()
            site_dir_abs = site_dir.resolve()
            if not abs_html_path.is_relative_to(site_dir_abs):
                msg = (
                    f'html_path "{self._options.html_path}" escapes '
                    f'site_dir "{site_dir_abs}"'
                )
                raise ValueError(
                    msg,
                )
            abs_html_path.parent.mkdir(parents=True, exist_ok=True)
            abs_html_path.write_text(html_string, encoding="utf-8")
            self.logger.info('Output HTML to "%s".', abs_html_path)

        self.logger.info("Rendering for PDF.")

        abs_pdf_path = site_dir / output_path
        abs_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info('Output a PDF to "%s".', abs_pdf_path)

        if self._options.relaxed_js:
            self._options.relaxed_js.write_pdf(html_string, str(abs_pdf_path))
        else:
            html = HTML(string=html_string)
            render = html.render()
            render.write_pdf(str(abs_pdf_path), finisher=prepend_producer)

    @staticmethod
    def _remove_empty_tags(soup: BeautifulSoup) -> None:
        def is_blank(el: Tag) -> bool:
            return not (len(el.get_text(strip=True)) != 0 or el.find(["img", "svg"]))

        includes = {"article", "p"}
        while True:
            hit = False
            for x in soup.find_all():
                if x.name in includes and is_blank(x):
                    x.extract()
                    hit = True
            if not hit:
                break

    @staticmethod
    def _page_path_for_id(page: Page | Section) -> str:
        """Normalize to directory URLs style."""
        path = get_section_path(page) if isinstance(page, Section) else page.url

        path = "." if not path or path == "index.html" else path
        if path.endswith("index.html"):
            path = re.sub(r"index\.html$", "", path)
        elif path.endswith(".html"):
            path = re.sub(r"\.html$", "/", path)
        return path

    @staticmethod
    def _soup_from_content(content: str, page: Page) -> BeautifulSoup:
        soup = BeautifulSoup(content, "html.parser")

        dest = pathlib.Path(page.file.abs_dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        filename = pathlib.Path(page.file.src_path).stem
        base_url = urls.path2url(str(dest.parent / filename))

        return prep_combined(soup, base_url, page.file.url)

    def _get_content(  # ruff: ignore[complex-structure]
        self,
        soup: BeautifulSoup,
        page: Page | Section,
    ) -> PageElement | None:
        def shift_heading(elem: Tag, page: Page | Section) -> Tag:
            for i in range(7, 0, -1):
                while True:
                    h = elem.find(f"h{i}")
                    if not h:
                        break
                    h.name = f"h{i + 1}"

            page_path = self._page_path_for_id(page)
            h1 = soup.new_tag("h1", id=f"{page_path}")
            h1.append(str(page.title))
            elem.insert(0, h1)
            return elem

        def cleanup_class(
            classes: AttributeValueList | str | None,
        ) -> AttributeValueList | str | None:
            if isinstance(classes, AttributeValueList) and classes:
                excludes = {"md-content__inner"}
                return AttributeValueList(c for c in classes if c not in excludes)
            return classes

        article = self._articles.get(id(page))
        if article is not None:
            page_path = self._page_path_for_id(page)
            article["id"] = f"{page_path}:"  # anchor for each page.
            article["data-url"] = f"/{page_path}"
            return article

        if isinstance(page, Section) and page.children:
            new_article = soup.new_tag("article")
            found = False
            for child in page.children:
                if not isinstance(child, (Page, Section)):
                    continue
                content = self._get_content(soup, child)
                if content:
                    new_article.append(content)
                    found = True

            if not found:
                return None

            child_classes: AttributeValueList | None = None
            for child_article in new_article.find_all("article"):
                child_article.name = "section"
                classes = child_article.get("class")
                if isinstance(classes, AttributeValueList) and child_classes is None:
                    child_classes = classes
                cleaned = cleanup_class(classes)
                if cleaned is not None:
                    child_article["class"] = cleaned

            page_path = self._page_path_for_id(page)
            new_article["id"] = f"{page_path}:"  # anchor for each page.
            new_article["data-url"] = f"/{page_path}"
            if child_classes is not None:
                new_article["class"] = child_classes

            if self._options.heading_shift:
                return shift_heading(new_article, page)
            return new_article

        return None

    def _fix_missing_id_for_h1(self, content: Tag, page: Page) -> None:
        h1 = content.find("h1")
        if h1 and not h1.get("id"):
            h1["id"] = self._page_path_for_id(page)

    @property
    def logger(self) -> logging.Logger:
        """The logger."""
        return self._options.logger

    def _load_theme_handler(self) -> ModuleType:
        theme = self._options.theme_name
        custom_handler_path = self._options.theme_handler_path
        module_name = "." + (theme or "generic").replace("-", "_")
        if custom_handler_path:
            try:
                custom_path = str(pathlib.Path.cwd() / custom_handler_path)
                spec = spec_from_file_location(module_name, custom_path)
                if spec is not None and spec.loader is not None:
                    mod = module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    return mod
            except FileNotFoundError:
                self.logger.exception(
                    "Could not load theme handler %s from custom directory %r",
                    theme,
                    custom_handler_path,
                )

        try:
            return import_module(module_name, "mkdocs_to_pdf.themes")
        except ImportError:
            self.logger.exception("Could not load theme handler %s", theme)
            return generic_theme

    def _normalize_link_anchors(  # ruff: ignore[complex-structure]
        self,
        soup: BeautifulSoup,
    ) -> None:
        def normalize_anchor_chars(anchor: str) -> str:
            # Should PDF hashtag links contain percent encoding?
            # https://discussions.apple.com/thread/251041261
            return anchor.replace("%25", "-").replace("%", "-")

        for anchor in soup.find_all(id=True):
            anchor["id"] = normalize_anchor_chars(get_attribute(anchor, "id"))
        for link in soup.find_all("a", href=True):
            link["href"] = normalize_anchor_chars(get_attribute(link, "href"))

        if not (
            self._options.debug_html
            or self._options.show_anchors
            or self._options.strict
            or self._options.verbose
        ):
            return

        anchors = {f"#{el['id']}" for el in soup.find_all(id=True)}

        if not (self._options.strict or self._options.debug_html):
            self.logger.info("Anchor points provided:")
            for anchor in sorted(anchors):
                self.logger.info("| %s", anchor)
            return

        missing: set[str] = set()
        for el in soup.find_all("a", href=True):
            href = get_attribute(el, "href")
            target_url = urlparse(href)

            if target_url.scheme or target_url.netloc:
                continue
            if href in anchors:
                continue

            missing.add(href)

        if missing:
            self.logger.error("Missing %s link(s):", len(missing))
            for link in sorted(missing):
                self.logger.warning("  | %s", link)
            if (
                self._options.show_anchors
                or self._options.verbose
                or self._options.debug_html
            ):
                self.logger.info("  | --- found anchors:")
                for anchor in sorted(anchors):
                    self.logger.info("  | %s", anchor)

    def _render_js(self, soup: BeautifulSoup, site_dir: pathlib.Path) -> str:
        if not self._options.js_renderer:
            fix_twemoji(soup, self._options.logger)
            return str(soup)

        soup = self._options.hook.pre_js_render(soup)

        scripts = self._theme.get_script_sources()
        if len(scripts) > 0:
            body = soup.find("body")
            if body:
                for script in self._scraped_scripts:
                    body.append(script)
                if len(self._mixed_script) > 0:
                    tag = soup.new_tag("script")
                    tag.append(self._mixed_script)
                    body.append(tag)
                for src in scripts:
                    body.append(soup.new_tag("script", src=f"file://{src}"))

        return self._options.js_renderer.render(str(soup), site_dir)

    def _scrap_scripts(self, soup: BeautifulSoup, page: Page) -> None:
        if not self._options.js_renderer:
            return

        # CAUTION:
        # It does not consider cases where the tag contains both src and text.

        base_dir = pathlib.Path(page.file.abs_dest_path).parent
        scripts, inline = collect_page_scripts(soup, base_dir)

        for script in scripts:
            src = get_attribute(script, "src")
            if src in self._scraped_srcs:
                continue
            self._scraped_srcs.add(src)
            self._scraped_scripts.append(script)

        if inline:
            self._mixed_script += ";" + inline
