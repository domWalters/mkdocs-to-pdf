"""Headless Chrome JavaScript rendering driver."""

# ruff: file-ignore[suspicious-subprocess-import]

import os
import tempfile
import uuid
from logging import Logger
from pathlib import Path
from shutil import which
from subprocess import PIPE, Popen
from tempfile import NamedTemporaryFile


def _is_under_temp_dir(path: Path) -> bool:
    """
    Return whether `path` resolves inside a temporary directory.

    Args:
        path: The path to test.

    Returns:
        True if `path` is `/tmp` or the system temporary directory, or a child
        of either.

    """
    # `/tmp` is checked explicitly: the Snap-confined Chromium remaps `/tmp`
    # regardless of `TMPDIR`, so a project built there is unreadable to it.
    roots = {Path(tempfile.gettempdir()), Path("/tmp")}  # ruff: ignore[hardcoded-temp-file]
    for root in roots:
        try:
            path.resolve().relative_to(root.resolve())
        except (ValueError, OSError):
            continue
        return True
    return False


def _failure_message(program_path: str, temp_name: str, work_dir: Path) -> str:
    """
    Build a helpful message for a render that returned no document.

    Args:
        program_path: Path to the Chrome-compatible executable.
        temp_name: Path of the temporary document that was not rendered.
        work_dir: Directory the temporary document was written to.

    Returns:
        The error message.

    """
    base = f"`Headless Chrome` ({program_path}) did not render {temp_name!r}. "

    if _is_under_temp_dir(work_dir):
        return base + (
            "The document is in a temporary directory, which the Snap-confined "
            "Chromium on Ubuntu cannot read. Install a non-Snap build (e.g. the "
            "Chrome `.deb`) or build the site outside the temporary directory."
        )

    return base + "Check that the browser runs and can read the document."


class HeadlessChromeDriver:
    """'Headless Chrome' executor."""

    @classmethod
    def setup(cls, program_path: str, logger: Logger) -> "HeadlessChromeDriver":
        """
        Create a driver after verifying the Chrome binary exists.

        Args:
            program_path: Path to the Chrome-compatible executable.
            logger: The logger.

        Returns:
            The driver instance.

        Raises:
            RuntimeError: If the program is not found.

        """
        absolute_program_path = which(program_path)
        if absolute_program_path is None:
            message = f"No such `Headless Chrome` program: '{program_path}'"
            raise RuntimeError(message)
        return cls(absolute_program_path, logger)

    def __init__(self, program_path: str, logger: Logger) -> None:
        """
        Store the executable path and logger.

        Args:
            program_path: Path to the executable.
            logger: The logger.

        """
        self._program_path = program_path
        self._logger = logger

    @staticmethod
    def _inject_marker(html: str, marker: str) -> str:
        """
        Add a marker the driver can look for in the rendered DOM.

        Args:
            html: The HTML to render.
            marker: The unique marker value.

        Returns:
            The HTML with a marker `<meta>` in its head.

        """
        meta = f'<meta name="mkdocs-to-pdf-marker" content="{marker}">'
        if "</head>" in html:
            return html.replace("</head>", f"{meta}</head>", 1)
        return meta + html

    def render(self, html: str, work_dir: Path) -> str:
        """
        Render the HTML by executing its JavaScript.

        Args:
            html: The HTML to render.
            work_dir: Directory for the temporary document. It must be readable
                by the browser; the site directory is used because a
                Snap-confined Chromium cannot read `/tmp`.

        Returns:
            The resulting DOM.

        Raises:
            RuntimeError: If Chrome does not return the rendered document, for
                example because it could not read the temporary file.

        """
        marker = uuid.uuid4().hex
        marked = self._inject_marker(html, marker)

        work_dir.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            dir=work_dir,
            suffix=".html",
            mode="w+",
            encoding="utf-8",
        ) as temp:
            temp.write(marked)
            # Chrome reads the file from disk, so flush the buffer (and fsync)
            # before launching it; otherwise it can see an empty file and dump
            # an empty DOM.
            temp.flush()
            os.fsync(temp.fileno())

            self._logger.info("Rendering on `Headless Chrome` (execute JS) ...")
            # ruff: ignore[subprocess-without-shell-equals-true]
            with Popen(
                [
                    self._program_path,
                    "--disable-web-security",
                    "--no-sandbox",
                    "--headless",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--allow-file-access-from-files",
                    "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=10000",
                    "--dump-dom",
                    temp.name,
                ],
                stdout=PIPE,
            ) as chrome:
                output = (
                    ""
                    if chrome.stdout is None
                    else chrome.stdout.read().decode("utf-8")
                )

            if marker not in output:
                raise RuntimeError(
                    _failure_message(self._program_path, temp.name, work_dir),
                )

        return output
