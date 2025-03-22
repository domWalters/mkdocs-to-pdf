import os
import pathlib
from logging import Logger
from shutil import which
from tempfile import NamedTemporaryFile

from playwright.sync_api import sync_playwright


class HeadlessChromeDriver(object):
    """'Headless Chrome' executor"""

    @classmethod
    def setup(self, program_path: str, output_path: str, logger: Logger):
        if not which(program_path):
            raise FileNotFoundError(
                f'Chromium executable not found at {program_path}'
            )
        return self(program_path, output_path, logger)

    def __init__(self, program_path: str, output_path: str, logger: Logger):
        self._program_path = program_path
        self._output_path = output_path
        self._logger = logger

    def render(self, html_string: str) -> str:
        os.makedirs(pathlib.Path(self._output_path).parent, exist_ok=True)
        html_file = NamedTemporaryFile(
            delete=False,
            suffix='.html',
            dir=pathlib.Path(self._output_path).parent,
        )
        try:
            html_file.write(html_string.encode('utf-8'))
            html_file.close()

            self._logger.info('Rendering on `Headless Chrome`(execute JS).')

            html_uri = pathlib.Path(html_file.name).as_uri()
            self._logger.info(html_uri)

            # Rendering JavaScript using Playwright
            with sync_playwright() as p:
                if self._program_path:
                    browser = p.chromium.launch(
                        executable_path=self._program_path
                    )
                else:
                    browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(html_uri)
                html_string = page.content()
                browser.close()

        except Exception as e:
            self._logger.error(f'Failed to render by JS: {e}')
        finally:
            os.unlink(html_file.name)

        return html_string
