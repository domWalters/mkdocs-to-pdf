import re

from _type_aliases import OptionsFactory

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
