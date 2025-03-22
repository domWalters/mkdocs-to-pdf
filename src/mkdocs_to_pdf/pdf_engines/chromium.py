import pathlib
import tempfile
from logging import getLogger

from .base import PDFEngine

logger = getLogger(__name__)


class Chromium(PDFEngine):
    """Chromium PDF engine."""

    def __init__(self, options):
        """Initialize Chromium PDF engine."""
        self.options = options

    def write_pdf(self, html_string: str, output_path: str):
        """Write PDF file from HTML string."""
        with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.html',
                    dir=pathlib.Path(output_path).parent) as temp:
            temp.write(html_string)
            temp_path = pathlib.Path(temp.name).as_uri()
            self.options._logger.info(f'Output a HTML to "{temp_path}"')

        chrome_path = self.options.headless_chrome_path
        self.options._logger.info(f'Browser executable path: {chrome_path}')

        # TODO:
        raise NotImplementedError

    def get_logger(self):
        """Get logger."""
        return logger
