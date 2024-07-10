import os
from ..utils.mermaid_util import render_mermaid
from logging import Logger
import shutil
from shutil import which
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory
import pathlib


class RelaxedJSRenderer(object):

    @classmethod
    def setup(self,
              program_path: str,
              mermaid_args: str,
              mermaid_img_scale_reduction: float,
              logger: Logger):
        if not program_path:
            return None

        if not which(program_path):
            raise RuntimeError(
                'No such `ReLaXed` program or not executable'
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

    def write_pdf(self, html_string: str,
                  output: str,
                  temporary_directory: pathlib.Path):
        self._logger.info(' Rendering with `ReLaXed JS`.')

        with TemporaryDirectory() as work_dir:
            html_string = render_mermaid(
                html_string,
                work_dir,
                self.mermaid_args,
                self.mermaid_img_scale_reduction,
                self._logger)

            entry_point = os.path.join(work_dir, 'pdf_print.html')
            with open(entry_point, 'w+') as f:
                f.write(html_string)
                f.close()

            self._logger.info(f"  entry_point: {entry_point}")
            with Popen([self._program_path, entry_point, output,
                        "--build-once"],
                       stdout=PIPE) as proc:
                while True:
                    log = proc.stdout.readline().decode().strip()
                    if log:
                        self._logger.info(f"  {log}")
                    if proc.poll() is not None:
                        break
                    # workaround for '--build-once' not working
                    if log.find("Now idle and waiting for file changes") > -1:
                        proc.kill()
                        break
