"""End-to-end regression tests for issue #63 (glightbox image links)."""

from types import SimpleNamespace

from bs4 import BeautifulSoup


def _html(built_issue_63: SimpleNamespace) -> BeautifulSoup:
    """Parse the combined HTML produced for the issue #63 fixture."""
    text = built_issue_63.html_path.read_text(encoding="utf-8")
    return BeautifulSoup(text, "html.parser")


def test_issue_63_build_succeeds(built_issue_63: SimpleNamespace) -> None:
    """Building a site with lightbox image links produces HTML and a PDF."""
    assert built_issue_63.html_path.is_file()
    assert built_issue_63.pdf_path.is_file()


def test_issue_63_unwraps_lightbox_anchor(built_issue_63: SimpleNamespace) -> None:
    """The lightbox anchor is dropped but the image is kept."""
    soup = _html(built_issue_63)

    assert soup.select("a.glightbox") == []
    sources = [str(img["src"]) for img in soup.find_all("img")]
    assert any(src.endswith("assets/image.svg") for src in sources)
