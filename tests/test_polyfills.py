"""Guard the committed ``material-polyfills`` assets against build regressions."""

import re
from pathlib import Path

_CSS = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "mkdocs_to_pdf"
    / "themes"
    / "material-polyfills.css"
)


def test_polyfills_css_keeps_shorthand_values() -> None:
    """
    Multi-value shorthands survive minification.

    Webpack 5.111's built-in CSS minifier (``experiments.css``) collapses
    ``border-width: a b c d`` into invalid CSS (``a.b.c``), which WeasyPrint
    silently drops. This guards against that regression (issue #70).
    """
    match = re.search(r"border-width:([^;}]+)", _CSS.read_text(encoding="utf-8"))

    assert match is not None
    assert len(match.group(1).split()) == 4


def test_polyfills_css_svg_data_uris_are_encoded() -> None:
    """
    Inline SVG data URIs must not contain a literal ``#``.

    A literal ``#`` starts a URL fragment, so WeasyPrint's URL parser raises on
    the truncated data URI and aborts the whole PDF build. Inline SVG fills
    must be percent-encoded (``%23``); this guards against a regression when
    the ``postcss-inline-svg``/``postcss-svgo`` pipeline is upgraded (#70).
    """
    css = _CSS.read_text(encoding="utf-8")
    uris = re.findall(r"data:image/svg\+xml;charset=utf-8,(.*?)</svg>", css)

    assert uris
    for uri in uris:
        assert "#" not in uri
