"""End-to-end regression tests for issue #88 (lists waste whole pages)."""

from types import SimpleNamespace

from pypdf import PdfReader


def _reader(built_issue_88: SimpleNamespace) -> PdfReader:
    """Open the PDF produced for the issue #88 fixture."""
    return PdfReader(str(built_issue_88.pdf_path))


def test_issue_88_build_succeeds(built_issue_88: SimpleNamespace) -> None:
    """Building the nested-list site produces both artifacts."""
    assert built_issue_88.html_path.is_file()
    assert built_issue_88.pdf_path.is_file()


def test_issue_88_does_not_waste_pages(built_issue_88: SimpleNamespace) -> None:
    """The nested list must not push most of its content onto empty pages."""
    reader = _reader(built_issue_88)
    # Before the fix this was 8 pages for the cover, TOC and one short page.
    # Cover + TOC + one content page is 3; allow a little slack, but a
    # regression to the old `page-break-inside: avoid` behaviour is caught.
    assert len(reader.pages) <= 5


def test_issue_88_pdf_contains_content(built_issue_88: SimpleNamespace) -> None:
    """Splitting the list across pages does not drop any of its entries."""
    text = "\n".join(
        page.extract_text() or "" for page in _reader(built_issue_88).pages
    )
    for needle in [
        "Help for GSAS-II",
        "Universal data tree items",
        "Pair Distribution Functions (PDF)",
        "Programmers' documentation",
    ]:
        assert needle in text, needle
