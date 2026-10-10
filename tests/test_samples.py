"""
Slow end-to-end tests that build the bundled sample sites (issue #34).

Deselected by default; run with ``pytest -m samples``. Building the samples
needs the sample submodules checked out and the ``samples`` extra installed.

The sample is copied to a temporary project whose heavy directories are
symlinked back to the (read-only) submodule, so the submodule is never
modified. The sample's ``mkdocs-yml.patch`` is then applied to the copy.
"""

import contextlib
import os
import shutil
import subprocess  # ruff: ignore[suspicious-subprocess-import]
import tempfile
from collections.abc import Generator, Iterable
from pathlib import Path
from types import SimpleNamespace

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLES = REPO_ROOT / "samples"

pytestmark = [
    pytest.mark.samples,
    pytest.mark.xdist_group("samples"),
]

# A truncation collapses the sample PDF to a handful of pages.
_PAGE_FLOORS = {
    "mkdocs": 50,
    "mkdocs-material": 50,
}


@contextlib.contextmanager
def _chdir(path: Path) -> Generator[None, None, None]:
    """Temporarily change the working directory (sample hooks use relative paths)."""
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _ensure_to_pdf(project: Path, patch: Path) -> None:
    """Add the `to-pdf` plugin to a copied sample config, idempotently."""
    text = (project / "mkdocs.yml").read_text(encoding="utf-8")
    if "- to-pdf" in text:
        return

    patch_exe = shutil.which("patch")
    if patch_exe is None:
        pytest.skip("the `patch` program is required to build the samples")

    subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [patch_exe, "-p1", "-i", str(patch)],
        cwd=str(project),
        capture_output=True,
        check=True,
        text=True,
    )


def _build_sample(name: str) -> SimpleNamespace:
    """Build a sample site in a temporary directory, leaving submodules intact."""
    sample = SAMPLES / name
    source = sample / name
    if not (source / "mkdocs.yml").is_file():
        pytest.skip(f"sample submodule {name!r} is not checked out")

    root = Path(tempfile.mkdtemp(prefix=f"mkdocs-to-pdf-{name}-"))
    project = root / "project"
    project.mkdir()

    for entry in source.iterdir():
        if entry.name in {"mkdocs.yml", ".git"}:
            continue
        (project / entry.name).symlink_to(entry)

    shutil.copy2(source / "mkdocs.yml", project / "mkdocs.yml")
    _ensure_to_pdf(project, sample / "mkdocs-yml.patch")

    site_dir = root / "site"
    with _chdir(project):
        config = load_config(
            config_file=str(project / "mkdocs.yml"),
            docs_dir=str(project / "docs"),
            site_dir=str(site_dir),
        )
        build(config)

    return SimpleNamespace(
        site_dir=site_dir,
        pdf_path=site_dir / "pdf" / "document.pdf",
    )


@pytest.fixture(scope="session")
def built_sample_mkdocs() -> SimpleNamespace:
    """Build the `samples/mkdocs` site."""
    return _build_sample("mkdocs")


@pytest.fixture(scope="session")
def built_sample_mkdocs_material() -> SimpleNamespace:
    """Build the `samples/mkdocs-material` site."""
    return _build_sample("mkdocs-material")


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


_SAMPLES = [
    pytest.param("mkdocs", "built_sample_mkdocs", id="mkdocs"),
    pytest.param(
        "mkdocs-material",
        "built_sample_mkdocs_material",
        id="mkdocs-material",
    ),
]


@pytest.mark.parametrize(("name", "fixture"), _SAMPLES)
def test_sample_builds_to_pdf(
    request: pytest.FixtureRequest,
    name: str,
    fixture: str,
) -> None:
    """The sample builds to a PDF that is not truncated to a few pages."""
    sample = request.getfixturevalue(fixture)
    assert sample.pdf_path.is_file()
    assert sample.pdf_path.read_bytes().startswith(b"%PDF-")

    pages = len(PdfReader(str(sample.pdf_path)).pages)
    assert pages >= _PAGE_FLOORS[name], pages


@pytest.mark.parametrize(("name", "fixture"), _SAMPLES)
def test_sample_has_outline_and_links(
    request: pytest.FixtureRequest,
    name: str,
    fixture: str,
) -> None:
    """The sample PDF carries an outline, destinations and link annotations."""
    sample = request.getfixturevalue(fixture)
    reader = PdfReader(str(sample.pdf_path))

    assert _outline_titles(reader), name
    assert reader.named_destinations, name

    link_annotations = sum(
        1
        for page in reader.pages
        for annotation in page.get("/Annots") or []
        if annotation.get_object().get("/Subtype") == "/Link"
    )
    assert link_annotations > 0, name


@pytest.mark.parametrize(("name", "fixture"), _SAMPLES)
def test_sample_text_is_complete(
    request: pytest.FixtureRequest,
    name: str,
    fixture: str,
) -> None:
    """The extracted text is substantial, so content was not dropped."""
    sample = request.getfixturevalue(fixture)
    text = _pdf_text(PdfReader(str(sample.pdf_path)))
    assert len(text) > 20_000, name
