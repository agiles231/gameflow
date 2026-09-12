#!/usr/bin/env python3
"""Initialize portable GameFlow state in a game project."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path


START = "<!-- gameflow:start -->"
END = "<!-- gameflow:end -->"


def copy_templates(source: Path, destination: Path, replacements: dict[str, str]) -> None:
    for item in source.rglob("*"):
        relative = item.relative_to(source)
        target = destination / relative
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            content = item.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(item, target)
            continue
        for key, value in replacements.items():
            content = content.replace("{{" + key + "}}", value)
        target.write_text(content, encoding="utf-8", newline="\n")


def update_agents(project: Path, block_path: Path) -> None:
    agents = project / "AGENTS.md"
    block = block_path.read_text(encoding="utf-8").strip()
    existing = agents.read_text(encoding="utf-8") if agents.exists() else ""
    if START in existing and END in existing:
        prefix, rest = existing.split(START, 1)
        _, suffix = rest.split(END, 1)
        updated = prefix.rstrip() + "\n\n" + block + suffix
    else:
        updated = existing.rstrip() + ("\n\n" if existing.strip() else "") + block + "\n"
    agents.write_text(updated, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--engine", default="unspecified")
    args = parser.parse_args()

    project = args.project.resolve()
    if not project.exists() or not project.is_dir():
        parser.error(f"project directory does not exist: {project}")

    plugin = Path(__file__).resolve().parent.parent
    template = plugin / "templates" / "gameflow"
    if not template.is_dir():
        raise RuntimeError(f"missing template directory: {template}")

    destination = project / ".gameflow"
    copy_templates(
        template,
        destination,
        {
            "PROJECT_NAME": args.name,
            "ENGINE": args.engine,
            "DATE": dt.date.today().isoformat(),
        },
    )
    update_agents(project, plugin / "templates" / "AGENTS.block.md")
    print(f"Initialized GameFlow at {destination}")
    print("Existing project-state files were preserved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
