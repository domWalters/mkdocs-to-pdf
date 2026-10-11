import importlib.util
import logging
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import cast

import pytest
from mkdocs.config import load_config
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import get_files

HOOK_PATH = Path(__file__).resolve().parents[1] / "hooks" / "publish-fixture-pdfs.py"


def _load_hook() -> ModuleType:
    """Load the dashed hook filename as an importable module."""
    spec = importlib.util.spec_from_file_location("publish_fixture_pdfs", HOOK_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_discover_fixtures_returns_sorted_directories(tmp_path: Path) -> None:
    """Only directories are listed, in alphabetical order."""
    (tmp_path / "beta").mkdir()
    (tmp_path / "alpha").mkdir()
    (tmp_path / "notes.txt").write_text("not a fixture")

    assert _load_hook().discover_fixtures(tmp_path) == ["alpha", "beta"]


def test_relative_prefix_directory_urls() -> None:
    """Directory URLs add one level of nesting to the output path."""
    hook = _load_hook()
    assert hook.relative_prefix(
        "examples/example-pdfs.md",
        use_directory_urls=True,
    ) == ("../../")
    assert hook.relative_prefix(
        "examples/example-pdfs.md",
        use_directory_urls=False,
    ) == ("../")
    assert hook.relative_prefix("index.md", use_directory_urls=True) == "../"
    assert not hook.relative_prefix("index.md", use_directory_urls=False)


def test_render_gallery_links_every_fixture() -> None:
    """Every fixture gets a raw HTML link relative to the page."""
    hook = _load_hook()

    page = hook.render_gallery(
        ["base", "weasyprint"],
        src_uri="examples/example-pdfs.md",
        use_directory_urls=True,
    )

    assert "<title" not in page
    for name in ("base", "weasyprint"):
        assert f'href="../../fixtures/{name}.pdf"' in page


def _config(tmp_path: Path) -> MkDocsConfig:
    """Load a minimal MkDocs config backed by a temporary project."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.md").write_text("# Home\n", encoding="utf-8")
    (tmp_path / "mkdocs.yml").write_text("site_name: Hook Test\n", encoding="utf-8")
    return load_config(config_file=str(tmp_path / "mkdocs.yml"))


def test_on_files_adds_gallery_page(tmp_path: Path) -> None:
    """The generated gallery is appended to the documentation files."""
    hook = _load_hook()
    config = _config(tmp_path)
    files = get_files(config)

    # `File.generated` attributes the file to the running plugin; there is no
    # plugin context when the handler is called directly.
    config.plugins._current_plugin = hook.GALLERY_SRC_URI  # ruff: ignore[private-member-access]

    result = hook.on_files(files, config)

    assert any(file.src_uri == hook.GALLERY_SRC_URI for file in result)
    gallery = next(file for file in result if file.src_uri == hook.GALLERY_SRC_URI)
    assert gallery.is_documentation_page()


def test_on_post_build_copies_each_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each discovered fixture PDF is copied into the site's fixtures directory."""
    hook = _load_hook()
    fixtures = tmp_path / "fixtures"
    (fixtures / "alpha").mkdir(parents=True)
    (fixtures / "beta").mkdir()
    monkeypatch.setattr(hook, "FIXTURES_DIR", fixtures)

    order: list[str] = []

    def fake_build(name: str, dest_dir: Path) -> Path:
        order.append(name)
        destination = dest_dir / f"{name}.pdf"
        destination.write_bytes(b"%PDF-1.4")
        return destination

    monkeypatch.setattr(hook, "build_fixture_pdf", fake_build)

    site_dir = tmp_path / "site"
    config = cast("MkDocsConfig", SimpleNamespace(site_dir=str(site_dir)))
    hook.on_post_build(config)

    assert order == ["alpha", "beta"]
    assert sorted(p.name for p in (site_dir / "fixtures").iterdir()) == [
        "alpha.pdf",
        "beta.pdf",
    ]


def test_on_post_build_continues_after_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A failing fixture does not stop the remaining PDFs being published."""
    hook = _load_hook()
    fixtures = tmp_path / "fixtures"
    (fixtures / "broken").mkdir(parents=True)
    (fixtures / "ok").mkdir()
    monkeypatch.setattr(hook, "FIXTURES_DIR", fixtures)

    def fake_build(name: str, dest_dir: Path) -> Path:
        if name == "broken":
            msg = "boom"
            raise RuntimeError(msg)
        destination = dest_dir / f"{name}.pdf"
        destination.write_bytes(b"%PDF-1.4")
        return destination

    monkeypatch.setattr(hook, "build_fixture_pdf", fake_build)

    site_dir = tmp_path / "site"
    config = cast("MkDocsConfig", SimpleNamespace(site_dir=str(site_dir)))
    with caplog.at_level(logging.ERROR, logger=hook.__name__):
        hook.on_post_build(config)

    assert [p.name for p in (site_dir / "fixtures").iterdir()] == ["ok.pdf"]
    assert "Failed to build fixture PDF 'broken'" in caplog.text
