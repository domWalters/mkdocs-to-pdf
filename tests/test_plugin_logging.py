"""Tests that WeasyPrint's logs are surfaced to the console."""

import io
import logging

from weasyprint.logger import LOGGER

from mkdocs_to_pdf.plugin import (
    _mkdocs_formatter,
    _setup_weasyprint_logging,
    _WeasyPrintLogHandler,
)


def _console_handler() -> _WeasyPrintLogHandler:
    """Return the single console handler attached to WeasyPrint's logger."""
    _setup_weasyprint_logging()
    handlers = [h for h in LOGGER.handlers if isinstance(h, _WeasyPrintLogHandler)]
    assert len(handlers) == 1
    return handlers[0]


def test_setup_weasyprint_logging_is_idempotent() -> None:
    """Attach only one console handler, however often setup runs."""
    _setup_weasyprint_logging()
    _setup_weasyprint_logging()

    handlers = [h for h in LOGGER.handlers if isinstance(h, _WeasyPrintLogHandler)]
    assert len(handlers) == 1


def test_weasyprint_errors_reach_the_console() -> None:
    """Write an error-level record to the console handler's stream."""
    handler = _console_handler()
    stream = io.StringIO()
    previous_stream = handler.setStream(stream)
    assert previous_stream is not None
    previous_level = LOGGER.level
    try:
        LOGGER.setLevel(logging.ERROR)
        LOGGER.error("Failed to load image at 'missing.png'")
    finally:
        LOGGER.setLevel(previous_level)
        handler.setStream(previous_stream)

    output = stream.getvalue()
    assert "ERROR" in output
    assert "Failed to load image" in output


def test_mkdocs_formatter_returns_usable_formatter() -> None:
    """Return a formatter that renders a log record's message."""
    record = logging.LogRecord("weasyprint", logging.ERROR, "", 0, "boom", (), None)

    assert "boom" in _mkdocs_formatter().format(record)
