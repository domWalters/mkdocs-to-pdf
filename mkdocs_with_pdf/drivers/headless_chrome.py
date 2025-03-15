import os
import html as html_lib
from logging import Logger
from shutil import which
from subprocess import PIPE, Popen
from tempfile import NamedTemporaryFile
import re
import tempfile

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
            mermaid_regex = r'<pre class="mermaid"><code>(.*?)</code></pre>'
            mermaid_matches = re.findall(mermaid_regex, html, flags=re.DOTALL)
             # Add a member variable for the output directory.
            self.output_dir = "./img_out"

            # Create the output directory if it does not exist.
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            # Convert each Mermaid diagram to an image.
            for i, mermaid_code in enumerate(mermaid_matches):
                self._logger.info("Converting diagram.")
                # Create a temporary file to hold the Mermaid code.
                with tempfile.NamedTemporaryFile(suffix=".mmd") as mermaid_file:
                    # Write the Mermaid code to the file.
                    mermaid_code_unescaped = html_lib.unescape(mermaid_code)
                    mermaid_file.write(mermaid_code_unescaped.encode("utf-8"))
                    self._logger.info(mermaid_code)
                    mermaid_file.flush()

                    # Create a filename for the image.
                    image_filename = os.path.join(self.output_dir, f"diagram_{i+1}.png")

                    # Convert the Mermaid diagram to an image using mmdc.
                    command = f"mmdc -p ../puppeteer-config.json -i {mermaid_file.name} -o {image_filename} -b transparent --scale 4"
                    os.system(command)

                    # Replace the Mermaid code with the image in the HTML string.
                    image_html = f'<img src="file://{os.path.abspath(image_filename)}" alt="Mermaid diagram {i+1}">'
                    html = html.replace(f'<pre class="mermaid"><code>{mermaid_code}</code></pre>', image_html)

            self._logger.info(html)
            temp.write(html.encode('utf-8'))
            temp.close()

            self._logger.info("Rendering on `Headless Chrome`(execute JS).")
            with Popen([self._program_path,
                        '--disable-web-security',
                        '--no-sandbox',
                        '--headless',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--disable-dev-shm-usage',
                        '--hide-scrollbars',
                        '--disable-web-security',
                        '-–allow-file-access-from-files',
                        '--run-all-compositor-stages-before-draw',
                        '--virtual-time-budget=10000',
                        '--dump-dom',
                        temp.name], stdout=PIPE) as chrome:
                return chrome.stdout.read().decode('utf-8')


        except Exception as e:
            self._logger.error(f'Failed to render by JS: {e}')
        finally:
            os.unlink(temp.name)

        return html
