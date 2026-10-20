#!/usr/bin/env python3
"""Initialize portable GameFlow state in a game project."""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

from managed_guidance import render, replace_checked
from task_contract import render_contract


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
    existing = agents.read_bytes() if agents.exists() else None
    updated = render(existing or b"", block_path.read_bytes())
    if updated != existing:
        replace_checked(agents, existing, updated)


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

    # Validate managed markers before creating any project state.
    agents = project / "AGENTS.md"
    if agents.is_symlink():
        parser.error("refusing symlink AGENTS.md")
    try:
        render(agents.read_bytes() if agents.exists() else b"", (plugin / "templates/AGENTS.block.md").read_bytes())
    except ValueError as exc:
        parser.error(str(exc))
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
    first_contract = destination / "tasks/TASK-0001.md"
    if not first_contract.exists():
        first_contract.write_text(render_contract("TASK-0001", "Define the first vertical slice", discovery=True), encoding="utf-8")
    update_agents(project, plugin / "templates" / "AGENTS.block.md")
    print(f"Initialized GameFlow at {destination}")
    print("Existing project-state files were preserved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
