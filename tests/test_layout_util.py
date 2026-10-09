import logging

import pytest
from _type_aliases import SoupFactory

from mkdocs_to_pdf.utils.layout_util import convert_for_two_columns


def test_two_columns_level_zero_is_noop(make_soup: SoupFactory) -> None:
    """Do nothing when the two-column level is disabled."""
    soup = make_soup("<h3>A</h3><p>a</p>")

    convert_for_two_columns(soup, 0)

    assert soup.find("section", class_="two-columns") is None


def test_two_columns_unsupported_level_warns(
    make_soup: SoupFactory,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Warn and do nothing for levels other than zero or three."""
    logger = logging.getLogger("mkdocs_to_pdf.test")
    soup = make_soup("<h3>A</h3><p>a</p>")

    with caplog.at_level(logging.WARNING, logger="mkdocs_to_pdf.test"):
        convert_for_two_columns(soup, 2, logger)

    assert soup.find("section", class_="two-columns") is None
    assert "only support" in caplog.text


def test_two_columns_level_three_wraps_sections(make_soup: SoupFactory) -> None:
    """Wrap each level-three heading and its content in a two-column section."""
    soup = make_soup(
        "<h1>Top</h1><h3>A</h3><p>a</p><h3>B</h3><p>b</p><h2>Stop</h2><p>c</p>",
    )

    convert_for_two_columns(soup, 3)

    sections = soup.find_all("section", class_="two-columns")
    assert len(sections) == 1

    section = sections[0]
    assert [h.get_text() for h in section.find_all("h3")] == ["A", "B"]
    assert [p.get_text() for p in section.find_all("p")] == ["a", "b"]
    # content after the next h1/h2 stays outside the section.
    stop = soup.find("h2")
    assert stop is not None
    trailing = stop.find_next_sibling("p")
    assert trailing is not None
    assert trailing.get_text() == "c"
