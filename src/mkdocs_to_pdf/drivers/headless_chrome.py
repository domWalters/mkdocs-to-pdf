"""Headless Chrome JavaScript rendering driver."""

# ruff: file-ignore[suspicious-subprocess-import]

import os
from logging import Logger
from shutil import which
from subprocess import PIPE, Popen
from tempfile import NamedTemporaryFile


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
            program_path: Path to the Chrome-compatible executable.
            logger: The logger.

        """
        self._program_path = program_path
        self._logger = logger

    def render(self, html: str) -> str:
        """
        Render the HTML by executing its JavaScript.

        Args:
            html: The HTML to render.

        Returns:
            The resulting DOM.

        """
        with NamedTemporaryFile(suffix=".html") as temp:
            temp.write(html.encode("utf-8"))
            # Chrome reads the file from disk, so flush the buffer (and fsync)
            # before launching it; otherwise it can see an empty file and dump
            # an empty DOM.
            temp.flush()
            os.fsync(temp.fileno())
            try:
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
                    if chrome.stdout is None:
                        self._logger.error(
                            "Failed to render JS, retaining the original HTML",
                        )
                        return html
                    return chrome.stdout.read().decode("utf-8")

            except Exception:
                self._logger.exception("Failed to render JS")

        return html
