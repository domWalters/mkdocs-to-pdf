from _type_aliases import SoupFactory

from mkdocs_to_pdf.utils.linenums_util import convert_linenums_tables


def _highlight_table(*, line_spans: bool) -> str:
    """Build a Pygments-style `highlighttable`, with or without line spans."""
    code = (
        '<span id="__span-0-1">one\n</span><span id="__span-0-2">two\n</span>'
        if line_spans
        else "one\ntwo\n"
    )
    return (
        '<table class="highlighttable"><tr>'
        '<td class="linenos"><div class="linenodiv"><pre>1\n2</pre></div></td>'
        f'<td class="code"><div><pre><code>{code}</code></pre></div></td>'
        "</tr></table>"
    )


def test_convert_linenums_tables_marks_table(make_soup: SoupFactory) -> None:
    """A `linenums` table with per-line spans gets the counter class."""
    soup = make_soup(_highlight_table(line_spans=True))

    convert_linenums_tables(soup)

    table = soup.find("table")
    assert table is not None
    assert "linenums-counter" in table["class"]
    assert table.find("td", class_="linenos") is None


def test_convert_linenums_tables_keeps_table_without_line_spans(
    make_soup: SoupFactory,
) -> None:
    """A code table without per-line spans is left untouched."""
    soup = make_soup(_highlight_table(line_spans=False))

    convert_linenums_tables(soup)

    table = soup.find("table")
    assert table is not None
    assert "linenums-counter" not in (table.get("class") or [])
    assert table.find("td", class_="linenos") is not None


def test_convert_linenums_tables_without_tables(make_soup: SoupFactory) -> None:
    """Do nothing when there are no highlight tables."""
    soup = make_soup("<p>plain</p>")

    convert_linenums_tables(soup)

    assert soup.find("table") is None
