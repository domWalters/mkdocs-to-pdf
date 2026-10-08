from _types import SoupFactory

from mkdocs_to_pdf.utils.tabbed_set_util import wrap_tabbed_set_content


def test_wrap_tabbed_set_content(make_soup: SoupFactory) -> None:
    """Wrap each tab input and its content in a `tabbed-content--wrap` div."""
    soup = make_soup(
        '<div class="tabbed-set">'
        '<input type="radio" id="t1">'
        '<div class="tabbed-content">c1</div>'
        '<input type="radio" id="t2">'
        '<div class="tabbed-content">c2</div>'
        "</div>",
    )

    wrap_tabbed_set_content(soup)

    wraps = soup.select("div.tabbed-content--wrap")
    assert len(wraps) == 2
    for wrap in wraps:
        assert wrap.find("input") is not None


def test_wrap_opens_details(make_soup: SoupFactory) -> None:
    """Force `<details>` elements open so their content prints."""
    soup = make_soup("<details><summary>s</summary><p>body</p></details>")

    wrap_tabbed_set_content(soup)

    details = soup.find("details")
    assert details is not None
    assert not details["open"]


def test_wrap_tabbed_set_content_without_tabs(make_soup: SoupFactory) -> None:
    """Generate no wrappers when there are no tabbed sets."""
    soup = make_soup("<p>plain</p>")

    wrap_tabbed_set_content(soup)

    assert soup.select("div.tabbed-content--wrap") == []
