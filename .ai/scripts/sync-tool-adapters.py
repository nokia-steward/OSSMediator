#!/usr/bin/env python3
"""Regenerate thin tool-specific adapter files from .ai/skills/*.md.

Each adapter file simply points back at the canonical skill file so Copilot,
Cursor, and Gemini all stay in sync with a single source of truth.
"""
import sys
from pathlib import Path

SKIP_FILES = {"README.md"}


COPILOT_TEMPLATE = """---
description: {title}
---

See canonical skill definition: `.ai/skills/{filename}`

Follow every section in that file exactly (Purpose, Trigger Phrases, Inputs,
Prechecks, Steps, Verification, Failure Handling, Rollback) before making any
changes. Do not duplicate the instructions here — always read the source file
first, since it is the single source of truth.
"""

CURSOR_TEMPLATE = """---
description: {title}
alwaysApply: false
---

See canonical skill definition: `.ai/skills/{filename}`

Follow every section in that file exactly (Purpose, Trigger Phrases, Inputs,
Prechecks, Steps, Verification, Failure Handling, Rollback) before making any
changes. Do not duplicate the instructions here — always read the source file
first, since it is the single source of truth.
"""

GEMINI_TEMPLATE = """# {title}

See canonical skill definition: `.ai/skills/{filename}`

Follow every section in that file exactly (Purpose, Trigger Phrases, Inputs,
Prechecks, Steps, Verification, Failure Handling, Rollback) before making any
changes. Do not duplicate the instructions here — always read the source file
first, since it is the single source of truth.
"""


def title_from_filename(filename: str) -> str:
    words = []
    for word in filename.rsplit(".", 1)[0].split("-"):
        if word == "ossmediator":
            words.append("OSSMediator")
        else:
            words.append(word.capitalize())
    return " ".join(words)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    skills_dir = repo_root / ".ai" / "skills"
    if not skills_dir.exists():
        print(f"ERROR: {skills_dir} does not exist", file=sys.stderr)
        return 1

    copilot_dir = repo_root / ".github" / "prompts"
    cursor_dir = repo_root / ".cursor" / "rules"
    gemini_dir = repo_root / ".gemini" / "prompts"
    for directory in (copilot_dir, cursor_dir, gemini_dir):
        directory.mkdir(parents=True, exist_ok=True)

    written = []
    for skill_path in sorted(skills_dir.glob("*.md")):
        if skill_path.name in SKIP_FILES:
            continue
        stem = skill_path.stem
        title = title_from_filename(skill_path.name)

        copilot_path = copilot_dir / f"{stem}.prompt.md"
        write_text(copilot_path, COPILOT_TEMPLATE.format(title=title, filename=skill_path.name))
        written.append(copilot_path)

        cursor_path = cursor_dir / f"skills-{stem}.mdc"
        write_text(cursor_path, CURSOR_TEMPLATE.format(title=title, filename=skill_path.name))
        written.append(cursor_path)

        gemini_path = gemini_dir / f"{stem}.md"
        write_text(gemini_path, GEMINI_TEMPLATE.format(title=title, filename=skill_path.name))
        written.append(gemini_path)

    print("Synced adapters:")
    for path in written:
        print(f"  - {path.relative_to(repo_root).as_posix()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
