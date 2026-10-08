"""
End-to-end tests driven through a real `mkdocs build`.

Layer 2 asserts on the combined HTML produced via the `html_path` option.
Layer 3 asserts on the final PDF structure/content with `pypdf`.
"""

from collections.abc import Iterable
from types import SimpleNamespace

from bs4 import BeautifulSoup
from pypdf import PdfReader


def _html(built_site: SimpleNamespace) -> BeautifulSoup:
    """Parse the generated combined HTML."""
    text = built_site.html_path.read_text(encoding="utf-8")
    return BeautifulSoup(text, "html.parser")


def _reader(built_site: SimpleNamespace) -> PdfReader:
    """Open the generated PDF for reading."""
    return PdfReader(str(built_site.pdf_path))


def _outline_titles(reader: PdfReader) -> list[str]:
    """Return every outline entry title, flattened in document order."""
    titles: list[str] = []

    def walk(nodes: Iterable[object]) -> None:
        """Walk nested outline nodes, appending each title."""
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


# --------------------------------------------------------------------------
# Layer 2: combined HTML
# --------------------------------------------------------------------------


def test_html_output_created(built_site: SimpleNamespace) -> None:
    """The combined HTML is written to `html_path`."""
    assert built_site.html_path.is_file()
    head = built_site.html_path.read_text(encoding="utf-8")[:200].lower()
    assert "<html" in head


def test_cover_rendered(built_site: SimpleNamespace) -> None:
    """The cover renders the configured title, subtitle and author."""
    cover = _html(built_site).find("article", id="doc-cover")
    assert cover is not None
    title = cover.find("h1")
    subtitle = cover.find("h2")
    author = cover.find("p", id="author")
    assert title is not None
    assert subtitle is not None
    assert author is not None
    assert title.get_text(strip=True) == "Fixture Cover"
    assert subtitle.get_text(strip=True) == "Fixture Subtitle"
    assert author.get_text(strip=True) == "Jane Doe"


def test_toc_generated(built_site: SimpleNamespace) -> None:
    """The table of contents lists numbered, nested headings."""
    soup = _html(built_site)
    toc = soup.find("article", id="doc-toc")
    assert toc is not None
    title = toc.find("h1")
    assert title is not None
    assert title.get_text(strip=True) == "Contents"

    texts = [a.get_text().strip() for a in toc.find_all("a")]
    assert texts[0] == "1. Introduction"
    assert "2. Page One" in texts
    assert "3.1.1 Child Heading" in texts

    outer = toc.find("ul")
    assert outer is not None
    assert outer.find("ul") is not None


def test_headings_numbered(built_site: SimpleNamespace) -> None:
    """Headings carry hierarchical numbering prefixes."""
    soup = _html(built_site)

    def order(anchor_id: str) -> str:
        """Return the numbering prefix attached to the given heading."""
        heading = soup.find(id=anchor_id)
        assert heading is not None, anchor_id
        badge = heading.find("span", class_="pdf-order")
        assert badge is not None
        return badge.get_text(strip=True)

    assert order("page-one/:section-a") == "2.1"
    assert order("nested/child/:child-heading") == "3.1.1"


def test_internal_links_transformed_and_resolve(built_site: SimpleNamespace) -> None:
    """Document links are rewritten to anchors that all resolve."""
    soup = _html(built_site)

    remaining = [
        str(a["href"])
        for a in soup.select("a[href]")
        if ".md" in str(a["href"]) or ".html" in str(a["href"])
    ]
    assert not remaining

    ids = {str(el["id"]) for el in soup.find_all(id=True)}
    for a in soup.select('a[href^="#"]'):
        target = str(a["href"])[1:]
        if target:
            assert target in ids, f"dangling anchor: {a['href']}"


def test_asset_hrefs_absolute_and_image_alignment(built_site: SimpleNamespace) -> None:
    """Image assets are absolutized and alignment folded into styles."""
    soup = _html(built_site)

    img = soup.find("img")
    assert img is not None
    assert str(img["src"]).startswith("file://")
    assert "align" not in img.attrs
    assert "float: right;" in str(img["style"])
    assert "width: 80px;" in str(img["style"])


# --------------------------------------------------------------------------
# Layer 3: the PDF
# --------------------------------------------------------------------------


def test_pdf_created_and_paginated(built_site: SimpleNamespace) -> None:
    """The PDF exists, has a PDF header and spans multiple pages."""
    assert built_site.pdf_path.is_file()
    assert bytes(built_site.pdf_path.read_bytes()).startswith(b"%PDF-")

    reader = _reader(built_site)
    assert len(reader.pages) >= 4


def test_pdf_metadata(built_site: SimpleNamespace) -> None:
    """Document metadata reflects the site title and author."""
    metadata = _reader(built_site).metadata
    assert metadata is not None
    assert metadata.title == "Fixture Site"
    assert metadata.author == "Jane Doe"
    producer = metadata.producer or ""
    assert producer.startswith("WeasyPrint")


def test_pdf_text_contains_rendered_content(built_site: SimpleNamespace) -> None:
    """Extracted PDF text contains the rendered content."""
    text = _pdf_text(_reader(built_site))
    for needle in [
        "Fixture Cover",
        "Fixture Subtitle",
        "Contents",
        "Introduction",
        "Getting started",
        "Page One",
        "Child Heading",
    ]:
        assert needle in text, needle


def test_pdf_outline_matches_heading_structure(built_site: SimpleNamespace) -> None:
    """PDF bookmarks mirror the document heading hierarchy."""
    titles = _outline_titles(_reader(built_site))
    assert "Fixture Cover" in titles
    assert "1. Introduction" in titles
    assert "2. Page One" in titles
    assert "3.1.1 Child Heading" in titles

    assert titles.index("1. Introduction") < titles.index("2. Page One")
    assert titles.index("2. Page One") < titles.index("3.1.1 Child Heading")


def test_pdf_named_destinations(built_site: SimpleNamespace) -> None:
    """Internal anchors are exported as named destinations."""
    destinations = set(_reader(built_site).named_destinations)
    assert ".:" in destinations
    assert "doc-cover" in destinations
    assert "doc-toc" in destinations
    assert "page-one/:section-a" in destinations
    assert "nested/child/:child-heading" in destinations


def test_pdf_has_link_annotations(built_site: SimpleNamespace) -> None:
    """The PDF contains at least one link annotation."""
    reader = _reader(built_site)
    count = 0
    for page in reader.pages:
        for annotation in page.get("/Annots") or []:
            if annotation.get_object().get("/Subtype") == "/Link":
                count += 1
    assert count > 0


def test_pdf_internal_links_resolve(built_site: SimpleNamespace) -> None:
    """Every internal link target exists as a PDF destination."""
    destinations = set(_reader(built_site).named_destinations)
    soup = _html(built_site)

    for a in soup.select('a[href^="#"]'):
        target = str(a["href"])[1:]
        if target:
            assert target in destinations, f"unresolved PDF link: {a['href']}"
