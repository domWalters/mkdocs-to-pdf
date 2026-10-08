from mkdocs_to_pdf.styles import _css_escape


def test_css_escape_empty() -> None:
    """Return an empty string for empty input."""
    assert not _css_escape("")


def test_css_escape_single_quote() -> None:
    """Escape single quotes for use in a CSS string."""
    assert _css_escape("It's") == "It\\27s"


def test_css_escape_unescapes_html_entities() -> None:
    """Unescape HTML entities before emitting CSS."""
    assert _css_escape("Tom &amp; Jerry") == "Tom & Jerry"
    assert _css_escape("&copy; 2026") == "© 2026"
