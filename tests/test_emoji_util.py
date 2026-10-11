import logging

import pytest
from _type_aliases import SoupFactory

from mkdocs_to_pdf.utils.emoji_util import _parse_view_box, fix_twemoji


def test_fix_twemoji_replaces_svg_with_img(make_soup: SoupFactory) -> None:
    """Replace twemoji SVGs with base64 data-URI images."""
    soup = make_soup(
        '<span class="twemoji"><svg viewBox="0 0 24 24"><path d="M0 0"/></svg></span>',
    )

    fix_twemoji(soup)

    assert soup.find("svg") is None
    img = soup.find("img", class_="converted-twemoji")
    assert img is not None
    src = str(img["src"])
    assert src.startswith("data:image/svg+xml;charset=utf-8;base64,")


def test_fix_twemoji_bad_viewbox_warns_and_keeps_svg(
    make_soup: SoupFactory,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Warn and keep the SVG when its viewBox cannot be parsed."""
    logger = logging.getLogger("mkdocs_to_pdf.test")
    soup = make_soup('<span class="twemoji"><svg viewBox="not-a-box"></svg></span>')

    with caplog.at_level(logging.WARNING, logger="mkdocs_to_pdf.test"):
        fix_twemoji(soup, logger)

    assert soup.find("svg") is not None
    assert "Failed to convert SVG" in caplog.text


def test_parse_view_box() -> None:
    """Parse an SVG viewBox into its four numeric components."""
    positive = _parse_view_box("0 0 24 24")
    negative = _parse_view_box("1.5 -2 10 20")
    assert positive == (0.0, 0.0, 24.0, 24.0)
    assert negative == (1.5, -2.0, 10.0, 20.0)
