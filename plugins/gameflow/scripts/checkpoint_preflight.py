#!/usr/bin/env python3
"""Read-only checkpoint identity checks; authority/liveness require coordinator review."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HEX = re.compile(r'^[0-9a-f]{64}$')
STATES = {'planned', 'ready', 'executing', 'verify', 'done', 'blocked', 'deferred'}


def safe_path(value):
    return isinstance(value, str) and bool(value) and not Path(value).is_absolute() and '..' not in Path(value).parts and '\\' not in value and ':' not in value


def hash_map(value):
    return isinstance(value, dict) and all(safe_path(p) and (h is None or isinstance(h, str) and HEX.fullmatch(h)) for p, h in value.items())


def validate_checkpoint(task):
    c = task.get('checkpoint')
    if c is None:
        return []
    errors = []
    if not isinstance(c, dict):
        return ['checkpoint must be an object']
    if type(c.get('version')) is not int or c.get('version') != 1:
        errors.append('checkpoint.version must be 1')
    if c.get('phase') != task.get('status') or not isinstance(c.get('phase'), str) or c.get('phase') not in STATES:
        errors.append('checkpoint.phase must match task status')
    for field in ('authority', 'base_head', 'shared_state_review', 'next_action'):
        if not isinstance(c.get(field), str) or not c[field].strip():
            errors.append(f'checkpoint.{field} must be a nonempty string')
    for field in ('owned_paths', 'preserved_baseline'):
        if not hash_map(c.get(field)):
            errors.append(f'checkpoint.{field} must map confined file paths to SHA256 or null')
    artifacts = c.get('artifact_paths')
    if not isinstance(artifacts, list) or not all(safe_path(p) and isinstance(c.get('owned_paths'), dict) and p in c['owned_paths'] for p in artifacts):
        errors.append('checkpoint.artifact_paths must list owned output files')
    elif task.get('status') == 'done' and not artifacts:
        errors.append('done checkpoint requires artifact_paths')
    if isinstance(c.get('acceptance'), dict) and isinstance(c['acceptance'].get('revision'), dict) and isinstance(artifacts, list):
        if any(not isinstance(p, str) or p not in c['acceptance']['revision'] for p in artifacts):
            errors.append('acceptance revision must cover every artifact path')
    if c.get('owner') is not None and not isinstance(c['owner'], str):
        errors.append('checkpoint.owner must be a string or null')
    if not isinstance(c.get('jobs'), list) or not all(isinstance(j, dict) for j in c.get('jobs', [])):
        errors.append('checkpoint.jobs must be an array of job records')
    counts = c.get('repair_counts')
    if not isinstance(counts, dict) or not all(type(n) is int and n >= 0 for n in counts.values()):
        errors.append('checkpoint.repair_counts must map criteria to nonnegative integers')
    commit = c.get('commit')
    if not isinstance(commit, dict) or commit.get('state') not in ('pending', 'failed', 'committed'):
        errors.append('checkpoint.commit.state must be pending, failed, or committed')
    elif commit['state'] == 'committed' and not isinstance(commit.get('hash'), str):
        errors.append('committed checkpoint requires commit hash')
    acceptance = c.get('acceptance')
    if acceptance is not None and (not isinstance(acceptance, dict) or not hash_map(acceptance.get('revision')) or not all(isinstance(acceptance.get(k), str) and acceptance[k] for k in ('verifier', 'evidence'))):
        errors.append('checkpoint.acceptance requires revision hashes, verifier and evidence')
    if task.get('status') == 'done' and acceptance is None:
        errors.append('done checkpoint requires independent acceptance')
    return errors


def identity(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'path escapes project: {relative}')
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(f'not a file: {relative}')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_task(root, task):
    errors = validate_checkpoint(task)
    c = task.get('checkpoint')
    if errors or c is None:
        return {'task': task['id'], 'action': 'reconcile' if errors else 'legacy-review', 'issues': errors}
    base = c['base_head']
    if not re.fullmatch(r'[0-9a-f]{7,64}', base) or subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', base, 'HEAD'], capture_output=True).returncode:
        errors.append('checkpoint base_head is not in current history')
    for field in ('owned_paths', 'preserved_baseline'):
        for path, expected in c[field].items():
            try:
                if identity(root, path) != expected:
                    errors.append(f'{field} identity changed: {path}')
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
    if c.get('acceptance'):
        for path, expected in c['acceptance']['revision'].items():
            if path not in c['owned_paths'] or c['owned_paths'][path] != expected:
                errors.append(f'acceptance revision differs: {path}')
    if c['commit']['state'] == 'committed':
        revision = c['commit']['hash']
        if not re.fullmatch(r'[0-9a-f]{7,64}', revision):
            errors.append('invalid commit identity')
        else:
            ancestor = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', revision, 'HEAD'], capture_output=True)
            if ancestor.returncode:
                errors.append('checkpoint commit is not in current history')
            for path, expected in c['owned_paths'].items():
                blob = subprocess.run(['git', '-C', str(root), 'show', f'{revision}:{path}'], capture_output=True)
                actual = hashlib.sha256(blob.stdout).hexdigest() if blob.returncode == 0 else None
                if actual != expected:
                    errors.append(f'commit artifact differs: {path}')
    action = 'reconcile' if errors else ('recover-commit' if task['status'] == 'done' and c['commit']['state'] != 'committed' else 'resume')
    return {'task': task['id'], 'action': action, 'issues': errors,
            'operational_review': 'Check live owners, authority, shared deltas and recorded jobs before writes.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--task', help='Explicitly inspect one task, including historical checkpoints')
    args = parser.parse_args()
    tasks = json.loads((args.project / '.gameflow/tasks/index.json').read_text())['tasks']
    selected = [task for task in tasks if task['id'] == args.task] if args.task else [task for task in tasks if task['status'] in ('executing', 'verify', 'blocked') or (task.get('checkpoint') is not None and (validate_checkpoint(task) or task['checkpoint']['commit']['state'] in ('pending', 'failed')))]
    if args.task and not selected:
        parser.error('unknown task')
    results = [inspect_task(args.project, task) for task in selected]
    print(json.dumps(results, indent=2))
    return int(any(result['issues'] for result in results))


if __name__ == '__main__':
    raise SystemExit(main())
