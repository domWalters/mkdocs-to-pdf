"""Helpers for rewriting links and asset references."""

import pathlib

from bs4 import BeautifulSoup
from weasyprint import urls

from mkdocs_to_pdf.utils.soup_util import get_attribute


def is_doc(href: str) -> bool:
    """
    Return whether an href points to a relative HTML document.

    Args:
        href: The href to inspect.

    Returns:
        True if the href is a relative HTML document.

    """
    path = pathlib.PurePosixPath(href)
    htmlfile = path.suffix.startswith(".html")

    absurl = urls.url_is_absolute(href)
    abspath = path.is_absolute()
    return not (absurl or abspath or not htmlfile)


def rel_pdf_href(href: str) -> str:
    """
    Rewrite a document href to its standalone PDF filename.

    Args:
        href: The href to rewrite.

    Returns:
        The rewritten href.

    """
    internal = href.startswith("#")
    if not is_doc(href) or internal:
        return href

    return str(urls.iri_to_uri(str(pathlib.PurePosixPath(href).with_suffix(".pdf"))))


def abs_asset_href(href: str, base_url: str) -> str:
    """
    Resolve a relative asset href against a base URL.

    Args:
        href: The asset href.
        base_url: The base URL.

    Returns:
        The absolute asset href.

    """
    if urls.url_is_absolute(href) or pathlib.PurePosixPath(href).is_absolute():
        return href

    return str(urls.iri_to_uri(urls.urljoin(base_url, href)))


def replace_asset_hrefs(soup: BeautifulSoup, base_url: str) -> BeautifulSoup:
    """
    Make all relative asset links absolute.

    Args:
        soup: DOM object of the page.
        base_url: The base URL used to resolve assets.

    Returns:
        The transformed document.

    """
    for link in soup.find_all("link", href=True):
        link["href"] = abs_asset_href(get_attribute(link, "href"), base_url)

    for asset in soup.find_all(src=True):
        asset["src"] = abs_asset_href(get_attribute(asset, "src"), base_url)

    return soup


def get_body_id(url: str) -> str:
    """
    Derive the body id from a page URL.

    Args:
        url: The page URL.

    Returns:
        The body id.

    """
    path = pathlib.PurePosixPath(url)
    section = str(path.with_suffix("")) if path.suffix else url
    return f"{section}:"
