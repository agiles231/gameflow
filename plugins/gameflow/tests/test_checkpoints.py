#!/usr/bin/env python3
"""Recovery identity regression tests in an isolated Git worktree."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from checkpoint_preflight import identity, inspect_task, validate_checkpoint


def main():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        def git(*args):
            return subprocess.run(['git', '-C', directory, *args], check=True, capture_output=True, text=True).stdout.strip()
        git('init'); git('config', 'user.name', 'Fixture'); git('config', 'user.email', 'fixture@example.test')
        (root / 'artifact').write_text('accepted')
        git('add', 'artifact'); git('commit', '-m', 'artifact')
        commit = git('rev-parse', 'HEAD')
        (root / 'notes').write_text('user work')
        revision = {'artifact': identity(root, 'artifact')}
        cp = dict(version=1, phase='verify', authority='existing request', base_head=commit,
                  owner=None, owned_paths=revision, artifact_paths=['artifact'], shared_state_review='reviewed serialized delta',
                  preserved_baseline={'notes': identity(root, 'notes')}, jobs=[{'id': 'existing-job', 'recovery': 'poll'}],
                  repair_counts={'criterion': 1}, next_action='verify', acceptance=None,
                  commit={'state': 'pending', 'hash': None})
        task = {'id': 'TASK-0001', 'status': 'verify', 'checkpoint': cp}
        before = copy.deepcopy(task)
        assert inspect_task(root, task)['action'] == 'resume'  # uncommitted verify + provider restart
        assert task == before  # jobs, ownership, repair counters never reset
        assert (root / 'notes').read_text() == 'user work'
        task['status'] = cp['phase'] = 'done'
        cp['acceptance'] = {'revision': revision.copy(), 'verifier': 'other-session', 'evidence': 'result.json'}
        for state in ('pending', 'failed'):
            cp['commit']['state'] = state
            assert inspect_task(root, task)['action'] == 'recover-commit'
        cp['commit'] = {'state': 'committed', 'hash': commit}
        assert inspect_task(root, task)['action'] == 'resume'
        (root / 'artifact').write_text('changed after acceptance')
        assert inspect_task(root, task)['action'] == 'reconcile'
        cp['owned_paths']['artifact'] = identity(root, 'artifact')
        assert any('acceptance revision' in s for s in inspect_task(root, task)['issues'])
        (root / 'artifact').write_text('accepted'); cp['owned_paths'] = revision = {'artifact': identity(root, 'artifact')}
        (root / 'notes').write_text('later user edit')
        assert inspect_task(root, task)['action'] == 'reconcile'
        assert (root / 'notes').read_text() == 'later user edit'
        # Normal preflight ignores historical committed tasks after later legitimate edits.
        (root / '.gameflow/tasks').mkdir(parents=True)
        (root / '.gameflow/tasks/index.json').write_text(json.dumps({'tasks': [task, {'id': 'TASK-0002', 'status': 'done'}]}))
        script = Path(__file__).resolve().parents[1] / 'scripts/checkpoint_preflight.py'
        result = subprocess.run([sys.executable, str(script), '--project', directory], capture_output=True, text=True)
        assert result.returncode == 0 and json.loads(result.stdout) == []
        # Shared mixed edits and liveness are explicitly operational, never auto-cleared by this helper.
        (root / 'notes').write_text('user work'); cp['owner'] = 'potentially-live'
        assert 'live owners' in inspect_task(root, task)['operational_review']
        assert cp['owner'] == 'potentially-live'
        malformed = copy.deepcopy(task); malformed['checkpoint']['acceptance']['revision'] = {}
        assert validate_checkpoint(malformed)
        malformed = copy.deepcopy(task); malformed['checkpoint']['base_head'] = 'not-a-commit'
        assert inspect_task(root, malformed)['action'] == 'reconcile'
        for field, value in [('owned_paths', {'../outside': None}), ('repair_counts', {'a': -1}),
                             ('commit', {'state': 'committed'}), ('phase', 'executing'), ('jobs', None)]:
            malformed = copy.deepcopy(task); malformed['checkpoint'][field] = value
            assert validate_checkpoint(malformed), field
        assert validate_checkpoint({'id': 'TASK-0002', 'status': 'done'}) == []
        assert inspect_task(root, {'id': 'TASK-0002', 'status': 'done'})['action'] == 'legacy-review'
    print('Checkpoint identity and recovery tests passed.')


if __name__ == '__main__':
    main()
