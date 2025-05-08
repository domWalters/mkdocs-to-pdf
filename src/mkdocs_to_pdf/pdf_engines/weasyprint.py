from weasyprint import HTML
from weasyprint.logger import LOGGER

from .base import PDFEngine
from ..options import Options


class WeasyPrint(PDFEngine):
    """WeasyPrint PDF engine."""

    def __init__(self, options: Options):
        """Initialize WeasyPrint PDF engine."""
        self.options = options

    def write_pdf(self, html_string: str, output_path: str):
        """Write PDF file from HTML string."""
        html = HTML(string=html_string)
        render = html.render()
        render.write_pdf(output_path)

    def get_logger(self):
        """Get logger."""
        return LOGGER
