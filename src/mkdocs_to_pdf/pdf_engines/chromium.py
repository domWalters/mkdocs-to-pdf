import pathlib
import tempfile
from logging import getLogger

from playwright.sync_api import sync_playwright

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
            mode='w', suffix='.html', dir=pathlib.Path(output_path).parent
        ) as html_file:
            html_file.write(html_string)
            html_url = pathlib.Path(html_file.name).as_uri()
            self.options._logger.info(f'Output a HTML to "{html_url}"')

            chrome_path = self.options.headless_chrome_path
            self.options._logger.info(f'Browser executable: {chrome_path}')

            # Rendering PDF using Playwright
            with sync_playwright() as p:
                if chrome_path:
                    browser = p.chromium.launch(executable_path=chrome_path)
                else:
                    browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(html_url)
                page.pdf(path=output_path)
                browser.close()

    def get_logger(self):
        """Get logger."""
        return logger
