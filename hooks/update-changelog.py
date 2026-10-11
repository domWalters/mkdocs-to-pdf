#!/usr/bin/env python3

"""Pre-commit hook: regenerate CHANGELOG.md from commit history via git-cliff."""

from __future__ import annotations

import subprocess  # ruff: ignore[suspicious-subprocess-import]
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

CHANGELOG_MD = ROOT_DIR / "CHANGELOG.md"
EXE = ROOT_DIR / ".venv" / "bin" / "git-cliff"


def main() -> int:
    """Regenerate the changelog; return 1 if it changed."""
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [str(EXE)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return result.returncode

    new_content = result.stdout

    if (
        CHANGELOG_MD.exists()
        and CHANGELOG_MD.read_text(encoding="utf-8") == new_content
    ):
        sys.stderr.write("No new changes\n")
        return 0

    CHANGELOG_MD.write_text(new_content, encoding="utf-8")
    sys.stderr.write("Updated CHANGELOG.md\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
