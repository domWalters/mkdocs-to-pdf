"""Tests for the headless Chrome JavaScript driver."""

import logging
import shutil
from pathlib import Path

import pytest

from mkdocs_to_pdf.drivers.headless_chrome import (
    HeadlessChromeDriver,
    _failure_message,
    _is_under_temp_dir,
)

_CHROME = (
    shutil.which("chromium")
    or shutil.which("chromium-browser")
    or shutil.which("google-chrome")
    or shutil.which("google-chrome-stable")
)

# Echo the temp document back (emulating `--dump-dom`) and record its path.
_FAKE_CHROME = (
    "#!/bin/sh\n"
    "for last; do :; done\n"
    'printf \'%s\' "$last" > "$(dirname "$0")/arg"\n'
    'cat "$last"\n'
)

# Emulate a browser that cannot read the temp file: no output at all.
_BLANK_CHROME = "#!/bin/sh\nexit 0\n"


def _fake_chrome(path: Path, script: str) -> str:
    """Write an executable fake Chrome and return its path."""
    path.write_text(script, encoding="utf-8")
    path.chmod(0o755)
    return str(path)


def test_render_writes_temp_file_to_work_dir(tmp_path: Path) -> None:
    """The temp document is written into `work_dir`, not the system temp dir."""
    driver = HeadlessChromeDriver.setup(
        _fake_chrome(tmp_path / "chrome", _FAKE_CHROME),
        logging.getLogger("test"),
    )

    driver.render("<html><body><p>x</p></body></html>", tmp_path)

    recorded = Path((tmp_path / "arg").read_text(encoding="utf-8"))
    assert recorded.parent == tmp_path
    assert recorded.suffix == ".html"


def test_render_raises_when_chrome_cannot_read_the_file(tmp_path: Path) -> None:
    """A browser that returns no document crashes the build with a message."""
    driver = HeadlessChromeDriver.setup(
        _fake_chrome(tmp_path / "chrome", _BLANK_CHROME),
        logging.getLogger("test"),
    )

    with pytest.raises(RuntimeError, match="temporary directory"):
        driver.render("<html><body><p>x</p></body></html>", tmp_path)


def test_is_under_temp_dir(tmp_path: Path) -> None:
    """Temp detection matches the temp dir (and /tmp) but not a project dir."""
    assert _is_under_temp_dir(tmp_path)
    assert _is_under_temp_dir(Path("/tmp"))  # ruff: ignore[hardcoded-temp-file]
    assert not _is_under_temp_dir(Path.cwd())


def test_failure_message_mentions_snap_only_under_tmp(tmp_path: Path) -> None:
    """The Snap hint is only shown when the document is under a temp dir."""
    in_tmp = _failure_message("chrome", str(tmp_path / "x.html"), tmp_path)
    assert "Snap" in in_tmp

    project = Path.cwd()
    outside = _failure_message("chrome", str(project / "x.html"), project)
    assert "Snap" not in outside
    assert "did not render" in outside


@pytest.mark.skipif(_CHROME is None, reason="no Chromium/Chrome available")
def test_render_returns_html_from_the_temp_file(tmp_path: Path) -> None:
    """
    Chrome must see the HTML written to the temporary file.

    The file was previously left unflushed, so a document smaller than the I/O
    buffer (and any document on Python 3.14) was empty when Chrome read it and
    the dumped DOM came back empty (issue #85).
    """
    assert _CHROME is not None
    driver = HeadlessChromeDriver.setup(_CHROME, logging.getLogger("test"))

    output = driver.render("<html><body><p>FLUSH_MARKER</p></body></html>", tmp_path)

    assert "FLUSH_MARKER" in output
