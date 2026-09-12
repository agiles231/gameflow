#!/usr/bin/env python3
"""Add a bounded task contract to an initialized GameFlow project."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--parent")
    parser.add_argument("--depends-on", action="append", default=[])
    args = parser.parse_args()

    flow = args.project.resolve() / ".gameflow"
    index_path = flow / "tasks" / "index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    number = int(data["next_id"])
    task_id = f"TASK-{number:04d}"
    known = {task["id"] for task in data["tasks"]}
    for dependency in args.depends_on:
        if dependency not in known:
            parser.error(f"unknown dependency: {dependency}")
    if args.parent and args.parent not in known:
        parser.error(f"unknown parent: {args.parent}")

    contract = f"tasks/{task_id}.md"
    body = f"""# {task_id} — {args.title}

## Outcome

Define one principal deliverable.

## Inputs

- Define required inputs.

## Outputs

- Define durable outputs.

## Acceptance

- Define an observable pass/fail condition.

## Context

Required: list exact files or sections.

Excluded: list nearby context that is not needed.

## Completion evidence

Not yet completed.
"""
    (flow / contract).write_text(body, encoding="utf-8", newline="\n")
    data["tasks"].append({
        "id": task_id, "title": args.title, "status": "planned",
        "parent": args.parent, "depends_on": args.depends_on,
        "owner": None, "contract": contract,
    })
    data["next_id"] = number + 1
    index_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(task_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
