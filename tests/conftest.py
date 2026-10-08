import logging
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from _types import OptionsFactory, SoupFactory
from bs4 import BeautifulSoup
from mkdocs.commands.build import build
from mkdocs.config import load_config

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def make_options() -> OptionsFactory:
    """Build a stand-in for `mkdocs_to_pdf.options.Options`."""

    def factory(**overrides: object) -> SimpleNamespace:
        """Return an options stand-in with `overrides` applied."""
        base: dict[str, object] = {
            "toc_title": "Table of contents",
            "toc_level": 3,
            "ordered_chapter_level": 3,
            "excludes_children": [],
            "cover": True,
            "back_cover": False,
            "logger": logging.getLogger("mkdocs_to_pdf.test"),
        }
        base.update(overrides)
        return SimpleNamespace(**base)

    return factory


@pytest.fixture
def make_soup() -> SoupFactory:
    """Parse HTML, optionally wrapped in a minimal html/body."""

    def factory(html: str, *, body: bool = True) -> BeautifulSoup:
        """Parse `html`, wrapping it in `<html><body>` unless `body` is false."""
        if body:
            return BeautifulSoup(f"<html><body>{html}</body></html>", "html.parser")
        return BeautifulSoup(html, "html.parser")

    return factory


@pytest.fixture(scope="session")
def built_site(tmp_path_factory: pytest.TempPathFactory) -> SimpleNamespace:
    """
    Build the fixture MkDocs site once and expose the generated artifacts.

    This drives the plugin through the real `mkdocs build` pipeline, producing
    both the combined HTML (`html_path`) and the final PDF.
    """
    root = tmp_path_factory.mktemp("built_site")
    project = root / "project"
    shutil.copytree(FIXTURES / "site", project)
    site_dir = root / "site"

    config = load_config(
        config_file=str(project / "mkdocs.yml"),
        docs_dir=str(project / "docs"),
        site_dir=str(site_dir),
    )
    build(config)

    return SimpleNamespace(
        project=project,
        site_dir=site_dir,
        html_path=site_dir / "single.html",
        pdf_path=site_dir / "pdf" / "document.pdf",
    )
