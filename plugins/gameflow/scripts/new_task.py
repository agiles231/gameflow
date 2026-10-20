#!/usr/bin/env python3
"""Add a bounded task contract to an initialized GameFlow project."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from task_contract import render_contract
from validate_gameflow import validate_project
from planning import render as render_planning, check_destinations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--parent")
    parser.add_argument("--depends-on", action="append", default=[])
    parser.add_argument('--epic', help='Epic ID from planning.json (optional)')
    parser.add_argument('--kind', choices=['delivery', 'experiment'], default='delivery')
    args = parser.parse_args()
    errors, _ = validate_project(args.project)
    if errors: parser.error('; '.join(errors))

    flow = args.project.resolve() / ".gameflow"
    index_path = flow / "tasks" / "index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    planning_path = flow / 'planning.json'
    planning = json.loads(planning_path.read_text(encoding='utf-8')) if planning_path.exists() else None
    if args.epic and (planning is None or args.epic not in {e['id'] for e in planning['epics']}):
        parser.error('Unknown epic: ' + args.epic)
    if planning is not None: check_destinations(args.project.resolve(), planning)
    number = int(data["next_id"])
    task_id = f"TASK-{number:04d}"
    known = {task["id"] for task in data["tasks"]}
    for dependency in args.depends_on:
        if dependency not in known:
            parser.error(f"unknown dependency: {dependency}")
    if args.parent and args.parent not in known:
        parser.error(f"unknown parent: {args.parent}")

    if any(t['id'] in args.depends_on and t['status'] == 'deferred' for t in data['tasks']):
        parser.error('Cannot depend on deferred work')
    contract = f"tasks/{task_id}.md"
    if (flow / contract).exists(): parser.error('Task contract already exists')
    body = render_contract(task_id, args.title, experiment=args.kind == "experiment")
    (flow / contract).write_text(body, encoding="utf-8", newline="\n")
    data["tasks"].append({
        "id": task_id, "title": args.title, "status": "planned",
        "parent": args.parent, "depends_on": args.depends_on,
        "owner": None, "contract": contract,
    })
    data['tasks'][-1]['kind'] = args.kind
    if args.epic: data['tasks'][-1]['epic'] = args.epic
    if args.kind == 'experiment': data['tasks'][-1]['experiment_outcome'] = 'pending'
    data["next_id"] = number + 1
    index_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    if planning is not None: render_planning(args.project.resolve(), data, planning)
    print(task_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
