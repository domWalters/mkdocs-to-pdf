"""Regression tests for issue #104: aligned images overlap nearby content."""

from types import SimpleNamespace
from typing import Protocol

import weasyprint

_Rect = tuple[float, float, float, float]
_Foreground = tuple[float, float, float, float, str]


class _Box(Protocol):
    """The subset of WeasyPrint's box interface used by these tests."""

    position_x: float
    position_y: float
    width: float
    height: float
    element_tag: str | None
    text: str
    children: list["_Box"]


def _flatten(box: _Box) -> list[_Box]:
    """Return `box` and all of its descendants, depth-first."""
    boxes = [box]
    for child in box.children:
        boxes.extend(_flatten(child))
    return boxes


def _rect(box: _Box) -> _Rect:
    """Return the box's `(x, y, width, height)` rectangle."""
    return (box.position_x, box.position_y, box.width, box.height)


def _overlap(a: _Rect, b: _Rect) -> bool:
    """Return whether two rectangles overlap."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def _images_and_foreground(
    html_path: str,
) -> tuple[list[_Rect], list[_Foreground]]:
    """
    Return the image and foreground rectangles for a rendered page set.

    Foreground covers text, list markers and pseudo-element decorations (such
    as the admonition icon): everything WeasyPrint paints on top of a float.
    """
    document = weasyprint.HTML(filename=html_path).render()
    images: list[_Rect] = []
    foreground: list[_Foreground] = []
    for page in document.pages:
        for box in _flatten(page._page_box):  # ruff: ignore[private-member-access]
            name = type(box).__name__
            tag = box.element_tag or ""
            if name == "BlockReplacedBox" and tag == "img":
                images.append(_rect(box))
            elif name == "TextBox":
                text = box.text.strip()
                if text:
                    foreground.append((*_rect(box), text))
            elif "::" in tag:
                foreground.append((*_rect(box), tag))
    return images, foreground


def test_aligned_images_do_not_overlap_content(
    built_issue_104: SimpleNamespace,
) -> None:
    """A floated image must not overlap the content that wraps around it."""
    images, foreground = _images_and_foreground(str(built_issue_104.html_path))

    assert images, "fixture should contain aligned images"
    assert foreground, "fixture should contain foreground content"

    overlaps = [
        (image, content)
        for image in images
        for content in foreground
        if _overlap(image, content[:4])
    ]
    assert not overlaps, f"image overlaps content: {overlaps}"
