from .base import PDFEngine
import platform
import subprocess
import tempfile
from logging import getLogger

logger = getLogger(__name__)


class Chromium(PDFEngine):
    """Chromium PDF engine."""

    def write_pdf(self, html_string: str, output_path: str):
        """Write PDF file from HTML string."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html') as temp:
            temp.write(html_string)
            temp_path = temp.name

            chromium_path = self._get_chromium_path()
            # XXX: need to add more options
            command = [
                chromium_path,
                '--headless',
                '--no-pdf-header-footer',
                '--print-to-pdf=' + output_path,
                temp_path,
            ]
            subprocess.run(command)

    def get_logger(self):
        """Get logger."""
        return logger

    def _get_chromium_path(self) -> str:
        """Get path to Chromium executable."""
        # XXX: need to add more platform support
        if platform.system() == 'Darwin':
            path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'   # noqa
        else:
            raise NotImplementedError(
                f'Unsupported platform: {platform.system()}')
        return path
