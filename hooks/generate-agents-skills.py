#!/usr/bin/env python3

"""
Pre-commit hook to auto-generate the Skills section of AGENTS.md.

Scans ``.agents/skills/*/SKILL.md`` and keeps the tree listing of available
skills in ``AGENTS.md`` in sync.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
AGENTS_MD = REPO_ROOT / "AGENTS.md"

BEGIN_MARKER = "<!-- BEGIN_SKILLS -->"
END_MARKER = "<!-- END_SKILLS -->"

_SECTION_RE = re.compile(
    rf"{re.escape(BEGIN_MARKER)}\n.*?\n{re.escape(END_MARKER)}",
    re.DOTALL,
)

_FRONTMATTER_RE = re.compile(
    r"^---\s*\nname:\s*(.+?)\s*\ndescription:\s*(.+?)\s*\n---",
    re.DOTALL,
)

BRANCH = "\u251c\u2500\u2500 "
LAST = "\u2514\u2500\u2500 "


def _parse_skill(skill_md: Path) -> tuple[str, str] | None:
    content = skill_md.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(content)
    if m is None:
        rel = skill_md.relative_to(REPO_ROOT)
        sys.stderr.write(
            f"Warning: Could not parse frontmatter in {rel}\n",
        )
        return None
    name, desc = m.group(1, 2)
    if not isinstance(name, str) or not isinstance(desc, str):
        message = f"Skill '{skill_md}' doesn't contain valid frontmatter"
        raise TypeError(message)
    return name.strip(), desc.strip()


def _collect_skills() -> list[tuple[str, str]]:
    skills: list[tuple[str, str]] = []
    seen: set[str] = set()
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        parsed = _parse_skill(skill_md)
        if parsed is not None:
            name, _ = parsed
            if name in seen:
                rel = skill_md.relative_to(REPO_ROOT)
                sys.stderr.write(
                    f"Warning: Duplicate skill name '{name}' in {rel}\n",
                )
            seen.add(name)
            skills.append(parsed)
    return skills


NAME_COLUMN_LENGTH = 30


def _render_skills(skills: list[tuple[str, str]]) -> str:
    lines: list[str] = [f"{BEGIN_MARKER}\n```txt", ".agents/skills"]
    for i, (name, desc) in enumerate(skills):
        prefix = LAST if i == len(skills) - 1 else BRANCH
        start = f"{prefix}{name}"
        start += " " * (NAME_COLUMN_LENGTH - len(start))
        lines.append(f"{start} - {desc}")
    lines.append(f"```\n{END_MARKER}")
    return "\n".join(lines)


def main() -> int:
    """Generate the Skills section of AGENTS.md from the SKILL.md files."""
    if not AGENTS_MD.exists():
        sys.stderr.write(f"Error: {AGENTS_MD.relative_to(REPO_ROOT)} not found\n")
        return 1

    if not SKILLS_DIR.exists():
        sys.stderr.write("Warning: .agents/skills directory not found, skipping\n")
        return 0

    skills = _collect_skills()
    if not skills:
        sys.stderr.write("Warning: No SKILL.md files found in .agents/skills/\n")
        return 0

    content = AGENTS_MD.read_text(encoding="utf-8")
    new_section = _render_skills(skills)

    if not _SECTION_RE.search(content):
        sys.stderr.write(
            f"Error: Markers {BEGIN_MARKER} / {END_MARKER} "
            f"not found in {AGENTS_MD.relative_to(REPO_ROOT)}\n",
        )
        return 1

    new_content = _SECTION_RE.sub(new_section, content)

    if new_content != content:
        AGENTS_MD.write_text(new_content, encoding="utf-8")
        sys.stderr.write(f"Updated {AGENTS_MD.relative_to(REPO_ROOT)} Skills section\n")
        # Return non-zero so pre-commit knows files were modified and re-stages them.
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
