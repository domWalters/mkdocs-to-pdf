import os
import pathlib
from logging import Logger
from shutil import which
from tempfile import NamedTemporaryFile

from playwright.sync_api import sync_playwright


class HeadlessChromeDriver(object):
    """Headless Chrome using Playwright"""

    @classmethod
    def setup(self, chrome_path: str, output_path: str, logger: Logger):
        if chrome_path and not which(chrome_path):
            raise FileNotFoundError(
                f'Chromium executable not found at {chrome_path}'
            )
        return self(chrome_path, output_path, logger)

    def __init__(self, chrome_path: str, output_path: str, logger: Logger):
        self._chrome_path = chrome_path
        self._output_path = output_path
        self._logger = logger

    def write_pdf(self, html_string: str, output_path: str):
        """Write PDF file from HTML string."""
        html_file = NamedTemporaryFile(
            delete=False, suffix='.html', dir=pathlib.Path(output_path).parent
        )
        try:
            html_file.write(html_string.encode('utf-8'))
            html_file.close()

            html_uri = pathlib.Path(html_file.name).as_uri()
            self._logger.debug(f'Output a HTML to "{html_uri}"')

            # Rendering PDF using Playwright/Chromium
            self._logger.info('Rendering PDF using Playwright/Chromium')
            with sync_playwright() as p:
                if self._chrome_path:
                    browser = p.chromium.launch(
                        executable_path=self._chrome_path
                    )
                else:
                    browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(html_uri)
                page.pdf(path=output_path)
                browser.close()

        except Exception as e:
            self._logger.error(f'Failed to render: {e}')
            raise e
        finally:
            os.unlink(html_file.name)

    def render(self, html_string: str) -> str:
        """Rendering HTML+JavaScript to HTML"""
        output_path = self._output_path
        os.makedirs(pathlib.Path(output_path).parent, exist_ok=True)
        html_file = NamedTemporaryFile(
            delete=False,
            suffix='.html',
            dir=pathlib.Path(output_path).parent,
        )
        try:
            html_file.write(html_string.encode('utf-8'))
            html_file.close()

            html_uri = pathlib.Path(html_file.name).as_uri()
            self._logger.debug(f'Output a HTML to "{html_uri}"')

            self._logger.info('Rendering JavaScript using Playwright/Chromium')

            # Rendering JavaScript using Playwright
            with sync_playwright() as p:
                if self._chrome_path:
                    browser = p.chromium.launch(
                        executable_path=self._chrome_path
                    )
                else:
                    browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(html_uri)
                html_string = page.content()    # dump-dom
                browser.close()

        except Exception as e:
            self._logger.error(f'Failed to render by JS: {e}')
            raise e
        finally:
            os.unlink(html_file.name)

        return html_string
