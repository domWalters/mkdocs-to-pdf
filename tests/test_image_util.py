import logging

from _type_aliases import SoupFactory

from mkdocs_to_pdf.utils.image_util import (
    _convert_dimension,
    _parse_style,
    fix_image_alignment,
    images_size_to_half_in,
    unwrap_image_links,
)

logger = logging.getLogger("mkdocs_to_pdf.test")


def test_fix_image_alignment_left(make_soup: SoupFactory) -> None:
    """Convert `align="left"` into float styles."""
    soup = make_soup('<img src="a.png" align="left">')

    fix_image_alignment(soup, logger)

    img = soup.img
    assert img is not None
    assert "align" not in img.attrs
    assert "float: left;" in img["style"]
    assert "padding-right: 1rem;" in img["style"]
    assert "padding-bottom: 0.5rem;" in img["style"]


def test_fix_image_alignment_right(make_soup: SoupFactory) -> None:
    """Convert `align="right"` into float styles."""
    soup = make_soup('<img src="a.png" align="right">')

    fix_image_alignment(soup, logger)

    img = soup.img
    assert img is not None
    assert "align" not in img.attrs
    assert "float: right;" in img["style"]
    assert "padding-left: 1rem;" in img["style"]


def test_fix_image_alignment_moves_numeric_dimensions_to_style(
    make_soup: SoupFactory,
) -> None:
    """Move numeric `width`/`height` attributes into inline styles."""
    soup = make_soup('<img src="a.png" width="80" height="40">')

    fix_image_alignment(soup, logger)

    img = soup.img
    assert img is not None
    assert "width" not in img.attrs
    assert "height" not in img.attrs
    assert "width: 80px;" in img["style"]
    assert "height: 40px;" in img["style"]


def test_fix_image_alignment_keeps_unit_dimensions(make_soup: SoupFactory) -> None:
    """Preserve dimensions that already carry a unit."""
    soup = make_soup('<img src="a.png" width="50%">')

    fix_image_alignment(soup, logger)

    img = soup.img
    assert img is not None
    assert "width: 50%;" in img["style"]


def test_fix_image_alignment_strips_trailing_commas(make_soup: SoupFactory) -> None:
    """Strip stray trailing commas from parsed style values."""
    soup = make_soup('<img src="a.png" style="width: 80px,;">')

    fix_image_alignment(soup, logger)

    img = soup.img
    assert img is not None
    assert img["style"] == "width: 80px;"


def test_fix_image_alignment_skips_twemoji(make_soup: SoupFactory) -> None:
    """Leave twemoji `<img>` elements untouched."""
    soup = make_soup('<img class="twemoji" src="a.png" align="left">')

    fix_image_alignment(soup, logger)

    img = soup.img
    assert img is not None
    assert img["align"] == "left"


def test_images_size_to_half_in(make_soup: SoupFactory) -> None:
    """Halve image dimensions and padding inside a section."""
    soup = make_soup(
        '<section><img style="width: 100px; height: 40px;"></section>',
        body=False,
    )

    section = soup.section
    assert section is not None
    images_size_to_half_in(section)

    img = soup.img
    assert img is not None
    style = str(img["style"])
    assert "width: 50.0px;" in style
    assert "height: 20.0px;" in style


def test_images_size_to_half_in_bare_number(make_soup: SoupFactory) -> None:
    """Halve a unit-less dimension without losing the last digit."""
    soup = make_soup(
        '<section><img style="width: 100;"></section>',
        body=False,
    )

    section = soup.section
    assert section is not None
    images_size_to_half_in(section)

    img = soup.img
    assert img is not None
    assert str(img["style"]) == "width: 50.0;"


def test_unwrap_image_links_removes_lightbox_anchor(
    make_soup: SoupFactory,
) -> None:
    """Drop an anchor whose only content is a linked image asset."""
    soup = make_soup(
        '<a class="glightbox" href="image.png"><img src="image.png"></a>',
    )

    unwrap_image_links(soup, logger)

    assert soup.find("a") is None
    assert soup.find("img") is not None


def test_unwrap_image_links_keeps_anchor_with_text(make_soup: SoupFactory) -> None:
    """Keep anchors that carry text alongside the image."""
    soup = make_soup('<a href="image.png"><img src="image.png">caption</a>')

    unwrap_image_links(soup, logger)

    assert soup.find("a") is not None


def test_unwrap_image_links_keeps_document_links(make_soup: SoupFactory) -> None:
    """Keep anchors that link an image to another page."""
    soup = make_soup('<a href="page.html"><img src="thumb.png"></a>')

    unwrap_image_links(soup, logger)

    assert soup.find("a") is not None


def test_unwrap_image_links_ignores_multiple_images(make_soup: SoupFactory) -> None:
    """Keep anchors that wrap more than one element."""
    soup = make_soup(
        '<a href="image.png"><img src="a.png"><img src="b.png"></a>',
    )

    unwrap_image_links(soup, logger)

    assert soup.find("a") is not None


def test_parse_style() -> None:
    """Parse an inline style string into a mapping."""
    assert _parse_style("") == {}
    assert _parse_style("width: 80px; float: left;") == {
        "width": "80px",
        "float": "left",
    }


def test_convert_dimension() -> None:
    """Append `px` to bare numeric dimensions and keep units otherwise."""
    assert _convert_dimension("80") == "80px"
    assert _convert_dimension("50%") == "50%"
    assert _convert_dimension("3rem") == "3rem"
