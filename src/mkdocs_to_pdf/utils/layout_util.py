"""Lay content out across two columns for print."""

import itertools
from logging import Logger

from bs4 import BeautifulSoup, PageElement, Tag

from .image_util import images_size_to_half_in


def convert_for_two_columns(
    soup: BeautifulSoup,
    level: int,
    logger: Logger | None = None,
) -> None:
    """
    Wrap level-three sections into two-column blocks.

    Args:
        soup: DOM object of the page.
        level: The configured `two_columns_level` (only 3 is supported).
        logger: Optional logger.

    """
    if level == 0:
        return
    # ruff: ignore[magic-value-comparison]
    if level != 3:
        if logger:
            logger.warning("`two_columns_level` is only support `3` yet.")
        return

    if logger:
        logger.info("Converting for two-column layout(heading level 3).")

    ignored: list[PageElement] = []
    for el in soup.find_all("h3"):
        if el in ignored:
            continue
        els = list(
            itertools.takewhile(
                lambda x: not (isinstance(x, Tag) and x.name in {"h1", "h2"}),
                el.next_siblings,
            ),
        )
        section = soup.new_tag("section", attrs={"class": "md-typeset two-columns"})
        el.wrap(section)
        for tag in els:
            section.append(tag)
            if isinstance(tag, Tag) and tag.name == "h3":
                ignored.append(tag)
        images_size_to_half_in(section)
