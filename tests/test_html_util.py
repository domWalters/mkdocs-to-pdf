"""Tests for the HTML string helpers."""

from mkdocs_to_pdf.utils.html_util import html_to_text


def test_html_to_text_strips_tags() -> None:
    """Tags are removed and their text content is kept."""
    html = 'Copyright <a href="https://example.com">Example</a>'

    assert html_to_text(html) == "Copyright Example"


def test_html_to_text_unescapes_entities() -> None:
    """HTML entities are decoded to their characters."""
    assert html_to_text("Copyright &copy; 2026") == "Copyright © 2026"


def test_html_to_text_plain_string_unchanged() -> None:
    """A string without markup is returned as-is."""
    assert html_to_text("Copyright Fixture") == "Copyright Fixture"
