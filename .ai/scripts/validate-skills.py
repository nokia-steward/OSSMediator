#!/usr/bin/env python3
"""Validate that every skill file under .ai/skills contains required sections."""
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "## Purpose",
    "## Trigger Phrases",
    "## Owner / Script",
    "## Inputs",
    "## Environment",
    "## Prechecks",
    "## Steps",
    "## What This Updates / Does",
    "## Verification",
    "## Failure Handling",
    "## Rollback",
    "## Outputs / Artifacts",
]

SKIP_FILES = {"README.md"}


def validate_skill_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in text]
    return missing


def main() -> int:
    skills_dir = Path(__file__).resolve().parents[1] / "skills"
    if not skills_dir.exists():
        print(f"ERROR: {skills_dir} does not exist", file=sys.stderr)
        return 1

    had_errors = False
    for path in sorted(skills_dir.glob("*.md")):
        if path.name in SKIP_FILES:
            continue
        missing = validate_skill_file(path)
        if missing:
            had_errors = True
            print(f"FAIL: {path.name} missing sections: {', '.join(missing)}")
        else:
            print(f"OK:   {path.name}")

    return 1 if had_errors else 0


if __name__ == "__main__":
    sys.exit(main())
