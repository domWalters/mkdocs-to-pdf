from ..utils.mermaid_util import render_mermaid
from logging import Logger
from shutil import which
from subprocess import PIPE, Popen
import pathlib


class HeadlessChromeDriver(object):
    """ 'Headless Chrome' executor """

    @classmethod
    def setup(self,
              program_path: str,
              mermaid_args: str,
              mermaid_img_scale_reduction: float,
              logger: Logger):
        if not which(program_path):
            raise RuntimeError(
                'No such `Headless Chrome` program or not executable'
                + f': "{program_path}".')
        return self(program_path,
                    mermaid_args,
                    mermaid_img_scale_reduction,
                    logger)

    def __init__(self, program_path: str,
                 mermaid_args: str,
                 mermaid_img_scale_reduction: float,
                 logger: Logger):
        self._program_path = program_path
        self.mermaid_args = mermaid_args
        self.mermaid_img_scale_reduction = mermaid_img_scale_reduction
        self._logger = logger

    def render(self, html: str, temporary_directory: pathlib.Path) -> str:
        try:
            html = render_mermaid(
                html,
                temporary_directory,
                self.mermaid_args,
                self.mermaid_img_scale_reduction,
                self._logger)

            self._logger.debug(f"Post mermaid translation: {html}")
            with open(temporary_directory / "post_mermaid_translation.html", "wb") as temp:
                temp.write(html.encode('utf-8'))

            self._logger.info("Rendering on `Headless Chrome`(execute JS).")
            with Popen([self._program_path,
                        '--disable-web-security',
                        '--no-sandbox',
                        '--headless',
                        '--disable-gpu',
                        '-–allow-file-access-from-files',
                        '--run-all-compositor-stages-before-draw',
                        '--virtual-time-budget=10000',
                        '--dump-dom',
                        temp.name], stdout=PIPE) as chrome:
                chrome_output = chrome.stdout.read().decode('utf-8')
                self._logger.debug(f"Post chrome translation: {chrome_output}")
                return chrome_output

        except Exception as e:
            self._logger.error(f'Failed to render by JS: {e}')

        return html
