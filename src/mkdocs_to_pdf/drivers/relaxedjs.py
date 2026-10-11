"""ReLaXed JavaScript PDF rendering driver."""

# ruff: file-ignore[suspicious-subprocess-import]

import pathlib
from logging import Logger
from shutil import which
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory


class RelaxedJSRenderer:
    """'ReLaXed' PDF renderer."""

    @classmethod
    def setup(cls, program_path: str, logger: Logger) -> "RelaxedJSRenderer | None":
        """
        Create a renderer if a program path is configured.

        Args:
            program_path: Path to the ReLaXed executable.
            logger: The logger.

        Returns:
            The renderer instance, or None if no path was given.

        Raises:
            RuntimeError: If the program is not found.

        """
        absolute_program_path = which(program_path)
        if absolute_program_path is None:
            message = f"No such `ReLaXed` program: '{program_path}'"
            raise RuntimeError(message)

        return cls(absolute_program_path, logger)

    def __init__(self, program_path: str, logger: Logger) -> None:
        """
        Store the executable path and logger.

        Args:
            program_path: Path to the ReLaXed executable.
            logger: The logger.

        """
        self._program_path = program_path
        self._logger = logger

    def write_pdf(self, html_string: str, output: str) -> None:
        """
        Render the HTML to a PDF via ReLaXed.

        Args:
            html_string: The HTML to render.
            output: The output PDF path.

        """
        self._logger.info(" Rendering with `ReLaXed JS` ...")

        with TemporaryDirectory() as work_dir:
            entry_point = pathlib.Path(work_dir) / "pdf_print.html"
            with entry_point.open("w+", encoding="utf-8") as f:
                f.write(html_string)

            self._logger.info("  entry_point: %s", entry_point)
            # ruff: ignore[subprocess-without-shell-equals-true]
            with Popen(
                [self._program_path, entry_point, output, "--build-once"],
                stdout=PIPE,
            ) as proc:
                if proc.stdout is None:
                    return
                while True:
                    log = proc.stdout.readline().decode().strip()
                    if log:
                        self._logger.info("  %s", log)
                    if proc.poll() is not None:
                        break
