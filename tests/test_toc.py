from _types import OptionsFactory, SoupFactory
from bs4 import BeautifulSoup

from mkdocs_to_pdf.toc import _inject_heading_order, make_indexes


def _ordered_headings(soup: BeautifulSoup) -> list[str]:
    """Return the numbering prefix for every heading carrying one."""
    result = []
    for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        order = h.find("span", class_="pdf-order")
        if order:
            result.append(order.get_text(strip=True))
    return result


def test_inject_heading_order_nests(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Number nested headings as a hierarchical outline."""
    soup = make_soup(
        "<h1 id='a'>A</h1><h2 id='a1'>A1</h2><h3 id='a11'>A11</h3><h1 id='b'>B</h1>",
    )

    _inject_heading_order(soup, make_options(ordered_chapter_level=3))

    assert _ordered_headings(soup) == ["1.", "1.1", "1.1.1", "2."]


def test_inject_heading_order_resets_lower_levels(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Reset deeper counters when a shallower heading is encountered."""
    soup = make_soup(
        "<h1 id='a'>A</h1>"
        "<h2 id='a1'>A1</h2>"
        "<h3 id='a11'>A11</h3>"
        "<h2 id='a2'>A2</h2>"
        "<h3 id='a21'>A21</h3>",
    )

    _inject_heading_order(soup, make_options(ordered_chapter_level=3))

    assert _ordered_headings(soup) == ["1.", "1.1", "1.1.1", "1.2", "1.2.1"]


def test_inject_heading_order_respects_level(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Do not number headings deeper than `ordered_chapter_level`."""
    soup = make_soup("<h1 id='a'>A</h1><h2 id='a1'>A1</h2><h3 id='a11'>A11</h3>")

    _inject_heading_order(soup, make_options(ordered_chapter_level=2))

    assert _ordered_headings(soup) == ["1.", "1.1"]


def test_inject_heading_order_level_zero_disables(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Skip numbering entirely when the configured level is zero."""
    soup = make_soup("<h1 id='a'>A</h1><h2 id='a1'>A1</h2>")

    _inject_heading_order(soup, make_options(ordered_chapter_level=0))

    assert _ordered_headings(soup) == []


def test_inject_heading_order_excludes_children(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Suppress child numbering under a heading listed in `excludes_children`."""
    soup = make_soup(
        "<h1 id='secret'>Secret</h1>"
        "<h2 id='secret-child'>Child</h2>"
        "<h1 id='open'>Open</h1>"
        "<h2 id='open-child'>Child</h2>",
    )

    _inject_heading_order(soup, make_options(excludes_children=["secret"]))

    # `excludes_children` suppresses numbering of a heading's *children*;
    # the excluded heading itself is still numbered.
    assert _ordered_headings(soup) == ["1.", "2.", "2.1"]


def test_make_indexes_builds_nested_toc(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Build a `doc-toc` article with nested lists for deeper headings."""
    soup = make_soup("<h1 id='a'>A</h1><h2 id='a1'>A1</h2><h3 id='a11'>A11</h3>")

    make_indexes(soup, make_options(toc_level=3))

    toc = soup.find("article", id="doc-toc")
    assert toc is not None
    title = toc.find("h1")
    assert title is not None
    assert title.get_text(strip=True) == "Table of contents"

    links = toc.find_all("a")
    assert [a["href"] for a in links] == ["#a", "#a1", "#a11"]

    outer = toc.find("ul")
    assert outer is not None
    assert len(outer.find_all("li", recursive=False)) == 1
    inner = outer.find("ul")
    assert inner is not None
    inner_link = inner.find("a")
    assert inner_link is not None
    assert inner_link["href"] == "#a1"


def test_make_indexes_toc_inserted_first(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Insert the table of contents before all other content."""
    soup = make_soup("<h1 id='a'>A</h1>")

    make_indexes(soup, make_options(toc_level=1))

    body = soup.body
    assert body is not None
    assert body.contents[0] is soup.find("article", id="doc-toc")


def test_make_indexes_respects_toc_level(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Only include headings up to `toc_level` in the table of contents."""
    soup = make_soup("<h1 id='a'>A</h1><h2 id='a1'>A1</h2><h3 id='a11'>A11</h3>")

    make_indexes(soup, make_options(toc_level=1))

    toc = soup.find("article", id="doc-toc")
    assert toc is not None
    links = toc.find_all("a")
    assert [a["href"] for a in links] == ["#a"]


def test_make_indexes_disabled_when_level_out_of_range(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Emit no table of contents when `toc_level` is out of range."""
    for level in (0, 7):
        soup = make_soup("<h1 id='a'>A</h1>")
        make_indexes(soup, make_options(toc_level=level))
        assert soup.find("article", id="doc-toc") is None


def test_inject_heading_order_skipped_level(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Number a heading even when an intermediate level is absent."""
    soup = make_soup("<h1 id='a'>A</h1><h3 id='c'>C</h3>")

    _inject_heading_order(soup, make_options(ordered_chapter_level=3))

    assert _ordered_headings(soup) == ["1.", "1.0.1"]


def test_inject_heading_order_exclusion_resets_on_new_parent(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Excluded descendants do not leak past a new top-level heading."""
    soup = make_soup(
        "<h1 id='a'>A</h1>"
        "<h2 id='a1'>A1</h2>"
        "<h3 id='a11'>A11</h3>"
        "<h1 id='b'>B</h1>"
        "<h3 id='b1'>B1</h3>",
    )

    _inject_heading_order(
        soup,
        make_options(ordered_chapter_level=3, excludes_children=["a1"]),
    )

    assert _ordered_headings(soup) == ["1.", "1.1", "2.", "2.0.1"]


def test_make_indexes_allows_skipped_levels(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Nest deeper headings under the nearest ancestor when a level is skipped."""
    soup = make_soup("<h1 id='a'>A</h1><h3 id='c'>C</h3><h4 id='d'>D</h4>")

    make_indexes(soup, make_options(toc_level=4))

    toc = soup.find("article", id="doc-toc")
    assert toc is not None
    outer = toc.find("ul")
    assert outer is not None

    h1_item = outer.find("li", recursive=False)
    assert h1_item is not None
    h1_link = h1_item.find("a")
    assert h1_link is not None
    assert h1_link["href"] == "#a"

    h3_list = h1_item.find("ul")
    assert h3_list is not None
    h3_item = h3_list.find("li", recursive=False)
    assert h3_item is not None
    h3_link = h3_item.find("a")
    assert h3_link is not None
    assert h3_link["href"] == "#c"

    h4_list = h3_item.find("ul")
    assert h4_list is not None
    h4_link = h4_list.find("a")
    assert h4_link is not None
    assert h4_link["href"] == "#d"


def test_make_indexes_omits_orphan_headings(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Skip headings that have no shallower heading to nest under."""
    soup = make_soup("<h3 id='c'>C</h3><h4 id='d'>D</h4>")

    make_indexes(soup, make_options(toc_level=4))

    toc = soup.find("article", id="doc-toc")
    assert toc is not None
    assert toc.find_all("a") == []


def test_make_indexes_excludes_children(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Omit the descendants of a heading listed in `excludes_children`."""
    soup = make_soup(
        "<h1 id='secret'>Secret</h1>"
        "<h2 id='secret-child'>Child</h2>"
        "<h1 id='open'>Open</h1>"
        "<h2 id='open-child'>Child</h2>",
    )

    make_indexes(soup, make_options(toc_level=3, excludes_children=["secret"]))

    toc = soup.find("article", id="doc-toc")
    assert toc is not None
    assert [a["href"] for a in toc.find_all("a")] == [
        "#secret",
        "#open",
        "#open-child",
    ]


def test_make_indexes_exclusion_resets_on_new_parent(
    make_options: OptionsFactory,
    make_soup: SoupFactory,
) -> None:
    """Excluded descendants do not leak past a new top-level heading."""
    soup = make_soup(
        "<h1 id='a'>A</h1>"
        "<h2 id='a1'>A1</h2>"
        "<h3 id='a11'>A11</h3>"
        "<h1 id='b'>B</h1>"
        "<h3 id='b1'>B1</h3>",
    )

    make_indexes(soup, make_options(toc_level=3, excludes_children=["a1"]))

    toc = soup.find("article", id="doc-toc")
    assert toc is not None
    assert [a["href"] for a in toc.find_all("a")] == ["#a", "#a1", "#b", "#b1"]
