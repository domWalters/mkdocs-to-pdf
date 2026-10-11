from _type_aliases import SoupFactory

from mkdocs_to_pdf.preprocessor import get_combined
from mkdocs_to_pdf.preprocessor.links.util import (
    abs_asset_href,
    get_body_id,
    is_doc,
    rel_pdf_href,
    replace_asset_hrefs,
)


def test_is_doc() -> None:
    """Classify only relative `.html` hrefs as documents."""
    assert is_doc("page.html") is True
    assert is_doc("dir/page.html") is True
    assert is_doc("page.htm") is False
    assert is_doc("page.md") is False
    assert is_doc("image.png") is False
    assert is_doc("https://example.com/page.html") is False
    assert is_doc("/abs/page.html") is False


def test_rel_pdf_href() -> None:
    """Rewrite document links to their `.pdf` counterparts."""
    assert rel_pdf_href("page.html") == "page.pdf"
    assert rel_pdf_href("dir/page.html") == "dir/page.pdf"
    assert rel_pdf_href("#anchor") == "#anchor"
    assert rel_pdf_href("image.png") == "image.png"
    assert (
        rel_pdf_href("https://example.com/page.html") == "https://example.com/page.html"
    )


def test_abs_asset_href() -> None:
    """Resolve relative assets against the base URL only."""
    assert (
        abs_asset_href("img/a.png", "file:///site/doc/") == "file:///site/doc/img/a.png"
    )
    assert (
        abs_asset_href("https://cdn.example/a.png", "file:///site/doc/")
        == "https://cdn.example/a.png"
    )


def test_replace_asset_hrefs(make_soup: SoupFactory) -> None:
    """Make `link`/`src` asset references absolute."""
    soup = make_soup('<link href="css/a.css"><img src="img/a.png">', body=False)

    replace_asset_hrefs(soup, "file:///site/doc/")

    link = soup.find("link")
    assert link is not None
    assert link["href"] == "file:///site/doc/css/a.css"
    img = soup.find("img")
    assert img is not None
    assert img["src"] == "file:///site/doc/img/a.png"


def test_get_body_id() -> None:
    """Derive the body id from the page URL."""
    assert get_body_id("path/index.html") == "path/index:"
    assert get_body_id("page.html") == "page:"


def test_get_combined_transforms_links_and_ids(make_soup: SoupFactory) -> None:
    """Rewrite ids, document links, the body id and asset hrefs."""
    soup = make_soup(
        '<a href="page.html#h">p</a>'
        '<h1 id="sec">S</h1>'
        '<link href="css/a.css">'
        '<img src="img/a.png">',
    )

    get_combined(soup, base_url="file:///site/doc/", rel_url="doc/")

    anchor = soup.find("a")
    heading = soup.find("h1")
    link = soup.find("link")
    img = soup.find("img")
    body = soup.body
    assert anchor is not None
    assert heading is not None
    assert link is not None
    assert img is not None
    assert body is not None
    assert anchor["href"] == "#doc/page/:h"
    assert heading["id"] == "doc/:sec"
    assert body["id"] == "doc/:"
    assert link["href"] == "file:///site/doc/css/a.css"
    assert img["src"] == "file:///site/doc/img/a.png"


def test_get_combined_keeps_absolute_links(make_soup: SoupFactory) -> None:
    """Leave absolute and root-relative links untouched."""
    soup = make_soup(
        '<a href="https://example.com/page.html">e</a>'
        '<a href="/rooted/page.html">r</a>',
    )

    get_combined(soup, base_url="file:///site/doc/", rel_url="doc/")

    hrefs = [a["href"] for a in soup.find_all("a")]
    assert hrefs == ["https://example.com/page.html", "/rooted/page.html"]
