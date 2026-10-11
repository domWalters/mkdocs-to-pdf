"""End-to-end regression tests for issue #85 (inline MathJax not rendered)."""

import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup
from mkdocs.commands.build import build
from mkdocs.config import load_config
from pypdf import PdfReader

# Building the fixture runs headless Chrome; keep the tests on one worker so the
# session-scoped fixture is built once.
pytestmark = pytest.mark.xdist_group("issue85")

FIXTURES = Path(__file__).parent / "fixtures"

# A stand-in for headless Chrome: `--dump-dom` is emulated by echoing the temp
# HTML file back, so the script collection can be exercised without running JS.
_FAKE_CHROME = '#!/bin/sh\nfor last; do :; done\ncat "$last"\n'


def _html(built_issue_85: SimpleNamespace) -> BeautifulSoup:
    """Parse the combined HTML produced for the issue #85 fixture."""
    text = built_issue_85.html_path.read_text(encoding="utf-8")
    return BeautifulSoup(text, "html.parser")


def _pdf_text(built_issue_85: SimpleNamespace) -> str:
    """Extract and join the text of every PDF page."""
    reader = PdfReader(str(built_issue_85.pdf_path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def test_issue_85_build_succeeds(built_issue_85: SimpleNamespace) -> None:
    """The fixture builds to both combined HTML and a PDF."""
    assert built_issue_85.html_path.is_file()
    assert built_issue_85.pdf_path.is_file()


def test_issue_85_mathjax_runs(built_issue_85: SimpleNamespace) -> None:
    """
    Both the inline and the block expression are converted by MathJax.

    The inline expression uses `$...$`, which only MathJax renders when the
    site's local `javascripts/mathjax.js` config is present. If that script
    were dropped only the block expression (whose `$$...$$` delimiters MathJax
    enables by default) would produce an `mjx-container`.
    """
    soup = _html(built_issue_85)
    assert len(soup.find_all("mjx-container")) == 2


def test_issue_85_pdf_has_rendered_math(built_issue_85: SimpleNamespace) -> None:
    """The PDF contains rendered math, not the raw TeX source."""
    text = _pdf_text(built_issue_85)
    assert "$a^2 + b^2 = c^2$" not in text
    assert "$$" not in text
    assert "a2 + b2 = c2" in text


def test_issue_85_local_scripts_replayed(tmp_path: Path) -> None:
    """
    Local scripts (e.g. the MathJax config) are replayed as `file://` URLs.

    Before the fix, `_scrap_scripts` kept only `https://` scripts, so Material's
    local `javascripts/mathjax.js` (which enables `$...$` inline math) never
    reached the JavaScript renderer.
    """
    project = tmp_path / "project"
    shutil.copytree(FIXTURES / "issue-85", project)

    fake_chrome = tmp_path / "chrome"
    fake_chrome.write_text(_FAKE_CHROME, encoding="utf-8")
    fake_chrome.chmod(0o755)

    config_path = project / "mkdocs.yml"
    config_path.write_text(
        config_path.read_text(encoding="utf-8").replace(
            "headless_chrome_path: chromium",
            f"headless_chrome_path: {fake_chrome}",
        ),
        encoding="utf-8",
    )

    site_dir = tmp_path / "site"
    config = load_config(
        config_file=str(config_path),
        docs_dir=str(project / "docs"),
        site_dir=str(site_dir),
    )
    build(config)

    soup = BeautifulSoup(
        (site_dir / "single.html").read_text(encoding="utf-8"),
        "html.parser",
    )
    scripts = [str(s["src"]) for s in soup.find_all("script", src=True)]

    mathjax_config = [s for s in scripts if s.endswith("javascripts/mathjax.js")]
    assert mathjax_config, scripts
    assert mathjax_config[0].startswith("file://")
    assert "https://unpkg.com/mathjax@3/es5/tex-mml-chtml.js" in scripts
