#!/usr/bin/env python3

"""
MkDocs hook that publishes the ``tests/fixtures`` PDFs with the docs site.

Every fixture site is built during ``mkdocs build`` and its rendered PDF is
copied into the site's ``fixtures/`` directory. A generated "Example PDFs" page
links to each of them so the outputs are browsable on the documentation
website.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from mkdocs.commands.build import build
from mkdocs.config import load_config
from mkdocs.structure.files import File, Files

if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"

GALLERY_SRC_URI = "examples/example-pdfs.md"
PDF_DEST_DIR = "fixtures"

logger = logging.getLogger(__name__)


def discover_fixtures(fixtures_dir: Path) -> list[str]:
    """
    Return the sorted names of the fixture sites under a directory.

    Args:
        fixtures_dir: Directory that contains one sub-directory per fixture.

    Returns:
        The fixture names, sorted alphabetically.

    """
    return sorted(path.name for path in fixtures_dir.iterdir() if path.is_dir())


def relative_prefix(src_uri: str, *, use_directory_urls: bool) -> str:
    """
    Return the relative path from a page's output directory to the site root.

    Args:
        src_uri: The source URI of the page, relative to the docs directory.
        use_directory_urls: Whether MkDocs renders pages as ``page/index.html``.

    Returns:
        Zero or more ``../`` segments.

    """
    stem = PurePosixPath(src_uri).with_suffix("")
    depth = len(stem.parts) if use_directory_urls else len(stem.parts) - 1
    return "../" * max(depth, 0)


def render_gallery(
    fixture_names: list[str],
    *,
    src_uri: str,
    use_directory_urls: bool,
) -> str:
    """
    Render the "Example PDFs" page as Markdown linking to each fixture PDF.

    The links are raw HTML so MkDocs leaves them untouched: the PDFs are
    copied into the site after the build, so they are not known documentation
    files.

    Args:
        fixture_names: The fixture names to list.
        src_uri: The source URI of the generated page.
        use_directory_urls: Whether MkDocs renders pages as ``page/index.html``.

    Returns:
        The Markdown source for the gallery page.

    """
    prefix = relative_prefix(src_uri, use_directory_urls=use_directory_urls)
    lines = [
        "# Example PDFs",
        "",
        "Each PDF below is rendered from a site in `tests/fixtures/` during the",
        "documentation build, exercising a different feature of the plugin.",
        "",
        "| Fixture | PDF |",
        "| --- | --- |",
    ]
    for name in fixture_names:
        target = f"{prefix}{PDF_DEST_DIR}/{name}.pdf"
        lines.append(f'| `{name}` | <a href="{target}">{name}.pdf</a> |')
    lines.append("")
    return "\n".join(lines)


def build_fixture_pdf(name: str, dest_dir: Path) -> Path:
    """
    Build a fixture site and copy its PDF into the destination directory.

    Args:
        name: The fixture name, i.e. a directory under ``tests/fixtures``.
        dest_dir: Directory that receives ``<name>.pdf``.

    Returns:
        The path of the copied PDF.

    Raises:
        FileNotFoundError: If the fixture produced no PDF.

    """
    source = FIXTURES_DIR / name
    with tempfile.TemporaryDirectory(prefix=f"mkdocs-to-pdf-{name}-") as tmp:
        root = Path(tmp)
        project = root / "project"
        shutil.copytree(source, project)

        site_dir = root / "site"
        config = load_config(
            config_file=str(project / "mkdocs.yml"),
            docs_dir=str(project / "docs"),
            site_dir=str(site_dir),
        )
        build(config)

        pdfs = sorted(site_dir.glob("**/*.pdf"))
        if not pdfs:
            msg = f"fixture {name!r} produced no PDF"
            raise FileNotFoundError(msg)

        destination = dest_dir / f"{name}.pdf"
        shutil.copyfile(pdfs[0], destination)
        return destination


def on_files(files: Files, config: MkDocsConfig) -> Files:
    """Add the generated "Example PDFs" page to the documentation files."""
    content = render_gallery(
        discover_fixtures(FIXTURES_DIR),
        src_uri=GALLERY_SRC_URI,
        use_directory_urls=config.use_directory_urls,
    )
    files.append(File.generated(config, GALLERY_SRC_URI, content=content))
    return files


def on_post_build(config: MkDocsConfig) -> None:
    """Build every fixture and copy its PDF into the site directory."""
    dest_dir = Path(config.site_dir) / PDF_DEST_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)

    for name in discover_fixtures(FIXTURES_DIR):
        try:
            destination = build_fixture_pdf(name, dest_dir)
        except Exception:
            logger.exception("Failed to build fixture PDF %r", name)
            continue
        logger.info('Published fixture PDF "%s".', destination)


__all__ = [
    "GALLERY_SRC_URI",
    "PDF_DEST_DIR",
    "build_fixture_pdf",
    "discover_fixtures",
    "on_files",
    "on_post_build",
    "relative_prefix",
    "render_gallery",
]
