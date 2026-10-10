"""HTML string helpers."""

from bs4 import BeautifulSoup


def html_to_text(value: str) -> str:
    """
    Convert an HTML fragment to its plain-text content.

    Useful where markup cannot be rendered, such as CSS `string-set` values
    used in page margin boxes.

    Args:
        value: The HTML fragment.

    Returns:
        The text content, with any tags removed.

    """
    return BeautifulSoup(value, "html.parser").get_text()
