from _types import SoupFactory

from mkdocs_to_pdf.utils.iframe_util import convert_iframe


def test_convert_iframe_no_entries_is_noop(make_soup: SoupFactory) -> None:
    """Leave iframes untouched when no conversion entries are configured."""
    soup = make_soup('<iframe src="https://example.com/embed"></iframe>')

    convert_iframe(soup, [])

    assert soup.find("iframe") is not None


def test_convert_iframe_matching_entry(make_soup: SoupFactory) -> None:
    """Replace a matching iframe with a poster-image anchor."""
    soup = make_soup(
        '<iframe src="https://example.com/embed" style="height: 10px"></iframe>',
    )
    entries = [
        {
            "src": "https://example.com/embed",
            "img": "poster.png",
            "text": "Open",
        },
    ]

    convert_iframe(soup, entries)

    assert soup.find("iframe") is None
    anchor = soup.find("a", class_="converted-iframe")
    assert anchor is not None
    assert anchor["href"] == "https://example.com/embed"
    assert anchor["target"] == "_blank"
    assert anchor["style"] == "height: 10px"
    img = anchor.find("img")
    assert img is not None
    assert img["src"] == "poster.png"
    span = anchor.find("span")
    assert span is not None
    assert span.get_text() == "Open"


def test_convert_iframe_non_matching_entry(make_soup: SoupFactory) -> None:
    """Leave iframes whose `src` is not configured untouched."""
    soup = make_soup('<iframe src="https://example.com/embed"></iframe>')

    convert_iframe(soup, [{"src": "https://other.example/embed"}])

    assert soup.find("iframe") is not None
    assert soup.find("a", class_="converted-iframe") is None
