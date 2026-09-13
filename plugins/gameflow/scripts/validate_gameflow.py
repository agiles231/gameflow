#!/usr/bin/env python3
"""Validate the structure and invariants of an initialized GameFlow project."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


TASK_ID = re.compile(r"^TASK-\d{4,}$")
STATES = {"planned", "ready", "executing", "verify", "done", "blocked"}
REQUIRED = [
    "PROJECT.md", "CONSTRAINTS.md", "ART_DIRECTION.md", "GAMEPLAY.md",
    "INTERFACE.md", "ARCHITECTURE.md", "DECISIONS.md", "GLOSSARY.md",
    "tasks/index.json", "assets/manifest.json", "verification/standards.md",
    "sessions/CURRENT.md", "tools/capabilities.json", "tools/applications.json",
]


def load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    root = args.project.resolve()
    flow = root / ".gameflow"
    errors: list[str] = []
    warnings: list[str] = []

    if not flow.is_dir():
        errors.append(f"missing {flow}")
    for relative in REQUIRED:
        if not (flow / relative).is_file():
            errors.append(f"missing .gameflow/{relative}")

    agents = root / "AGENTS.md"
    if not agents.is_file() or "<!-- gameflow:start -->" not in agents.read_text(encoding="utf-8"):
        errors.append("AGENTS.md does not contain the GameFlow entrypoint")

    index_path = flow / "tasks" / "index.json"
    index = load_json(index_path, errors) if index_path.is_file() else None
    if isinstance(index, dict):
        tasks = index.get("tasks")
        if not isinstance(tasks, list):
            errors.append("tasks/index.json: tasks must be an array")
            tasks = []
        ids: set[str] = set()
        for pos, task in enumerate(tasks):
            label = f"tasks[{pos}]"
            if not isinstance(task, dict):
                errors.append(f"{label} must be an object")
                continue
            task_id = task.get("id")
            if not isinstance(task_id, str) or not TASK_ID.match(task_id):
                errors.append(f"{label}.id is invalid")
            elif task_id in ids:
                errors.append(f"duplicate task id: {task_id}")
            else:
                ids.add(task_id)
            if task.get("status") not in STATES:
                errors.append(f"{label}.status is invalid")
            contract = task.get("contract")
            if not isinstance(contract, str) or not (flow / contract).is_file():
                errors.append(f"{label}.contract does not exist: {contract!r}")
            deps = task.get("depends_on")
            if not isinstance(deps, list):
                errors.append(f"{label}.depends_on must be an array")
        for task in tasks:
            if isinstance(task, dict):
                for dependency in task.get("depends_on", []):
                    if dependency not in ids:
                        errors.append(f"{task.get('id')} has unknown dependency {dependency}")

    manifest_path = flow / "assets" / "manifest.json"
    manifest = load_json(manifest_path, errors) if manifest_path.is_file() else None
    if isinstance(manifest, dict) and not isinstance(manifest.get("assets"), list):
        errors.append("assets/manifest.json: assets must be an array")

    temporary = flow / "verification" / "temporary"
    if temporary.is_dir():
        retained = [p for p in temporary.iterdir() if p.name != ".gitignore"]
        if retained:
            warnings.append(f"temporary verification directory contains {len(retained)} item(s)")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"GameFlow validation failed with {len(errors)} error(s).")
        return 1
    print(f"GameFlow validation passed ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
