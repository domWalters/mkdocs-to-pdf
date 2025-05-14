from logging import getLogger

from .base import PDFEngine
from ..options import Options

logger = getLogger(__name__)


class Chromium(PDFEngine):
    """Chromium PDF engine."""

    def __init__(self, options: Options):
        """Initialize Chromium PDF engine."""
        self.options = options

    def write_pdf(self, html_string: str, output_path: str):
        """Write PDF file from HTML string."""
        self.options.pdf_renderer.write_pdf(html_string, output_path)

    def get_logger(self):
        """Get logger."""
        return logger
