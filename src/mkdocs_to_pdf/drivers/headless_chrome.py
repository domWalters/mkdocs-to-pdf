import os
import pathlib
from logging import Logger
from shutil import which
from tempfile import NamedTemporaryFile

from playwright.sync_api import sync_playwright


class HeadlessChromeDriver(object):
    """ 'Headless Chrome' executor """

    @classmethod
    def setup(self, program_path: str, logger: Logger):
        if not which(program_path):
            raise RuntimeError(
                'No such `Headless Chrome` program or not executable'
                + f': "{program_path}".')
        return self(program_path, logger)

    def __init__(self, program_path: str, logger: Logger):
        self._program_path = program_path
        self._logger = logger

    def render(self, html: str) -> str:
        temp = NamedTemporaryFile(delete=False, suffix='.html')
        try:
            temp.write(html.encode('utf-8'))
            temp.close()

            self._logger.info('Rendering on `Headless Chrome`(execute JS).')

            html_uri = pathlib.Path(temp.name).as_uri()

            # Rendering JavaScript using Playwright
            with sync_playwright() as p:
                if self._program_path:
                    browser = p.chromium.launch(executable_path=self._program_path)
                else:
                    browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(html_uri)
                html = page.content()
                browser.close()

        except Exception as e:
            self._logger.error(f'Failed to render by JS: {e}')
        finally:
            os.unlink(temp.name)

        return html
