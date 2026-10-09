"""Twemoji SVG fix-ups for print output."""

import re
from base64 import b64encode
from logging import Logger

from bs4 import BeautifulSoup, Tag

from .soup_util import get_attribute


def fix_twemoji(soup: BeautifulSoup, logger: Logger | None = None) -> None:
    """
    Replace SVG twemoji with base64-encoded images.

    Works around SVGs not rendering in older WeasyPrint versions, for
    Material for MkDocs v4.5.0 and later.

    See https://github.com/squidfunk/mkdocs-material/pull/1330.

    Args:
        soup: DOM object of the page.
        logger: Optional logger.

    """

    def fix_size(svg: Tag) -> None:
        """Set the SVG size and fill from its viewBox."""
        view_box = _parse_view_box(get_attribute(svg, "viewbox"))
        width, height = (view_box[2] - view_box[0], view_box[3] - view_box[1])
        svg["width"] = str(int(width))
        svg["height"] = str(int(height))
        svg["style"] = "fill: currentColor;"

    if logger:
        logger.debug("Converting emoji SVG to img(workaround).")

    for svg in soup.select(".twemoji svg"):
        try:  # ruff: ignore[too-many-statements-in-try-clause]
            fix_size(svg)
            encoded = b64encode(str(svg).encode("utf-8")).decode("ascii")
            data = "data:image/svg+xml;charset=utf-8;base64," + encoded
            img = soup.new_tag("img", src=data, attrs={"class": "converted-twemoji"})
            svg.replace_with(img)

            if logger:
                logger.debug("> svg: %s", svg)
                logger.debug("< img: %s", img)

        except Exception as e:  # ruff: ignore[blind-except]
            if logger:
                logger.warning("Failed to convert SVG: %s", e)


def _parse_view_box(view_box_string: str) -> tuple[float, float, float, float]:
    """
    Parse an SVG viewBox into its four numeric components.

    Args:
        view_box_string: The viewBox string.

    Returns:
        The four components.

    Raises:
        ValueError: If the viewBox cannot be parsed.

    """
    p = re.compile(r"(-?[\d\.]+) (-?[\d\.]+) (-?[\d\.]+) (-?[\d\.]+)")
    m = p.match(view_box_string)
    if m is None:
        msg = f"Invalid viewBox: {view_box_string!r}"
        raise ValueError(msg)
    return (
        float(m.group(1)),
        float(m.group(2)),
        float(m.group(3)),
        float(m.group(4)),
    )
