"""End-to-end regression tests for issue #103 (KaTeX via markdown-katex)."""

from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup
from pypdf import PdfReader

pytestmark = pytest.mark.xdist_group("issue103-katex-with-markdown-extension")


def _html(
    built_issue_103_katex_with_markdown_extension: SimpleNamespace,
) -> BeautifulSoup:
    """Parse the combined HTML produced for the markdown-katex fixture."""
    text = built_issue_103_katex_with_markdown_extension.html_path.read_text(
        encoding="utf-8",
    )
    return BeautifulSoup(text, "html.parser")


def _pdf_text(built_issue_103_katex_with_markdown_extension: SimpleNamespace) -> str:
    """Extract and join the text of every PDF page."""
    reader = PdfReader(str(built_issue_103_katex_with_markdown_extension.pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def test_markdown_katex_build_succeeds(
    built_issue_103_katex_with_markdown_extension: SimpleNamespace,
) -> None:
    """The fixture builds to both combined HTML and a PDF."""
    assert built_issue_103_katex_with_markdown_extension.html_path.is_file()
    assert built_issue_103_katex_with_markdown_extension.pdf_path.is_file()


def test_markdown_katex_renders(
    built_issue_103_katex_with_markdown_extension: SimpleNamespace,
) -> None:
    """The inline and the fenced `math` block are both rendered by KaTeX."""
    soup = _html(built_issue_103_katex_with_markdown_extension)
    assert len(soup.find_all(class_="katex")) == 2
    # KaTeX emits an accessible MathML copy alongside the visual HTML.
    assert len(soup.find_all(class_="katex-mathml")) == 2


def test_markdown_katex_pdf_has_rendered_math(
    built_issue_103_katex_with_markdown_extension: SimpleNamespace,
) -> None:
    """The PDF contains selectable rendered math, not a code block."""
    text = _pdf_text(built_issue_103_katex_with_markdown_extension)
    assert "```" not in text
    # KaTeX lays the expressions out as selectable spans; the exact spacing of
    # the extracted text varies, hence the compact forms.
    assert "a2+b2=c2" in text
    assert "f(x)=" in text
