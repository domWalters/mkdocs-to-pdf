"""Make tabbed and collapsible content printable."""

import itertools
from logging import Logger

from bs4 import BeautifulSoup, Tag


def wrap_tabbed_set_content(
    soup: BeautifulSoup,
    _logger: Logger | None = None,
) -> None:
    """
    Wrap tabbed content and force details elements open.

    Args:
        soup: DOM object of the page.
        _logger: Optional logger.

    """
    for ts in soup.select("div.tabbed-set"):
        for radio in ts.select("input"):
            els = list(
                itertools.takewhile(
                    lambda x: not (isinstance(x, Tag) and x.name == "input"),
                    radio.next_siblings,
                ),
            )
            wrapper = soup.new_tag("div", attrs={"class": "tabbed-content--wrap"})
            radio.wrap(wrapper)
            for tag in els:
                wrapper.append(tag)

    for d in soup.select("details"):
        d["open"] = ""
