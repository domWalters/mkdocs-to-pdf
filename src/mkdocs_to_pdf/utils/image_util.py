"""Image attribute fix-ups for print output."""

import pathlib
from logging import Logger
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, NavigableString, PageElement, Tag

from .soup_util import get_attribute

# Suffixes whose image links are dropped in favour of the image itself.
_IMAGE_SUFFIXES = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".avif", ".ico"},
)


def unwrap_image_links(soup: BeautifulSoup, logger: Logger | None = None) -> None:
    """
    Unwrap anchors that only wrap a single image asset.

    Lightbox plugins such as ``mkdocs-glightbox`` wrap every image in an
    ``<a>`` whose href points back at the image. A zoom link is meaningless in
    print and its relative href cannot be resolved, so the anchor is removed
    while the image is kept.

    Args:
        soup: DOM object of the page.
        logger: Optional logger.

    """
    for anchor in soup.find_all("a", href=True):
        href = get_attribute(anchor, "href")
        suffix = pathlib.PurePosixPath(urlsplit(href).path).suffix.lower()
        if suffix not in _IMAGE_SUFFIXES:
            continue

        children = [child for child in anchor.contents if not _is_blank(child)]
        if len(children) != 1:
            continue
        child = children[0]
        if not isinstance(child, Tag) or child.name != "img":
            continue

        if logger:
            logger.debug("Unwrapping image link: %s", anchor)
        anchor.unwrap()


def _is_blank(node: PageElement) -> bool:
    return isinstance(node, NavigableString) and not str(node).strip()


def fix_image_alignment(  # ruff: ignore[complex-structure]
    soup: BeautifulSoup,
    logger: Logger | None = None,
) -> None:
    """
    Fold ``align``/``width``/``height`` image attributes into inline styles.

    Args:
        soup: DOM object of the page.
        logger: Optional logger.

    """
    if logger:
        logger.info("Converting <img> alignment(workaround).")

    for img in soup.select("img"):
        try:  # ruff: ignore[too-many-statements-in-try-clause]
            classes = img.get("class")
            if classes and "twemoji" in classes:
                continue

            styles = _parse_style(get_attribute(img, "style"))

            if logger:
                logger.debug("  | %s", img)
            if img.has_attr("align"):
                if img["align"] == "left":
                    styles["float"] = "left"
                    styles["padding-right"] = "1rem"
                    styles["padding-bottom"] = "0.5rem"
                    img.attrs.pop("align")
                elif img["align"] == "right":
                    styles["float"] = "right"
                    styles["padding-left"] = "1rem"
                    styles["padding-bottom"] = "0.5rem"
                    img.attrs.pop("align")

            if img.has_attr("width"):
                styles["width"] = _convert_dimension(get_attribute(img, "width"))
                img.attrs.pop("width")
            if img.has_attr("height"):
                styles["height"] = _convert_dimension(get_attribute(img, "height"))
                img.attrs.pop("height")

            # Remove any trailing commas from style values
            img["style"] = " ".join(f"{k}: {v.rstrip(',')};" for k, v in styles.items())
        except Exception as e:  # ruff: ignore[blind-except]
            if logger:
                logger.warning("Failed to convert img align: %s", e)


def images_size_to_half_in(section: Tag) -> None:
    """
    Halve image dimensions and padding inside a section.

    Args:
        section: The section to process.

    """

    def _split(s: str) -> tuple[str, str]:
        index = next((i for i, c in enumerate(s) if not c.isdigit()), len(s))
        return (s[:index], s[index:].lstrip())

    for img in section.find_all("img"):
        if not img.has_attr("style"):
            continue
        styles = _parse_style(get_attribute(img, "style"))
        if not len(styles):
            continue

        for key in ["width", "height", "padding-left", "padding-right"]:
            if key in styles:
                (dim, u) = _split(styles[key])
                styles[key] = str(int(dim) / 2) + u
        img["style"] = " ".join(f"{k}: {v};" for k, v in styles.items())


def _parse_style(style_string: str) -> dict[str, str]:
    styles = {}
    if style_string:
        for attr in style_string.split(";"):
            if not len(attr):
                continue
            val = attr.split(":", 2)
            styles[val[0].strip()] = val[1].strip()
    return styles


def _convert_dimension(dim_str: str) -> str:
    if dim_str.isdecimal():
        return dim_str + "px"
    return dim_str
