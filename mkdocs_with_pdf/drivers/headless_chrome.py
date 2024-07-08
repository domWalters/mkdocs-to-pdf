import os
import html as html_lib
from logging import Logger
from shutil import which
from subprocess import PIPE, Popen
import re
import pathlib


class HeadlessChromeDriver(object):
    """ 'Headless Chrome' executor """

    @classmethod
    def setup(self, program_path: str, mermaid_args: str, logger: Logger):
        if not which(program_path):
            raise RuntimeError(
                'No such `Headless Chrome` program or not executable'
                + f': "{program_path}".')
        return self(program_path, mermaid_args, logger)

    def __init__(self, program_path: str, mermaid_args: str, logger: Logger):
        self._program_path = program_path
        self.mermaid_args = mermaid_args
        self._logger = logger

    def render(self, html: str, temporary_directory: pathlib.Path) -> str:
        try:
            mermaid_regex = re.compile(r'<(\w*?[^>]*)(><[^>]*?|[^>]*?)class="(language-)?mermaid">(<[^>]*?>)?(?P<code>.*?)(<\/[^>]*?>)?<\/\1>', flags=re.DOTALL)
            mermaid_matches = mermaid_regex.finditer(html)

            i = 0
            # Convert each Mermaid diagram to an image.
            for mermaid_block in mermaid_matches:
                i += 1
                self._logger.info(f"Converting mermaid diagram {i}")
                mermaid_code = mermaid_block.group("code")

                # Create a temporary file to hold the Mermaid code.
                mermaid_file_path = temporary_directory / f"diagram_{i + 1}.mmd"
                with open(mermaid_file_path, "wb") as mermaid_file:
                    mermaid_code_unescaped = html_lib.unescape(mermaid_code)
                    mermaid_file.write(mermaid_code_unescaped.encode("utf-8"))

                # Create a filename for the image.
                image_file_path = temporary_directory / f"diagram_{i}.png"

                # Convert the Mermaid diagram to an image using mmdc.
                command = f"mmdc -i {mermaid_file_path} -o {image_file_path} {self.mermaid_args}"

                # suppress sub-process chatter when using '--quiet'
                if self.mermaid_args.find('--quiet') > -1 or self.mermaid_args.find(' -q ') > -1 or self.mermaid_args.endswith(' -q'):
                    command += " >/dev/null 2>&1"

                os.system(command)

                if not os.path.exists(image_file_path):
                    self._logger.warning(f"Error: Failed to generate mermaid diagram {i}")
                else:
                    # Replace the Mermaid code with the image in the HTML string.
                    image_html = f'<img src="file://{image_file_path}" alt="Mermaid diagram {i}">'
                    html = html.replace(mermaid_block.group(0),
                                        mermaid_block.group(0).replace(mermaid_code, image_html))

            self._logger.debug(f"Post mermaid translation: {html}")
            with open(temporary_directory / "post_mermaid_translation.html", "wb") as temp:
                temp.write(html.encode('utf-8'))

            self._logger.info("Rendering on `Headless Chrome`(execute JS).")
            with Popen([self._program_path,
                        '--disable-web-security',
                        '--no-sandbox',
                        '--headless',
                        '--disable-gpu',
                        '--disable-web-security',
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
