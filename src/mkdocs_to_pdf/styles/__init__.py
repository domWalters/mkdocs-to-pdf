"""Compile the stylesheets used for print rendering."""

import html
import pathlib

import sass

from mkdocs_to_pdf.options import Options
from mkdocs_to_pdf.utils.html_util import html_to_text


def _css_escape(text: str) -> str:  # ruff: ignore[non-empty-init-module]
    """
    Escape a value for interpolation into a CSS string.

    See https://developer.mozilla.org/en-US/docs/Web/CSS/string.
    """
    if not text:
        return ""

    text = html.unescape(text)

    return text.replace("'", "\\27")


def style_for_print(options: Options) -> str:  # ruff: ignore[non-empty-init-module]
    """
    Compile the SCSS stylesheets used to render the PDF.

    Args:
        options: The project options.

    Returns:
        The compiled CSS.

    """
    scss = f"""
    :root {{
        string-set: author '{_css_escape(options.author)}',
            copyright '{_css_escape(html_to_text(options.copyright))}',
            title '{_css_escape(options.cover_title)}',
            subtitle '{_css_escape(options.cover_subtitle)}';
    }}
    h1, h2, h3 {{
        string-set: chapter content();
    }}
    """
    css = str(sass.compile(string=scss))

    base_path = pathlib.Path(__file__).resolve().parent

    filename = str(base_path / "report-print.scss")
    css += str(sass.compile(filename=filename))

    if options.cover or options.back_cover:
        filename = str(base_path / "cover.scss")
        css += str(sass.compile(filename=filename))

    custom = pathlib.Path(options.custom_template_path) / "styles.scss"
    if custom.exists():
        source = custom.read_text(encoding="utf-8")
        source = options.template.render_string(source)
        css += str(sass.compile(string=source))

    return css
