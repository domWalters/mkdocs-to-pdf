"""
End-to-end layout regression tests for WeasyPrint upgrades.

These assert structural invariants (no truncation, complete outline, resolving
anchors) rather than pixel output, so they stay stable across WeasyPrint
versions while still catching the layout regressions tracked in issues #34,
#35, #42 and #62.
"""

from collections.abc import Iterable
from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup
from pypdf import PdfReader

# WeasyPrint 62.3 drops everything after the long code block in this fixture
# (issues #34 and #62). These assertions describe the correct behaviour; they
# are expected to fail until WeasyPrint is upgraded, then XPASS so the markers
# can be removed.
_TRUNCATION_XFAIL = pytest.mark.xfail(
    reason="WeasyPrint 62.3 truncates after a page-spanning code block (#34/#62)",
    strict=False,
)

_CONTENT_SENTINELS = [
    "WEASYPRINT_FINAL_SENTINEL",
    "WEASYPRINT_GRID_SENTINEL",
    "WEASYPRINT_FOOTNOTE_SENTINEL",
    "WEASYPRINT_ADMONITION_SENTINEL",
]

_LAST_HEADING = "Final Sentinel Heading"


def _html(built_weasyprint: SimpleNamespace) -> BeautifulSoup:
    """Parse the combined HTML produced for the regression fixture."""
    text = built_weasyprint.html_path.read_text(encoding="utf-8")
    return BeautifulSoup(text, "html.parser")


def _reader(built_weasyprint: SimpleNamespace) -> PdfReader:
    """Open the PDF produced for the regression fixture."""
    return PdfReader(str(built_weasyprint.pdf_path))


def _outline_titles(reader: PdfReader) -> list[str]:
    """Return every outline entry title, flattened in document order."""
    titles: list[str] = []

    def walk(nodes: Iterable[object]) -> None:
        for node in nodes or []:
            if isinstance(node, list):
                walk(node)
            else:
                titles.append(str(getattr(node, "title", node)))

    walk(reader.outline)
    return titles


def _pdf_text(reader: PdfReader) -> str:
    """Extract and join the text of every page."""
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _content_headings(soup: BeautifulSoup) -> list[str]:
    """Return the text of every content heading, without numbering badges."""
    for article_id in ("doc-cover", "doc-toc", "doc-back_cover"):
        for article in soup.find_all("article", id=article_id):
            article.decompose()

    headings: list[str] = []
    for heading in soup.find_all(["h1", "h2", "h3"]):
        badge = heading.find("span", class_="pdf-order")
        if badge is not None:
            badge.decompose()
        text = heading.get_text(" ", strip=True)
        if text:
            headings.append(text)
    return headings


def test_regression_build_succeeds(built_weasyprint: SimpleNamespace) -> None:
    """The fixture builds to both combined HTML and a PDF."""
    assert built_weasyprint.html_path.is_file()
    assert built_weasyprint.pdf_path.is_file()
    assert built_weasyprint.pdf_path.read_bytes().startswith(b"%PDF-")


def test_regression_page_floor(built_weasyprint: SimpleNamespace) -> None:
    """The document spans several pages (a truncation collapses it)."""
    assert len(_reader(built_weasyprint).pages) >= 4


@_TRUNCATION_XFAIL
def test_regression_not_truncated(built_weasyprint: SimpleNamespace) -> None:
    """Every sentinel survives to the PDF, including those after the long block."""
    text = _pdf_text(_reader(built_weasyprint))
    for sentinel in _CONTENT_SENTINELS:
        assert sentinel in text, sentinel


@_TRUNCATION_XFAIL
def test_regression_outline_complete(built_weasyprint: SimpleNamespace) -> None:
    """Every content heading appears in both the outline and the text."""
    soup = _html(built_weasyprint)
    headings = _content_headings(soup)
    assert _LAST_HEADING in headings

    titles = _outline_titles(_reader(built_weasyprint))
    text = _pdf_text(_reader(built_weasyprint))

    for heading in headings:
        assert any(heading in title for title in titles), heading
        assert heading in text, heading


@_TRUNCATION_XFAIL
def test_regression_anchors_resolve(built_weasyprint: SimpleNamespace) -> None:
    """Every internal link resolves to a PDF named destination."""
    destinations = set(_reader(built_weasyprint).named_destinations)

    for anchor in _html(built_weasyprint).select('a[href^="#"]'):
        target = str(anchor["href"])[1:]
        if target:
            assert target in destinations, f"dangling anchor: {anchor['href']}"


def test_regression_no_dangling_doc_links(
    built_weasyprint: SimpleNamespace,
) -> None:
    """Document links are rewritten to in-document anchors."""
    remaining = [
        str(anchor["href"])
        for anchor in _html(built_weasyprint).select("a[href]")
        if ".md" in str(anchor["href"]) or ".html" in str(anchor["href"])
    ]
    assert not remaining


def test_regression_cover_rendered(built_weasyprint: SimpleNamespace) -> None:
    """The cover renders the configured title and subtitle."""
    cover = _html(built_weasyprint).find("article", id="doc-cover")
    assert cover is not None
    title = cover.find("h1")
    subtitle = cover.find("h2")
    assert title is not None
    assert subtitle is not None
    assert title.get_text(strip=True) == "WeasyPrint Regression"
    assert subtitle.get_text(strip=True) == "Layout correctness corpus"
