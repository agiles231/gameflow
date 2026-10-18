#!/usr/bin/env python3
"""Validate the structure and invariants of an initialized GameFlow project."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from checkpoint_preflight import validate_checkpoint
from asset_review import validate as validate_manual_review


TASK_ID = re.compile(r"^TASK-\d{4,}$")
STATES = {"planned", "ready", "executing", "verify", "done", "blocked", "deferred"}
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


def validate_task_graph(index, flow: Path, errors: list[str]) -> None:
    if not isinstance(index, dict):
        errors.append("tasks/index.json must be an object")
        return
    tasks = index.get("tasks")
    if not isinstance(tasks, list):
        errors.append("tasks/index.json: tasks must be an array")
        return
    by_id: dict[str, dict] = {}
    for pos, task in enumerate(tasks):
        label = f"tasks[{pos}]"
        if not isinstance(task, dict):
            errors.append(f"{label} must be an object")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
            errors.append(f"{label}.id is invalid")
        elif task_id in by_id:
            errors.append(f"duplicate task id: {task_id}")
        else:
            by_id[task_id] = task
        if task.get("execution_mode", "autonomous") not in ("autonomous", "interactive"):
            errors.append(f"{label}.execution_mode must be autonomous or interactive")
        for issue in validate_checkpoint(task):
            errors.append(f"{label}: {issue}")
        status = task.get("status")
        if not isinstance(status, str) or status not in STATES:
            errors.append(f"{label}.status is invalid")
        contract = task.get("contract")
        if not isinstance(contract, str) or not contract:
            errors.append(f"{label}.contract must be a relative file path")
        else:
            candidate = flow / contract
            try:
                confined = not Path(contract).is_absolute() and candidate.resolve().is_relative_to(flow.resolve())
            except (OSError, RuntimeError, ValueError):
                confined = False
            if not confined:
                errors.append(f"{label}.contract escapes .gameflow: {contract!r}")
            elif not candidate.is_file():
                errors.append(f"{label}.contract does not exist: {contract!r}")
        deps = task.get("depends_on")
        if not isinstance(deps, list):
            errors.append(f"{label}.depends_on must be an array")
        else:
            for dependency in deps:
                if not isinstance(dependency, str) or not TASK_ID.fullmatch(dependency):
                    errors.append(f"{label}.depends_on contains an invalid task ID: {dependency!r}")
        parent = task.get("parent")
        if parent is not None and (not isinstance(parent, str) or not TASK_ID.fullmatch(parent)):
            errors.append(f"{label}.parent must be a task ID or null")

    next_id = index.get("next_id")
    high_watermark = max((int(task_id[5:]) for task_id in by_id), default=0)
    if type(next_id) is not int or next_id <= high_watermark:
        errors.append(f"tasks/index.json: next_id must be an integer above {high_watermark}")

    dependencies: dict[str, list[str]] = {task_id: [] for task_id in by_id}
    parents: dict[str, list[str]] = {task_id: [] for task_id in by_id}
    for task_id, task in by_id.items():
        deps = task.get("depends_on")
        for dependency in deps if isinstance(deps, list) else []:
            if not isinstance(dependency, str):
                continue
            if dependency not in by_id:
                errors.append(f"{task_id} has unknown dependency {dependency!r}")
            else:
                dependencies[task_id].append(dependency)
                if by_id[dependency].get("status") == "deferred":
                    errors.append(f"{task_id} depends on deferred task {dependency}; deferred tasks must have no dependents")
        parent = task.get("parent")
        if isinstance(parent, str):
            if parent not in by_id:
                errors.append(f"{task_id} has unknown parent {parent!r}")
            else:
                parents[task_id].append(parent)

    # Iterative topological elimination also handles large graphs without
    # depending on Python's recursion limit. Parent and dependency edges have
    # different meanings and are checked as separate graphs.
    for label, graph in (("dependency", dependencies), ("parent", parents)):
        remaining = {task_id: len(set(edges)) for task_id, edges in graph.items()}
        dependents: dict[str, list[str]] = {task_id: [] for task_id in graph}
        for task_id, edges in graph.items():
            for edge in set(edges):
                dependents[edge].append(task_id)
        ready = [task_id for task_id, count in remaining.items() if count == 0]
        visited = 0
        while ready:
            current = ready.pop()
            visited += 1
            for dependent in dependents[current]:
                remaining[dependent] -= 1
                if remaining[dependent] == 0:
                    ready.append(dependent)
        if visited != len(graph):
            errors.append(f"task graph contains a {label} cycle")


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
    if index is not None:
        validate_task_graph(index, flow, errors)
        if isinstance(index, dict) and isinstance(index.get("tasks"), list):
            legacy = [t for t in index["tasks"] if isinstance(t, dict) and t.get("status") in ("executing", "verify", "blocked") and t.get("checkpoint") is None]
            if legacy:
                warnings.append(f"{len(legacy)} legacy task(s) lack checkpoint metadata; reconcile once when resumed")

    manifest_path = flow / "assets" / "manifest.json"
    manifest = load_json(manifest_path, errors) if manifest_path.is_file() else None
    if isinstance(manifest, dict) and not isinstance(manifest.get("assets"), list):
        errors.append("assets/manifest.json: assets must be an array")

    review_path = flow / "assets" / "manual-review.json"
    if review_path.is_file():
        queue = load_json(review_path, errors)
        if queue is not None:
            try:
                validate_manual_review(queue)
            except ValueError as exc:
                errors.append(f"assets/manual-review.json: {exc}")

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
