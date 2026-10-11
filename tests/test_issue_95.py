"""End-to-end regression tests for issue #95 (skipped heading levels)."""

from types import SimpleNamespace

from bs4 import BeautifulSoup
from pypdf import PdfReader


def _html(built_issue_95: SimpleNamespace) -> BeautifulSoup:
    """Parse the combined HTML produced for the issue #95 fixture."""
    text = built_issue_95.html_path.read_text(encoding="utf-8")
    return BeautifulSoup(text, "html.parser")


def _reader(built_issue_95: SimpleNamespace) -> PdfReader:
    """Open the PDF produced for the issue #95 fixture."""
    return PdfReader(str(built_issue_95.pdf_path))


def _pdf_text(reader: PdfReader) -> str:
    """Extract and join the text of every page."""
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def test_issue_95_build_succeeds(built_issue_95: SimpleNamespace) -> None:
    """Building a site whose headings skip a level does not crash."""
    assert built_issue_95.html_path.is_file()
    assert built_issue_95.pdf_path.is_file()


def test_issue_95_toc_nests_skipped_level_heading(
    built_issue_95: SimpleNamespace,
) -> None:
    """The deeper heading nests under its nearest ancestor in the TOC."""
    soup = _html(built_issue_95)
    toc = soup.find("article", id="doc-toc")
    assert toc is not None

    subsection = next(
        (a for a in toc.find_all("a") if "sub-section" in a.get_text()),
        None,
    )
    assert subsection is not None

    # It must hang off the "Introduction" entry, not sit at the top level.
    parent_li = subsection.find_parent("li")
    assert parent_li is not None
    enclosing_li = parent_li.find_parent("li")
    assert enclosing_li is not None
    intro = enclosing_li.find("a", recursive=False)
    assert intro is not None
    assert "Introduction" in intro.get_text()


def test_issue_95_pdf_contains_content(built_issue_95: SimpleNamespace) -> None:
    """The generated PDF contains both the page and the skipped-level heading."""
    text = _pdf_text(_reader(built_issue_95))
    for needle in ["Introduction", "sub-section", "test123", "test456"]:
        assert needle in text, needle
