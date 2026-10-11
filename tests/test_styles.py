import re
from pathlib import Path

from _type_aliases import OptionsFactory, OptionsStub

from mkdocs_to_pdf.styles import _css_escape, style_for_print

# Viewport and container query units are not supported by WeasyPrint.
_UNSUPPORTED_UNITS = (
    "vh",
    "vw",
    "vmin",
    "vmax",
    "dvh",
    "dvw",
    "svh",
    "svw",
    "lvh",
    "lvw",
    "cqw",
    "cqh",
    "cqi",
    "cqb",
)


def test_css_escape_empty() -> None:
    """Return an empty string for empty input."""
    assert not _css_escape("")


def test_css_escape_single_quote() -> None:
    """Escape single quotes for use in a CSS string."""
    assert _css_escape("It's") == "It\\27s"


def test_css_escape_unescapes_html_entities() -> None:
    """Unescape HTML entities before emitting CSS."""
    assert _css_escape("Tom &amp; Jerry") == "Tom & Jerry"
    assert _css_escape("&copy; 2026") == "© 2026"


def test_style_for_print_avoids_new_unsupported_units(
    make_options: OptionsFactory,
) -> None:
    """
    Guard against new viewport/container units in the print styles.

    WeasyPrint silently ignores these units, which caused the cover layout
    regressions in issue #42. ``vh`` is still emitted by the cover stylesheet
    (issue #42); this test catches any *new* unsupported unit.
    """
    options = make_options(
        author="Author",
        copyright="Copyright",
        cover_title="Title",
        cover_subtitle="Subtitle",
        custom_template_path="/nonexistent",
    )
    css = style_for_print(options)

    found = {unit for unit in _UNSUPPORTED_UNITS if re.search(rf"[0-9]{unit}\b", css)}
    unexpected = sorted(found - {"vh"})
    assert not unexpected, f"unsupported units in print styles: {unexpected}"


def _options(make_options: OptionsFactory, tmp_path: Path) -> OptionsStub:
    """Return options with a cover-less `custom_template_path` of `tmp_path`."""
    return make_options(
        author="Author",
        copyright="Copyright",
        cover_title="Title",
        cover_subtitle="Subtitle",
        custom_template_path=str(tmp_path),
    )


def test_style_for_print_compiles_custom_scss(
    make_options: OptionsFactory,
    tmp_path: Path,
) -> None:
    """A `styles.scss` is compiled with SCSS features and appended."""
    (tmp_path / "styles.scss").write_text(
        "$accent: #ff00ff;\narticle h1 { color: $accent !important; }\n",
        encoding="utf-8",
    )

    css = style_for_print(_options(make_options, tmp_path))

    assert "article h1" in css
    assert "color: #ff00ff !important;" in css


def test_style_for_print_custom_styles_come_last(
    make_options: OptionsFactory,
    tmp_path: Path,
) -> None:
    """Custom rules are appended after the built-in styles, so they win."""
    (tmp_path / "styles.scss").write_text(
        "article h1 { color: #ff00ff !important; }\n",
        encoding="utf-8",
    )

    css = style_for_print(_options(make_options, tmp_path))

    assert css.index("color: #ff00ff") > css.index("@page")


def test_style_for_print_ignores_missing_custom_styles(
    make_options: OptionsFactory,
    tmp_path: Path,
) -> None:
    """A directory without a `styles.scss` adds no custom rules."""
    empty = style_for_print(_options(make_options, tmp_path))

    missing = style_for_print(
        make_options(
            author="Author",
            copyright="Copyright",
            cover_title="Title",
            cover_subtitle="Subtitle",
            custom_template_path="/nonexistent",
        ),
    )

    assert empty == missing
