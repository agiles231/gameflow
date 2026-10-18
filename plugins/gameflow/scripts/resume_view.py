#!/usr/bin/env python3
"""Print a read-only compact task view; validate the full graph before filtering."""
import argparse
from collections import Counter
import json
from pathlib import Path

from validate_gameflow import load_json, validate_task_graph


def recovery_reasons(task):
    reasons = []
    checkpoint = task.get('checkpoint') or {}
    if task.get('owner') or checkpoint.get('owner'):
        reasons.append('owner')
    if task['status'] in ('executing', 'verify', 'blocked'):
        reasons.append(task['status'])
    if checkpoint and checkpoint['commit']['state'] != 'committed':
        reasons.append('uncommitted')
    # Unknown job state must remain visible for coordinator reconciliation.
    if any(str(job.get('status', '')).lower() not in ('completed', 'succeeded', 'failed', 'cancelled', 'canceled')
           for job in checkpoint.get('jobs', [])):
        reasons.append('jobs')
    return reasons


def compact(index):
    tasks = index['tasks']
    by_id = {t['id']: t for t in tasks}
    rows = []
    for task in tasks:
        recovery = recovery_reasons(task)
        if task['status'] == 'done' and not recovery:
            continue
        row = {key: task[key] for key in ('id', 'title', 'status', 'contract', 'parent',
                                         'execution_mode', 'priority') if key in task}
        row['dependencies'] = {dep: by_id[dep]['status'] for dep in task['depends_on']}
        row['recovery'] = recovery
        rows.append(row)
    return {'counts': dict(sorted(Counter(t['status'] for t in tasks).items())),
            'tasks': rows,
            'note': 'Read full task record and contract before recovery or selection; this view is not authority, liveness, acceptance, or commit verification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--task', help='Print the full canonical record for one task')
    args = parser.parse_args()
    flow = args.project.resolve() / '.gameflow'
    errors = []
    index = load_json(flow / 'tasks/index.json', errors)
    if not errors:
        validate_task_graph(index, flow, errors)
    if errors:
        print(json.dumps({'errors': errors}, indent=2))
        return 1
    if args.task:
        selected = next((task for task in index['tasks'] if task['id'] == args.task), None)
        if selected is None:
            parser.error('unknown task')
        output = selected
    else:
        output = compact(index)
    print(json.dumps(output, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
