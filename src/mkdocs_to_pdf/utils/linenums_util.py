"""Make `linenums` code blocks page-breakable while keeping their gutter."""

from logging import Logger

from bs4 import BeautifulSoup

# A single line gives no reliable per-line numbering; two or more is a `linenums`
# block for which the CSS counter can draw the gutter.
_MIN_LINE_SPANS = 2


def convert_linenums_tables(
    soup: BeautifulSoup,
    _logger: Logger | None = None,
) -> None:
    """
    Mark Pygments `linenums` tables so line numbers come from a CSS counter.

    Pygments renders `linenums` as a single-row `table.highlighttable` whose
    cells hold tall `<pre>` blocks. WeasyPrint cannot split that row, so an
    over-long code block drops everything that follows it (issue #62). Adding
    the `linenums-counter` class lets the print stylesheet lay the table out as
    blocks and draw the gutter with a CSS counter, so the block can break
    across pages while keeping its line numbers.

    The class is only added when per-line spans are available (`line_spans`
    must be enabled in `pymdownx.highlight`); otherwise the existing numbers
    are left untouched.

    Args:
        soup: DOM object of the document.
        _logger: Optional logger.

    """
    for table in soup.select("table.highlighttable"):
        code = table.find("code")
        if code is None:
            continue

        lines = code.find_all("span", recursive=False)
        if len(lines) < _MIN_LINE_SPANS:
            continue

        # Remove the separate line-number column: its numbers become dead links
        # once the counter draws the gutter.
        linenos = table.find("td", class_="linenos")
        if linenos is not None:
            linenos.decompose()

        classes = table.get("class")
        if isinstance(classes, list):
            classes.append("linenums-counter")
        else:
            table["class"] = "linenums-counter"
