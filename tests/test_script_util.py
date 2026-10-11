"""Unit tests for the script collection helper (issue #85)."""

from pathlib import Path

from _type_aliases import SoupFactory
from bs4 import BeautifulSoup

from mkdocs_to_pdf.utils.script_util import collect_page_scripts


def _soup_with_scripts(make_soup: SoupFactory, body: str) -> BeautifulSoup:
    """Wrap body markup (including a head script) in a full document."""
    return make_soup(f"<head><script src='head.js'></script></head>{body}")


def test_collect_local_script_becomes_file_url(
    make_soup: SoupFactory,
    tmp_path: Path,
) -> None:
    """A local script is resolved to a loadable `file://` URL."""
    (tmp_path / "javascripts").mkdir()
    (tmp_path / "javascripts" / "mathjax.js").write_text("x", encoding="utf-8")

    soup = _soup_with_scripts(
        make_soup,
        '<body><script src="javascripts/mathjax.js"></script></body>',
    )
    scripts, _ = collect_page_scripts(soup, tmp_path)

    assert len(scripts) == 1
    src = str(scripts[0]["src"])
    assert src.startswith("file://")
    assert src.endswith("javascripts/mathjax.js")


def test_collect_remote_and_protocol_relative_kept(
    make_soup: SoupFactory,
    tmp_path: Path,
) -> None:
    """Remote and protocol-relative sources are kept unchanged."""
    soup = _soup_with_scripts(
        make_soup,
        (
            '<body><script src="https://example.com/a.js"></script>'
            '<script src="//example.com/b.js"></script></body>'
        ),
    )
    scripts, _ = collect_page_scripts(soup, tmp_path)

    assert [str(s["src"]) for s in scripts] == [
        "https://example.com/a.js",
        "//example.com/b.js",
    ]


def test_collect_existing_file_url_kept(
    make_soup: SoupFactory,
    tmp_path: Path,
) -> None:
    """An already-absolute `file://` source is kept when the file exists."""
    target = tmp_path / "bundle.js"
    target.write_text("x", encoding="utf-8")

    soup = _soup_with_scripts(
        make_soup,
        f'<body><script src="{target.as_uri()}"></script></body>',
    )
    scripts, _ = collect_page_scripts(soup, tmp_path)

    assert [str(s["src"]) for s in scripts] == [target.as_uri()]


def test_collect_missing_scripts_dropped(
    make_soup: SoupFactory,
    tmp_path: Path,
) -> None:
    """Missing local and `file://` sources are dropped."""
    missing = (tmp_path / "nope.js").as_uri()
    body = (
        f'<body><script src="nope.js"></script><script src="{missing}"></script></body>'
    )
    soup = _soup_with_scripts(make_soup, body)
    scripts, _ = collect_page_scripts(soup, tmp_path)

    assert scripts == []


def test_collect_inline_scripts_joined_and_head_ignored(
    make_soup: SoupFactory,
    tmp_path: Path,
) -> None:
    """Inline body scripts are joined; head scripts are not collected."""
    soup = _soup_with_scripts(
        make_soup,
        "<body><script>a()</script><script>b()</script></body>",
    )
    scripts, inline = collect_page_scripts(soup, tmp_path)

    assert scripts == []
    assert inline == "a();b()"
