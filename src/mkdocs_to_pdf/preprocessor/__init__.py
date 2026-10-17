"""Assemble the individual pages into a single document."""

import pathlib
from typing import cast

from bs4 import BeautifulSoup, Tag
from weasyprint import urls

from mkdocs_to_pdf.utils.soup_util import get_attribute

from .links.transform import is_asset_href, transform_href, transform_id
from .links.util import (
    abs_asset_href,
    get_body_id,
    rel_pdf_href,
    replace_asset_hrefs,
)


def get_combined(  # ruff: ignore[non-empty-init-module]
    soup: BeautifulSoup,
    base_url: str,
    rel_url: str,
) -> BeautifulSoup:
    """
    Rewrite relative hrefs pointing to other HTML docs into PDF hrefs.

    Args:
        soup: DOM object of the page.
        base_url: The base URL used to resolve assets.
        rel_url: The page URL relative to the site root.

    Returns:
        The transformed document.

    """
    for element in soup.find_all(id=True):
        element["id"] = transform_id(get_attribute(element, "id"), rel_url)

    for a in soup.find_all("a", href=True):
        href = get_attribute(a, "href")
        if urls.url_is_absolute(href) or pathlib.PurePosixPath(href).is_absolute():
            continue

        if is_asset_href(href):
            a["href"] = abs_asset_href(href, base_url)
            continue

        a["href"] = transform_href(href, rel_url)

    cast("Tag", soup.body)["id"] = get_body_id(rel_url)
    return replace_asset_hrefs(soup, base_url)


def get_separate(  # ruff: ignore[non-empty-init-module]
    soup: BeautifulSoup,
    base_url: str,
) -> BeautifulSoup:
    """
    Rewrite document hrefs to their standalone PDF counterparts.

    Args:
        soup: DOM object of the page.
        base_url: The base URL used to resolve assets.

    Returns:
        The transformed document.

    """
    for a in soup.find_all("a", href=True):
        a["href"] = rel_pdf_href(get_attribute(a, "href"))

    return replace_asset_hrefs(soup, base_url)
