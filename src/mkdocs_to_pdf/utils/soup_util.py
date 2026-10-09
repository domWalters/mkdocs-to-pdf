"""BeautifulSoup element helpers."""

from copy import copy
from typing import TypeVar

from bs4 import PageElement, Tag

_PageElementT = TypeVar("_PageElementT", bound=PageElement)


def clone_element(el: _PageElementT) -> _PageElementT:
    """
    Clone a BeautifulSoup element, including its children.

    bs4 only permits one element per position in a parse tree, so a copy is
    always a deep copy.

    Args:
        el: The element to clone.

    Returns:
        A deep copy of the element.

    """
    return copy(el)


def get_attribute(tag: Tag, name: str, default: str = "") -> str:
    """
    Return a single-valued attribute as a string.

    BeautifulSoup types every attribute as ``str | AttributeValueList``. The
    attributes read through this helper (``id``, ``href``, ``src``,
    ``style``, ...) are single-valued, so any non-string value falls back to
    ``default``.

    Args:
        tag: The element to read from.
        name: The attribute name.
        default: Value returned when the attribute is absent.

    Returns:
        The attribute value as a string.

    """
    value = tag.get(name, default)
    return value if isinstance(value, str) else default
