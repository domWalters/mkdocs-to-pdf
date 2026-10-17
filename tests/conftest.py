import importlib
import logging
import os
import shutil
from pathlib import Path
from types import SimpleNamespace

# Opt in to exercising the suite against ProperDocs, a drop-in MkDocs fork.
# `properdocs.replacement` installs an import hook that redirects every
# `mkdocs.*` import to `properdocs.*`, so it must be imported before anything
# (including this file) imports `mkdocs`. Imported dynamically so the optional
# dependency is not required (or type-checked) for a normal run.
if os.environ.get("MKDOCS_TO_PDF_USE_PROPERDOCS"):
    importlib.import_module("properdocs.replacement")

import pytest
from _type_aliases import OptionsFactory, SoupFactory
from bs4 import BeautifulSoup
from mkdocs.commands.build import build
from mkdocs.config import load_config

FIXTURES = Path(__file__).parent / "fixtures"


class TemplateStub:
    """Stand-in for the Jinja2 template handler used by option stubs."""

    @staticmethod
    def render_string(source: str) -> str:
        """Render a template given as a string using the keywords."""
        return source


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
            "template": TemplateStub(),
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


def _build_fixture(
    tmp_path_factory: pytest.TempPathFactory,
    name: str,
) -> SimpleNamespace:
    """Build the named fixture site and expose the generated artifacts."""
    root = tmp_path_factory.mktemp(name)
    project = root / "project"
    shutil.copytree(FIXTURES / name, project)
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


def _fixture_name(directory: str) -> str:
    """Return the `built_*` fixture name for a fixture directory."""
    return "built_" + "".join(c if c.isalnum() else "_" for c in directory)


def _make_built_fixture(directory: str) -> object:
    """Create a session-scoped fixture that builds the given directory."""

    @pytest.fixture(scope="session", name=_fixture_name(directory))
    def _built(tmp_path_factory: pytest.TempPathFactory) -> SimpleNamespace:
        return _build_fixture(tmp_path_factory, directory)

    return _built


def _register_built_fixtures() -> None:
    """Expose each `tests/fixtures/<dir>` as a session-scoped `built_<dir>`."""
    for path in sorted(FIXTURES.iterdir()):
        if path.is_dir():
            globals()[_fixture_name(path.name)] = _make_built_fixture(path.name)


_register_built_fixtures()
