"""Generic theme handler."""

from logging import Logger

from bs4 import BeautifulSoup
from mkdocs.structure.pages import Page


def get_stylesheet(
    _debug_html: bool,  # ruff: ignore[boolean-type-hint-positional-argument]
) -> str | None:
    """
    Return the theme stylesheet, if any.

    Args:
        _debug_html: Whether debug HTML output is enabled.

    Returns:
        The stylesheet, or None.

    """
    return None


def get_script_sources() -> list[str]:
    """
    Return the theme script sources.

    Returns:
        The script sources.

    """
    return []


def inject_link(html: str, href: str, _page: Page, _logger: Logger) -> str:
    """
    Inject the PDF download link into the page head.

    Args:
        html: The rendered page HTML.
        href: The PDF href.
        _page: The page being rendered.
        _logger: The logger.

    Returns:
        The modified HTML.

    """
    soup = BeautifulSoup(html, "html.parser")
    if soup.head:
        link = soup.new_tag(
            "link",
            href=href,
            rel="alternate",
            title="PDF",
            type="application/pdf",
        )
        soup.head.append(link)
        return str(soup)

    return html
