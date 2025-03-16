from weasyprint import HTML
from weasyprint.logger import LOGGER

from .base import PDFEngine


class WeasyPrint(PDFEngine):
    """WeasyPrint PDF engine."""

    def write_pdf(self, html_string: str, output_path: str):
        """Write PDF file from HTML string."""
        html = HTML(string=html_string)
        render = html.render()
        render.write_pdf(output_path)

    def get_logger(self):
        """Get logger."""
        return LOGGER
