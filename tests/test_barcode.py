"""Tests for the barcode Jinja2 filter."""

import base64
from typing import TYPE_CHECKING, cast

from mkdocs_to_pdf.templates.filters.barcode import Barcode

if TYPE_CHECKING:
    from mkdocs.config.base import Config

    from mkdocs_to_pdf.options import Options

DATA_URI_PREFIX = "data:image/svg+xml;charset=utf-8;base64,"


def _decode(data_uri: str) -> bytes:
    """Decode the base64 payload of a data URI."""
    return base64.b64decode(data_uri.split(",", 1)[1])


def _filter() -> Barcode:
    """Return a barcode filter with unused options/config stubs."""
    return Barcode(cast("Options", object()), cast("Config", object()))


def test_barcode_returns_svg_data_uri() -> None:
    """Render a barcode as a base64 SVG data URI."""
    result = _filter()("1234567890", "code39")

    assert result.startswith(DATA_URI_PREFIX)
    assert b"<svg" in _decode(result)


def test_barcode_supports_multiple_kinds() -> None:
    """Render different barcode types."""
    result = _filter()("ABC-123", "code128")

    assert result.startswith(DATA_URI_PREFIX)
    assert b"<svg" in _decode(result)


def test_barcode_passes_options_through() -> None:
    """Forward extra options to the barcode class constructor."""
    result = _filter()("1234567890", "code39", add_checksum=False)

    assert result.startswith(DATA_URI_PREFIX)
