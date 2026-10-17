"""Tests for the element exclusion helper."""

import pytest
from _type_aliases import SoupFactory

from mkdocs_to_pdf.utils.exclude_util import remove_elements


def test_remove_elements_no_selectors_is_noop(make_soup: SoupFactory) -> None:
    """Leave the document untouched when no selectors are configured."""
    soup = make_soup('<p class="feedback-button">Feedback</p>')

    remove_elements(soup, [])

    assert soup.find("p") is not None


def test_remove_elements_removes_match_and_children(make_soup: SoupFactory) -> None:
    """Remove the matching element together with its descendants."""
    soup = make_soup(
        '<div class="print-hidden"><p>Hidden <span>child</span></p></div>',
    )

    remove_elements(soup, [".print-hidden"])

    assert soup.find("div", class_="print-hidden") is None
    assert soup.find("span") is None


def test_remove_elements_keeps_non_matching_elements(make_soup: SoupFactory) -> None:
    """Leave elements that do not match a selector in place."""
    soup = make_soup('<p class="feedback-button">Feedback</p><p>Visible</p>')

    remove_elements(soup, [".feedback-button"])

    assert soup.find("p", class_="feedback-button") is None
    visible = soup.find("p")
    assert visible is not None
    assert visible.get_text() == "Visible"


def test_remove_elements_applies_every_selector(make_soup: SoupFactory) -> None:
    """Remove the union of every configured selector."""
    soup = make_soup(
        '<a class="feedback-button">Feedback</a>'
        '<div id="web-only-banner">Banner</div>'
        "<p>Visible</p>",
    )

    remove_elements(soup, [".feedback-button", "#web-only-banner"])

    assert soup.find(class_="feedback-button") is None
    assert soup.find(id="web-only-banner") is None
    assert soup.find("p") is not None


def test_remove_elements_invalid_selector_raises(make_soup: SoupFactory) -> None:
    """Raise a descriptive error for a selector that is not valid CSS."""
    soup = make_soup("<p>Visible</p>")

    with pytest.raises(ValueError, match="Invalid exclude_elements selector"):
        remove_elements(soup, ["div["])
