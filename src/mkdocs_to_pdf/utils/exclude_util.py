"""Remove HTML elements selected for exclusion from the PDF."""

from logging import Logger

from bs4 import BeautifulSoup


def remove_elements(
    soup: BeautifulSoup,
    selectors: list[str],
    logger: Logger | None = None,
) -> None:
    """
    Remove every element matching one of the configured CSS selectors.

    Args:
        soup: DOM object of the combined document.
        selectors: CSS selectors identifying elements to remove.
        logger: Optional logger.

    Raises:
        ValueError: If a selector is not valid CSS.

    """
    for selector in selectors:
        try:
            elements = soup.select(selector)
        except Exception as error:
            msg = f'Invalid exclude_elements selector "{selector}": {error}'
            raise ValueError(msg) from error

        if logger and not elements:
            logger.warning(
                'exclude_elements selector "%s" matched no elements.',
                selector,
            )
        if logger and elements:
            logger.debug(
                'Removed %s element(s) matching "%s".',
                len(elements),
                selector,
            )

        for element in elements:
            element.decompose()
