"""End-to-end tests for customising the PDF style with `styles.scss`."""

import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup
from mkdocs.commands.build import build
from mkdocs.config import load_config

_SCSS = """
$custom-accent: {{ pdf_accent }};

article h1 {
  color: $custom-accent !important;
}
"""


@pytest.fixture
def built_custom_style(tmp_path: Path) -> SimpleNamespace:
    """Build a site whose `custom_template_path` provides `styles.scss`."""
    project = tmp_path / "project"
    docs = project / "docs"
    stylesheets = project / "stylesheets"
    docs.mkdir(parents=True)
    stylesheets.mkdir()

    (docs / "index.md").write_text(
        "# Custom Style\n\nBody text.\n",
        encoding="utf-8",
    )
    (stylesheets / "styles.scss").write_text(_SCSS, encoding="utf-8")
    (project / "mkdocs.yml").write_text(
        textwrap.dedent(
            f"""
            site_name: Custom Style

            theme:
              name: mkdocs

            plugins:
              - to-pdf:
                  custom_template_path: {stylesheets}
                  html_path: single.html
                  output_path: pdf/document.pdf

            extra:
              pdf_accent: "#ff00ff"

            site_url: ""
            use_directory_urls: false
            """,
        ).strip(),
        encoding="utf-8",
    )

    site_dir = tmp_path / "site"
    config = load_config(
        config_file=str(project / "mkdocs.yml"),
        docs_dir=str(docs),
        site_dir=str(site_dir),
    )
    build(config)

    return SimpleNamespace(
        html_path=site_dir / "single.html",
        pdf_path=site_dir / "pdf" / "document.pdf",
    )


def _styles(soup: BeautifulSoup) -> str:
    """Return the contents of every `<style>` tag, joined."""
    return "\n".join(tag.get_text() for tag in soup.find_all("style"))


def test_custom_style_build_succeeds(built_custom_style: SimpleNamespace) -> None:
    """A site with a custom `styles.scss` builds HTML and a PDF."""
    assert built_custom_style.html_path.is_file()
    assert built_custom_style.pdf_path.is_file()
    assert built_custom_style.pdf_path.read_bytes().startswith(b"%PDF-")


def test_custom_style_scss_is_compiled_into_html(
    built_custom_style: SimpleNamespace,
) -> None:
    """The custom SCSS is compiled (variables resolved) into the stylesheet."""
    soup = BeautifulSoup(
        built_custom_style.html_path.read_text(encoding="utf-8"),
        "html.parser",
    )
    assert "article h1" in _styles(soup)
    assert "color: #ff00ff !important;" in _styles(soup)


def test_custom_style_uses_extra_variables(
    built_custom_style: SimpleNamespace,
) -> None:
    """`extra` variables are available as Jinja2 variables in `styles.scss`."""
    styles = _styles(
        BeautifulSoup(
            built_custom_style.html_path.read_text(encoding="utf-8"),
            "html.parser",
        ),
    )
    assert "{{ pdf_accent }}" not in styles
