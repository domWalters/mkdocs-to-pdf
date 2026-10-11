from datetime import UTC, datetime
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from _type_aliases import SoupFactory
from bs4 import BeautifulSoup, Tag

from mkdocs_to_pdf.utils.metadata_util import prepend_producer, set_pdf_metadata

if TYPE_CHECKING:
    import pydyf
    from weasyprint.document import Document


def _head(soup: BeautifulSoup) -> Tag:
    """Return the document head, which the tests always create."""
    head = soup.head
    assert head is not None
    return head


def _meta(soup: BeautifulSoup, name: str) -> Tag | None:
    """Return the single meta tag with the given name, if any."""
    return _head(soup).find("meta", attrs={"name": name})


def test_set_pdf_metadata_sets_all_fields(make_soup: SoupFactory) -> None:
    """The author, subject, keywords, creator and dates are written."""
    soup = make_soup("<html><head></head><body></body></html>", body=False)
    created = datetime(2026, 2, 25, 12, 30, 0, tzinfo=UTC)

    set_pdf_metadata(
        soup,
        author="Michał Czyżewski",
        description="A user manual",
        keywords="manual, pdf, mkdocs",
        created=created,
    )

    author = _meta(soup, "author")
    assert author is not None
    assert author["content"] == "Michał Czyżewski"

    description = _meta(soup, "description")
    assert description is not None
    assert description["content"] == "A user manual"

    keywords = _meta(soup, "keywords")
    assert keywords is not None
    assert keywords["content"] == "manual, pdf, mkdocs"

    generator = _meta(soup, "generator")
    assert generator is not None
    assert str(generator["content"]).startswith("mkdocs-to-pdf")

    created_meta = _meta(soup, "dcterms.created")
    assert created_meta is not None
    assert created_meta["content"] == created.isoformat()

    modified_meta = _meta(soup, "dcterms.modified")
    assert modified_meta is not None
    assert modified_meta["content"] == created.isoformat()


def test_set_pdf_metadata_replaces_existing_meta(make_soup: SoupFactory) -> None:
    """Theme-provided metadata is replaced instead of duplicated."""
    soup = make_soup(
        "<html><head>"
        '<meta name="author" content="Theme Author">'
        '<meta name="description" content="None">'
        '<meta name="generator" content="mkdocs-1.6.1">'
        "</head><body></body></html>",
        body=False,
    )

    set_pdf_metadata(
        soup,
        author="Plugin Author",
        description="Plugin description",
        keywords="",
        created=datetime(2026, 2, 25, tzinfo=UTC),
    )

    for name, expected in (
        ("author", "Plugin Author"),
        ("description", "Plugin description"),
    ):
        tags = _head(soup).find_all("meta", attrs={"name": name})
        assert len(tags) == 1
        assert tags[0]["content"] == expected

    generator = _meta(soup, "generator")
    assert generator is not None
    assert str(generator["content"]).startswith("mkdocs-to-pdf")


def test_set_pdf_metadata_skips_empty_values(make_soup: SoupFactory) -> None:
    """Empty values remove the corresponding meta tags."""
    soup = make_soup(
        '<html><head><meta name="description" content="None"></head>'
        "<body></body></html>",
        body=False,
    )

    set_pdf_metadata(
        soup,
        author="",
        description="",
        keywords="",
        created=datetime(2026, 2, 25, tzinfo=UTC),
    )

    for name in ("author", "description", "keywords"):
        assert _meta(soup, name) is None


def test_prepend_producer_prefixes_weasyprint() -> None:
    """The WeasyPrint producer is prefixed with `mkdocs-to-pdf <version>`, ."""
    producer = SimpleNamespace(string="WeasyPrint 62.3")
    pdf = SimpleNamespace(info={"Producer": producer})

    prepend_producer(cast("Document", SimpleNamespace()), cast("pydyf.PDF", pdf))

    assert producer.string.startswith("mkdocs-to-pdf ")
    assert producer.string.endswith(", WeasyPrint 62.3")


def test_prepend_producer_without_producer() -> None:
    """A PDF without a producer is left untouched."""
    pdf = SimpleNamespace(info={})

    prepend_producer(cast("Document", SimpleNamespace()), cast("pydyf.PDF", pdf))

    assert pdf.info == {}
