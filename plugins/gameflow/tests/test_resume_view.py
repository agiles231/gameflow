#!/usr/bin/env python3
"""Check compact recovery visibility, complete-record access and fail-closed graphs."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from resume_view import compact, recovery_reasons


def main():
    with tempfile.TemporaryDirectory() as folder:
        subprocess.run([sys.executable, str(ROOT / 'scripts/init_gameflow.py'),
                        '--project', folder, '--name', 'Resume fixture'], check=True, capture_output=True)
        path = Path(folder) / '.gameflow/tasks/index.json'
        index = json.loads(path.read_text())
        template = index['tasks'][0]
        statuses = ['done', 'planned', 'ready', 'executing', 'verify', 'blocked', 'deferred']
        index['tasks'] = [dict(template, id=f'TASK-{i:04d}', status=status,
                               depends_on=['TASK-0001'] if i > 1 else [],
                               execution_mode='interactive' if status == 'blocked' else 'autonomous',
                               priority=100-i) for i, status in enumerate(statuses, 1)]
        index['next_id'] = 8
        original = json.dumps(index)
        path.write_text(original)
        def run(*args):
            return subprocess.run([sys.executable, str(ROOT / 'scripts/resume_view.py'),
                                   '--project', folder, *args], capture_output=True, text=True)
        result = run()
        assert result.returncode == 0, result.stdout + result.stderr
        rows = json.loads(result.stdout)['tasks']
        assert [r['status'] for r in rows] == statuses[1:]
        assert all(r['dependencies'] == {'TASK-0001': 'done'} for r in rows)
        assert rows[-2]['execution_mode'] == 'interactive'
        assert [r['priority'] for r in rows] == list(range(98, 92, -1))
        assert json.loads(run('--task', 'TASK-0001').stdout) == index['tasks'][0]
        assert run('--task', 'TASK-9999').returncode != 0
        assert path.read_text() == original
        for malformed in (None, {}, {'tasks': [None]}, dict(index, next_id=1)):
            path.write_text(json.dumps(malformed))
            result = run()
            assert result.returncode == 1 and 'errors' in json.loads(result.stdout), result
            assert 'Traceback' not in result.stderr
        cyclic = copy.deepcopy(index)
        cyclic['tasks'][0]['depends_on'] = ['TASK-0002']
        path.write_text(json.dumps(cyclic))
        assert run().returncode == 1
        path.write_text('{')
        assert run().returncode == 1

    done = dict(template, status='done', checkpoint={'commit': {'state': 'committed'},
                                                    'owner': None, 'jobs': []})
    assert recovery_reasons(done) == []
    for state in ('pending', 'failed'):
        task = copy.deepcopy(done)
        task['checkpoint']['commit']['state'] = state
        assert 'uncommitted' in recovery_reasons(task)
        assert compact({'tasks': [task]})['tasks']
    for field in ('owner', 'checkpoint'):
        task = copy.deepcopy(done)
        if field == 'owner': task['owner'] = 'worker'
        else: task['checkpoint']['owner'] = 'worker'
        assert 'owner' in recovery_reasons(task)
    for status in ('SUCCEEDED', 'completed', 'FAILED', 'CANCELED'):
        task = copy.deepcopy(done)
        task['checkpoint']['jobs'] = [{'status': status}]
        assert 'jobs' not in recovery_reasons(task)
    for job in ({}, {'status': 'RUNNING'}, {'status': None}):
        task = copy.deepcopy(done)
        task['checkpoint']['jobs'] = [job]
        assert 'jobs' in recovery_reasons(task)
    print('Resume view tests passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
