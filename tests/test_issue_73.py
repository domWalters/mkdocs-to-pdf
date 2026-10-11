"""End-to-end regression tests for issue #73 (light/dark theme images)."""

from types import SimpleNamespace

from bs4 import BeautifulSoup

_DARK_SELECTORS = [
    '.md-typeset img[src$="#only-dark"]',
    '.md-typeset img[src$="#gh-dark-mode-only"]',
    '.md-typeset figure img[src$="#only-dark"]',
    '.md-typeset figure img[src$="#gh-dark-mode-only"]',
]


def _html(built_issue_73: SimpleNamespace) -> BeautifulSoup:
    """Parse the combined HTML produced for the issue #73 fixture."""
    text = built_issue_73.html_path.read_text(encoding="utf-8")
    return BeautifulSoup(text, "html.parser")


def _styles(soup: BeautifulSoup) -> str:
    """Join the contents of every `<style>` tag in the document."""
    return "\n".join(tag.get_text() for tag in soup.find_all("style"))


def test_issue_73_build_succeeds(built_issue_73: SimpleNamespace) -> None:
    """Building a site with light/dark images produces HTML and a PDF."""
    assert built_issue_73.html_path.is_file()
    assert built_issue_73.pdf_path.is_file()


def test_issue_73_both_variants_in_html(built_issue_73: SimpleNamespace) -> None:
    """Both variants stay in the combined HTML (the CSS hides the dark one)."""
    sources = [str(img["src"]) for img in _html(built_issue_73).find_all("img")]
    assert any(src.endswith("#only-light") for src in sources)
    assert any(src.endswith("#only-dark") for src in sources)


def test_issue_73_dark_variants_hidden_in_print(
    built_issue_73: SimpleNamespace,
) -> None:
    """The print stylesheet hides every dark-mode image variant."""
    styles = _styles(_html(built_issue_73))
    for selector in _DARK_SELECTORS:
        assert selector in styles, selector
