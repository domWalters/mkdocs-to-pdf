"""Tests for the QR code Jinja2 filter."""

import base64
from typing import TYPE_CHECKING, cast

from mkdocs_to_pdf.templates.filters.qrcode import QRCode

if TYPE_CHECKING:
    from mkdocs.config.base import Config

    from mkdocs_to_pdf.options import Options

SVG_PREFIX = "data:image/svg+xml;charset=utf-8;base64,"
PNG_PREFIX = "data:image/png;base64,"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _decode(data_uri: str) -> bytes:
    """Decode the base64 payload of a data URI."""
    return base64.b64decode(data_uri.split(",", 1)[1])


def _filter() -> QRCode:
    """Return a QR code filter with unused options/config stubs."""
    return QRCode(cast("Options", object()), cast("Config", object()))


def test_qrcode_returns_svg_data_uri() -> None:
    """Render a QR code as a base64 SVG data URI."""
    result = _filter()("hello world", format="SVG")

    assert result.startswith(SVG_PREFIX)
    assert b"<svg" in _decode(result)


def test_qrcode_defaults_to_svg() -> None:
    """Render a QR code as SVG when no format is given."""
    result = _filter()("hello world")

    assert result.startswith(SVG_PREFIX)


def test_qrcode_returns_png_data_uri() -> None:
    """Render a QR code as a base64 PNG data URI."""
    result = _filter()("hello world", format="PNG")

    assert result.startswith(PNG_PREFIX)
    assert _decode(result).startswith(PNG_SIGNATURE)


def test_qrcode_error_correction() -> None:
    """Render a QR code with a specific error-correction level."""
    result = _filter()("hello", error_correction="H")

    assert result.startswith(SVG_PREFIX)
