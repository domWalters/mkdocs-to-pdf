"""End-to-end tests for the `exclude_pages` option."""

from types import SimpleNamespace

from bs4 import BeautifulSoup


def _html(built_exclude_pages: SimpleNamespace) -> BeautifulSoup:
    """Parse the combined HTML produced for the exclude-pages fixture."""
    text = built_exclude_pages.html_path.read_text(encoding="utf-8")
    return BeautifulSoup(text, "html.parser")


def test_exclude_pages_removes_matching_pages(
    built_exclude_pages: SimpleNamespace,
) -> None:
    """Pages whose URL matches a pattern are left out of the PDF."""
    text = _html(built_exclude_pages).get_text()

    assert "Welcome to the home page." in text
    assert "Bug list." not in text
    assert "Known bug details." not in text
    assert "Contribution guide." not in text


def test_exclude_pages_removes_matching_headings_from_toc(
    built_exclude_pages: SimpleNamespace,
) -> None:
    """Excluded pages contribute no entries to the table of contents."""
    toc = _html(built_exclude_pages).find("article", id="doc-toc")
    assert toc is not None

    hrefs = [str(a["href"]) for a in toc.find_all("a")]
    assert not any(href.startswith("#bugs/") for href in hrefs)
    assert not any(href.startswith("#appendix/") for href in hrefs)
