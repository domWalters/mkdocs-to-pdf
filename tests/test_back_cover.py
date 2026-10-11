"""Tests for the back cover and its optional QR code and barcode."""

from pathlib import Path
from types import SimpleNamespace

import jinja2
from bs4 import BeautifulSoup

TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "mkdocs_to_pdf"
    / "templates"
    / "default_back_cover.html.j2"
)


def _fake_qrcode(value: str, **_: object) -> str:
    """Stand-in for the real QR filter, encoding the value verbatim."""
    return f"QR::{value}"


def _fake_barcode(value: str, kind: str, **_: object) -> str:
    """Stand-in for the real barcode filter."""
    return f"BAR::{kind}::{value}"


def _render(**keywords: object) -> str:
    """Render the default back-cover template with the given keywords."""
    env = jinja2.Environment(autoescape=True, lstrip_blocks=True, trim_blocks=True)
    env.filters["qrcode"] = _fake_qrcode
    env.filters["barcode"] = _fake_barcode
    template = env.from_string(TEMPLATE.read_text(encoding="utf-8"))
    return template.render(**keywords)


def test_back_cover_qrcode_disabled_by_default() -> None:
    """No QR code when `back_cover_qrcode` is false."""
    html = _render(back_cover_qrcode=False, site_url="https://example.com")
    assert "qrcode" not in html


def test_back_cover_qrcode_falls_back_to_site_url() -> None:
    """Fall back to `site_url` when no explicit QR URL is set."""
    html = _render(
        back_cover_qrcode=True,
        back_cover_qr_url="",
        site_url="https://example.com",
    )
    assert "QR::https://example.com" in html


def test_back_cover_qrcode_prefers_explicit_url() -> None:
    """Prefer `back_cover_qr_url` over `site_url`."""
    html = _render(
        back_cover_qrcode=True,
        back_cover_qr_url="https://example.org/scan",
        site_url="https://example.com",
    )
    assert "QR::https://example.org/scan" in html


def test_back_cover_qrcode_skipped_without_url() -> None:
    """Render no QR code when there is no URL to encode."""
    html = _render(
        back_cover_qrcode=True,
        back_cover_qr_url="",
        site_url="",
        repo_url="",
    )
    assert "qrcode" not in html


def test_back_cover_barcode_disabled_by_default() -> None:
    """No barcode when `back_cover_barcode` is false."""
    html = _render(
        back_cover_barcode=False,
        back_cover_barcode_value="123456789012",
        back_cover_barcode_kind="code128",
    )
    assert "barcode" not in html


def test_back_cover_barcode_renders_value_and_kind() -> None:
    """Encode the value with the configured barcode kind."""
    html = _render(
        back_cover_barcode=True,
        back_cover_barcode_value="123456789012",
        back_cover_barcode_kind="code128",
    )
    assert "BAR::code128::123456789012" in html


def test_back_cover_barcode_skipped_without_value() -> None:
    """Render no barcode when there is no value to encode."""
    html = _render(
        back_cover_barcode=True,
        back_cover_barcode_value="",
        back_cover_barcode_kind="code128",
    )
    assert "barcode" not in html


def test_back_cover_qrcode_and_barcode_together() -> None:
    """Render the QR code and the barcode on the same back cover."""
    html = _render(
        back_cover_qrcode=True,
        back_cover_qr_url="https://example.org/scan",
        back_cover_barcode=True,
        back_cover_barcode_value="123456789012",
        back_cover_barcode_kind="code39",
    )
    assert "QR::https://example.org/scan" in html
    assert "BAR::code39::123456789012" in html


def test_back_cover_rendered(built_back_cover: SimpleNamespace) -> None:
    """A built back cover embeds both the QR code and the barcode."""
    soup = BeautifulSoup(
        built_back_cover.html_path.read_text(encoding="utf-8"),
        "html.parser",
    )
    back = soup.find("article", id="doc-back_cover")
    assert back is not None

    qrcode = back.find("div", class_="qrcode")
    assert qrcode is not None
    qr_link = qrcode.find("a")
    assert qr_link is not None
    assert qr_link["href"] == "https://example.org/scanned"
    qr_image = qrcode.find("img")
    assert qr_image is not None
    assert str(qr_image["src"]).startswith("data:image/svg+xml")

    barcode = back.find("div", class_="barcode")
    assert barcode is not None
    bar_image = barcode.find("img")
    assert bar_image is not None
    assert str(bar_image["src"]).startswith("data:image/svg+xml;charset=utf-8;base64,")
