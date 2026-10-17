"""End-to-end regression tests for issue #103 (KaTeX without markdown-katex)."""

from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup
from pypdf import PdfReader

# Building the fixture runs headless Chrome; keep the tests on one worker so the
# session-scoped fixture is built once.
pytestmark = pytest.mark.xdist_group("issue103-katex-without-markdown-extension")


def _html(
    built_issue_103_katex_without_markdown_extension: SimpleNamespace,
) -> BeautifulSoup:
    """Parse the combined HTML produced for the without-markdown-katex fixture."""
    text = built_issue_103_katex_without_markdown_extension.html_path.read_text(
        encoding="utf-8",
    )
    return BeautifulSoup(text, "html.parser")


def _pdf_text(built_issue_103_katex_without_markdown_extension: SimpleNamespace) -> str:
    """Extract and join the text of every PDF page."""
    reader = PdfReader(str(built_issue_103_katex_without_markdown_extension.pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def test_issue_103_build_succeeds(
    built_issue_103_katex_without_markdown_extension: SimpleNamespace,
) -> None:
    """The fixture builds to both combined HTML and a PDF."""
    assert built_issue_103_katex_without_markdown_extension.html_path.is_file()
    assert built_issue_103_katex_without_markdown_extension.pdf_path.is_file()


def test_issue_103_combined_html_has_doctype(
    built_issue_103_katex_without_markdown_extension: SimpleNamespace,
) -> None:
    """
    The combined HTML starts with a doctype.

    KaTeX refuses to run in quirks mode ("KaTeX doesn't work in quirks mode"),
    and headless Chrome only renders in standards mode when the document
    declares a doctype.
    """
    text = built_issue_103_katex_without_markdown_extension.html_path.read_text(
        encoding="utf-8",
    )
    assert text.lstrip().lower().startswith("<!doctype html>")


def test_issue_103_katex_renders(
    built_issue_103_katex_without_markdown_extension: SimpleNamespace,
) -> None:
    """Both the inline and the block expression are converted by KaTeX."""
    soup = _html(built_issue_103_katex_without_markdown_extension)
    assert len(soup.find_all(class_="katex")) == 2
    # KaTeX emits an accessible MathML copy alongside the visual HTML.
    assert len(soup.find_all(class_="katex-mathml")) == 2


def test_issue_103_pdf_has_rendered_math(
    built_issue_103_katex_without_markdown_extension: SimpleNamespace,
) -> None:
    """The PDF contains selectable rendered math, not the raw TeX source."""
    text = _pdf_text(built_issue_103_katex_without_markdown_extension)
    assert "$a^2 + b^2 = c^2$" not in text
    assert "$$" not in text
    # KaTeX lays the expression out as selectable spans; the exact spacing of
    # the extracted text varies, hence the compact form.
    assert "a2+b2=c2" in text
