"""End-to-end tests for the `exclude_elements` option."""

from types import SimpleNamespace

from bs4 import BeautifulSoup


def _html(built_exclude_elements: SimpleNamespace) -> BeautifulSoup:
    """Parse the combined HTML produced for the exclude-elements fixture."""
    text = built_exclude_elements.html_path.read_text(encoding="utf-8")
    return BeautifulSoup(text, "html.parser")


def test_exclude_elements_removed_from_combined_html(
    built_exclude_elements: SimpleNamespace,
) -> None:
    """Configured selectors and their children are absent from the output."""
    soup = _html(built_exclude_elements)

    assert soup.select_one(".feedback-button") is None
    assert soup.select_one("#web-only-banner") is None
    assert soup.select_one("div.print-hidden") is None
    assert soup.select_one("span.nested") is None


def test_exclude_elements_keeps_visible_content(
    built_exclude_elements: SimpleNamespace,
) -> None:
    """Content that does not match a selector is still rendered."""
    text = _html(built_exclude_elements).get_text()

    assert "Visible introduction." in text
    assert "Keep this text." in text
