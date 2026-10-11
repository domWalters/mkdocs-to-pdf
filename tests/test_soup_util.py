from _type_aliases import SoupFactory

from mkdocs_to_pdf.utils.soup_util import clone_element


def test_clone_element_is_deep(make_soup: SoupFactory) -> None:
    """Mutating a clone must not affect the original element."""
    soup = make_soup('<div class="a"><span id="s">x</span></div>', body=False)

    original = soup.div
    assert original is not None
    clone = clone_element(original)
    clone["class"] = "b"
    clone_span = clone.find("span")
    assert clone_span is not None
    clone_span["id"] = "y"
    clone_span.string = "changed"

    original_span = original.find("span")
    assert original["class"] == ["a"]
    assert original_span is not None
    assert original_span["id"] == "s"
    assert original_span.get_text() == "x"


def test_clone_element_preserves_structure(make_soup: SoupFactory) -> None:
    """The clone keeps the element's name, attributes and children."""
    soup = make_soup('<div class="a"><span id="s">x</span></div>', body=False)

    original = soup.div
    assert original is not None
    clone = clone_element(original)

    assert clone.name == "div"
    assert clone["class"] == ["a"]
    clone_span = clone.find("span")
    assert clone_span is not None
    assert clone_span["id"] == "s"
    assert clone_span.get_text() == "x"
