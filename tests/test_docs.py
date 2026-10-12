"""
End-to-end regression test for the repository's own documentation PDF.

Building ``docs/`` exercises the plugin against a large, real Material site, so
layout regressions (in particular truncation) are caught here rather than only
when publishing. This would have caught the ``min-height: 100vh`` regression,
where WeasyPrint 70 dropped most of the document after a handful of pages.
"""

from pathlib import Path

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[1]

# A truncation collapses the documentation PDF to a handful of pages.
_PAGE_FLOOR = 20


@pytest.fixture(scope="session")
def built_docs(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the repository documentation and return the generated PDF."""
    site_dir = tmp_path_factory.mktemp("docs-site")
    config = load_config(
        config_file=str(REPO_ROOT / "mkdocs.yml"),
        site_dir=str(site_dir),
    )
    build(config)
    return site_dir / "pdf" / "document.pdf"


def test_docs_pdf_builds(built_docs: Path) -> None:
    """The documentation builds to a PDF."""
    assert built_docs.is_file()
    assert built_docs.read_bytes().startswith(b"%PDF-")


def test_docs_pdf_is_not_truncated(built_docs: Path) -> None:
    """The whole documentation survives to the PDF, including the last page."""
    reader = PdfReader(str(built_docs))
    assert len(reader.pages) >= _PAGE_FLOOR

    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    # The final nav entry is `LICENSE.md`; its text must reach the PDF.
    assert "OUT OF OR IN CONNECTION WITH THE SOFTWARE" in text
