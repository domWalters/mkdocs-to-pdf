"""Convert iframes into printable anchors."""

from logging import Logger

from bs4 import BeautifulSoup

from .soup_util import get_attribute


def convert_iframe(
    soup: BeautifulSoup,
    entries: list[dict[str, str]],
    logger: Logger | None = None,
) -> None:
    """
    Replace a matching iframe with an anchor pointing at its source.

    Example:
        ``<iframe src="SRC"/>`` becomes
        ``<a class="converted-iframe" href="SRC" target="_blank">...</a>``.

    Args:
        soup: DOM object of the page.
        entries: The configured iframe conversions.
        logger: Optional logger.

    """
    if len(entries) < 1:
        return

    if logger:
        logger.info("Converting <iframe> to poster image(if available).")

    for iframe in soup.find_all("iframe", src=True):
        for entry in entries:
            if iframe["src"] != entry.get("src"):
                continue

            a = soup.new_tag(
                "a",
                href=get_attribute(iframe, "src"),
                target="_blank",
                attrs={"class": "converted-iframe"},
            )
            img_src = entry.get("img")
            if img_src:
                a.append(soup.new_tag("img", src=img_src))
            text = entry.get("text")
            if text:
                span = soup.new_tag("span")
                span.string = text
                a.append(span)

            # copy attributes
            for key, val in iframe.attrs.items():
                if key == "style":
                    a[key] = val

            iframe.replace_with(a)
