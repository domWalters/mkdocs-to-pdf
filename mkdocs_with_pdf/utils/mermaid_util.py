import os
import re
import html as html_lib
import pathlib
from logging import Logger
from typing import Union


def render_mermaid(html: str,
                   temporary_directory: Union[str, pathlib.Path],
                   mermaid_args: str,
                   mermaid_img_scale_reduction: float,
                   logger: Logger):

    if (isinstance(temporary_directory, str)):
        temporary_directory = pathlib.Path(temporary_directory)

    mermaid_regex = re.compile(r'<(\w*?[^>]*)(><[^>]*?|[^>]*?)class="[^>\"]*(language-)?mermaid[^>\"]*">(<[^>]*?>)?(?P<code>.*?)(<\/[^>]*?>)?<\/\1>', flags=re.DOTALL)
    mermaid_matches = mermaid_regex.finditer(html)

    i = 0
    # Convert each Mermaid diagram to an image.
    for mermaid_block in mermaid_matches:
        i += 1
        logger.info(f"Converting mermaid diagram {i}")
        mermaid_code = mermaid_block.group("code")

        # Create a temporary file to hold the Mermaid code.
        mermaid_file_path = temporary_directory / f"diagram_{i + 1}.mmd"
        with open(mermaid_file_path, "wb") as mermaid_file:
            mermaid_code_unescaped = html_lib.unescape(mermaid_code)
            mermaid_file.write(mermaid_code_unescaped.encode("utf-8"))

        # Create a filename for the image.
        image_file_path = temporary_directory / f"diagram_{i}.png"

        # Convert the Mermaid diagram to an image using mmdc.
        command = f"mmdc -i {mermaid_file_path} -o {image_file_path} {mermaid_args}"

        # suppress sub-process chatter when using '--quiet'
        if mermaid_args.find('--quiet') > -1 or mermaid_args.find(' -q ') > -1 or mermaid_args.endswith(' -q'):
            command += " >/dev/null 2>&1"

        os.system(command)

        if not os.path.exists(image_file_path):
            logger.warning(f"Error: Failed to generate mermaid diagram {i}")
        else:
            from PIL import Image

            with Image.open(image_file_path) as im:
                # Replace the Mermaid code with the image in the HTML string.
                image_html = f'<img src="file://{image_file_path}" alt="Mermaid diagram {i}">'

                if mermaid_img_scale_reduction != 1:
                    height = im.height // mermaid_img_scale_reduction
                    width = im.width // mermaid_img_scale_reduction
                    image_html = image_html.replace('">', f'" style="max-width:{width}px; max-height:{height}px;">')

                html = html.replace(mermaid_block.group(0),
                                    mermaid_block.group(0).replace(mermaid_code, image_html))

    return html
