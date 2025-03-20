import pathlib
import platform
import subprocess
import tempfile
from logging import getLogger

from ..options import Options
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
            temp_path = temp.name

            chromium_path = ChromiumUtils(self.options).get_chromium_path()
            args = ChromiumUtils(self.options).get_args()
            command = (
                [chromium_path]
                + args
                + [
                    '--no-pdf-header-footer',
                    '--print-to-pdf=' + output_path,
                    temp_path,
                ]
            )
            self.options._logger.info(command)
            chrome_log = subprocess.run(command,
                                        capture_output=True, text=True).stderr
            self.options._logger.info(chrome_log)

    def get_logger(self):
        """Get logger."""
        return logger


class ChromiumUtils:
    def __init__(self, options: Options):
        self.default_path = options.headless_chrome_path
        self.chrome_arguments = options.chrome_arguments
        self.chrome_extra_arguments = options.chrome_extra_arguments
        self.logger = options._logger

    def get_chromium_path(self) -> str:
        """Get path to Chromium executable."""
        command = [self.default_path, '--version']
        try:
            version = subprocess.run(
                command, check=True, capture_output=True, text=True
            ).stdout
            self.logger.info(version)
            return self.default_path
        except FileNotFoundError:
            self.logger.info(
                f'Chromium executable not found at {self.default_path}. '
                'Trying to find Chromium executable in the system.'
            )
            system = platform.system()
            if system == 'Linux':
                # Ubuntu, AlmaLinux, etc
                path = "/usr/bin/google-chrome"
            elif system == 'Darwin':
                # macOS
                path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'   # noqa
            else:
                # TODO: need to add more platform support
                raise NotImplementedError(
                    f'Unsupported platform: {platform.system()}'
                )

            command = [path, '--version']
            try:
                version = subprocess.run(
                    command, check=True, capture_output=True, text=True
                ).stdout
                self.logger.info(version)
                return path
            except Exception:
                raise FileNotFoundError(
                    f'Chromium executable not found at {path}'
                )

    def get_args(self) -> str:
        """Get Headless Chromium arguments"""
        args = [
            '--headless',
            '--no-sandbox',
            '--disable-gpu',
            '--disable-web-security',
            '--allow-file-access-from-files',
            '--run-all-compositor-stages-before-draw',
            '--virtual-time-budget=10000',
        ]
        if self.chrome_extra_arguments:
            args = args + self.chrome_extra_arguments.split()
        if self.chrome_arguments:
            args = self.chrome_arguments.split()
        return args
