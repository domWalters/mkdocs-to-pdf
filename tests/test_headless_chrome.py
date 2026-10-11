"""Tests for the headless Chrome JavaScript driver."""

import logging
import shutil

import pytest

from mkdocs_to_pdf.drivers.headless_chrome import HeadlessChromeDriver

_CHROME = (
    shutil.which("chromium")
    or shutil.which("chromium-browser")
    or shutil.which("google-chrome")
    or shutil.which("google-chrome-stable")
)


@pytest.mark.skipif(_CHROME is None, reason="no Chromium/Chrome available")
def test_render_returns_html_from_the_temp_file() -> None:
    """
    Chrome must see the HTML written to the temporary file.

    The file was previously left unflushed, so a document smaller than the I/O
    buffer (and any document on Python 3.14) was empty when Chrome read it and
    the dumped DOM came back empty (issue #85).
    """
    assert _CHROME is not None
    driver = HeadlessChromeDriver.setup(_CHROME, logging.getLogger("test"))

    output = driver.render("<html><body><p>FLUSH_MARKER</p></body></html>")

    assert "FLUSH_MARKER" in output
