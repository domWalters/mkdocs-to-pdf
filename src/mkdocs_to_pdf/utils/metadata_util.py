"""Set the PDF document metadata on the combined HTML."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    import pydyf
    from bs4 import BeautifulSoup
    from weasyprint.document import Document

_PACKAGE = "mkdocs-to-pdf"


def _package_version() -> str | None:
    """Return the installed package version, if it can be determined."""
    try:
        return version(_PACKAGE)
    except PackageNotFoundError:
        return None


def _creator() -> str:
    """Return the `Creator` string, including the version when available."""
    package_version = _package_version()
    return f"{_PACKAGE} {package_version}" if package_version else _PACKAGE


def _producer_prefix() -> str:
    """Return the `mkdocs-to-pdf ...` prefix for the `Producer`."""
    package_version = _package_version()
    return f"{_PACKAGE} {package_version}, " if package_version else f"{_PACKAGE}, "


def _set_meta(soup: BeautifulSoup, name: str, content: str) -> None:
    """
    Replace, or insert, a single `<meta name=...>` tag in the document head.

    Existing tags with the same name are removed so the document carries a
    single authoritative value. An empty `content` removes the tag entirely.

    Args:
        soup: The combined document.
        name: The `name` attribute of the meta tag.
        content: The `content` attribute of the meta tag.

    """
    head = soup.head
    if head is None:
        return

    for existing in head.find_all("meta", attrs={"name": name}):
        existing.decompose()

    if content:
        head.append(soup.new_tag("meta", attrs={"name": name, "content": content}))


def set_pdf_metadata(
    soup: BeautifulSoup,
    *,
    author: str,
    description: str,
    keywords: str,
    created: datetime,
) -> None:
    """
    Populate the metadata that WeasyPrint writes into the PDF.

    WeasyPrint reads the document author, subject, keywords, creator and
    dates from the HTML `<meta>` tags, so the combined document has to carry
    them explicitly rather than relying on the theme templates.

    Args:
        soup: The combined document.
        author: The document author (`Author`).
        description: The document summary (`Subject`).
        keywords: Comma-separated keywords (`Keywords`).
        created: The document creation and modification date.

    """
    _set_meta(soup, "author", author)
    _set_meta(soup, "description", description)
    _set_meta(soup, "keywords", keywords)
    _set_meta(soup, "generator", _creator())
    _set_meta(soup, "dcterms.created", created.isoformat())
    _set_meta(soup, "dcterms.modified", created.isoformat())


def prepend_producer(document: Document, pdf: pydyf.PDF) -> None:
    """
    Prefix the `Producer` of a rendered PDF with `mkdocs-to-pdf <version>`.

    WeasyPrint always writes `WeasyPrint <version>` as the `Producer` and
    offers no HTML hook for it. This is passed as the `finisher` callback of
    :meth:`weasyprint.document.Document.write_pdf`, which runs after the
    metadata is set and before the trailer is written.

    Args:
        document: The rendered WeasyPrint document (unused).
        pdf: The pydyf PDF object being written.

    """
    del document
    producer = pdf.info.get("Producer")
    if producer is None:
        return
    producer.string = f"{_producer_prefix()}{producer.string}"
