"""Cover page generation."""

from bs4 import BeautifulSoup

from .options import Options


def make_cover(soup: BeautifulSoup, options: Options) -> None:
    """
    Generate the cover and/or back cover pages.

    Args:
        soup: Target document.
        options: The project options.

    """
    if options.cover:
        _make_cover(soup, options)

    if options.back_cover:
        _make_back_cover(soup, options)


def _make_cover(soup: BeautifulSoup, options: Options) -> None:
    keywords = options.template.keywords
    template = options.template.select(["cover", "default_cover"])

    options.logger.info('Generating a cover page with "%s" ...', template.name)
    try:
        soup_template = BeautifulSoup(template.render(keywords), "html.parser")
    except Exception:
        options.logger.exception("Failed to generate the cover page")
        return

    if soup.body is None:
        options.logger.error("Failed to insert the cover page")
        return

    soup.body.insert(0, soup_template)


def _make_back_cover(soup: BeautifulSoup, options: Options) -> None:
    keywords = dict(options.template.keywords)
    if keywords.get("back_cover_qrcode") and not options.template.qrcode_available:
        options.logger.warning(
            "`back_cover_qrcode` is enabled but the `qrcode` package is not "
            "installed; generating the back cover without a QR code.",
        )
        keywords["back_cover_qrcode"] = False

    if keywords.get("back_cover_barcode") and not options.template.barcode_available:
        options.logger.warning(
            "`back_cover_barcode` is enabled but the `python-barcode` package "
            "is not installed; generating the back cover without a barcode.",
        )
        keywords["back_cover_barcode"] = False

    template = options.template.select(["back_cover", "default_back_cover"])

    options.logger.info('Generating a back cover page with "%s" ...', template.name)
    try:
        soup_template = BeautifulSoup(template.render(keywords), "html.parser")
    except Exception:
        options.logger.exception("Failed to generate the back cover page")
        return

    if soup.body is None:
        options.logger.error("Failed to insert the back cover page")
        return

    soup.body.append(soup_template)
