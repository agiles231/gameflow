"""Exercise output retention and branch cleanup against disposable Git repositories."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


def run(*args, cwd=None, check=True):
    return subprocess.run(args, cwd=cwd, check=check, text=True, capture_output=True)


class RetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name); self.project = self.base/'project'; self.project.mkdir()
        run('git', 'init', '-b', 'demo', str(self.project))
        run('git', 'config', 'user.email', 'fixture@example.invalid', cwd=self.project)
        run('git', 'config', 'user.name', 'Fixture', cwd=self.project)
        run(sys.executable, str(ROOT/'scripts/init_gameflow.py'), '--project', str(self.project), '--name', 'Fixture')

    def test_outputs_ignored_accepted_assets_and_conclusions_tracked(self):
        ignored = ['Artifacts/preview.glb', 'Experiments/variant.blend', '.gameflow/verification/results/check.json', '.gameflow/verification/temporary/view.png']
        tracked = ['Art/Accepted/tree.blend', 'Content/tree.uasset', '.gameflow/tasks/TASK-0001.md', '.gameflow/verification/standards.md']
        for name in ignored + tracked:
            path = self.project/name; path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists(): path.write_text('fixture')
            result = run('git', 'check-ignore', '-q', name, cwd=self.project, check=False)
            self.assertEqual(result.returncode, 0 if name in ignored else 1, name)
        run('git', 'add', '.', cwd=self.project)
        report = run(sys.executable, str(ROOT/'scripts/artifact_audit.py'), '--project', str(self.project))
        data = json.loads(report.stdout)
        self.assertNotIn('Artifacts', data['groups']); self.assertIn('Art', data['groups'])

    def test_cleanup_isolated_and_preserves_other_refs(self):
        run('git', 'add', '.', cwd=self.project); run('git', 'commit', '-m', 'fixture', cwd=self.project)
        run('git', 'branch', 'archive', cwd=self.project)
        before = run('git', 'show-ref', cwd=self.project).stdout
        bundle = self.base/'backup.bundle'
        run('git', 'bundle', 'create', str(bundle), '--all', cwd=self.project)
        paths = self.base/'paths.txt'; paths.write_text('Artifacts/\n')
        # Test orchestration with a no-op supplied filter, not a real history rewrite.
        tool = self.base/'filter.py'; tool.write_text('import sys\nassert "--paths-from-file" in sys.argv\n')
        out = self.base/'candidate.git'
        cmd = [sys.executable, str(ROOT/'scripts/prepare_history_cleanup.py'), '--project', str(self.project), '--branch', 'demo', '--backup', str(bundle), '--output', str(out), '--filter-repo', str(tool), '--paths-file', str(paths)]
        run(*cmd)
        report = json.loads((out/'cleanup-report.json').read_text())
        self.assertTrue(report['tip_tree_identical']); self.assertFalse(report['remote_updated'])
        self.assertEqual(run('git', 'show-ref', cwd=self.project).stdout, before)
        self.assertEqual(run('git', 'for-each-ref', '--format=%(refname)', cwd=out).stdout.strip(), 'refs/heads/demo')
        self.assertNotEqual(run(*cmd, check=False).returncode, 0)

    def test_cleanup_rejects_changed_retained_tip(self):
        run('git', 'add', '.', cwd=self.project); run('git', 'commit', '-m', 'fixture', cwd=self.project)
        bundle = self.base/'backup.bundle'; run('git', 'bundle', 'create', str(bundle), '--all', cwd=self.project)
        paths=self.base/'paths.txt'; paths.write_text('Artifacts/\n')
        tool=self.base/'filter.py'
        tool.write_text('import subprocess,os\nenv=dict(os.environ,GIT_AUTHOR_NAME="Fixture",GIT_AUTHOR_EMAIL="fixture@example.invalid",GIT_COMMITTER_NAME="Fixture",GIT_COMMITTER_EMAIL="fixture@example.invalid")\ntree=subprocess.check_output(["git","hash-object","-t","tree","-w","--stdin"],input=b"").decode().strip()\ncommit=subprocess.check_output(["git","commit-tree",tree,"-m","bad filter"],env=env).decode().strip()\nsubprocess.run(["git","update-ref","refs/heads/demo",commit],check=True)\n')
        out=self.base/'candidate.git'
        result=run(sys.executable,str(ROOT/'scripts/prepare_history_cleanup.py'),'--project',str(self.project),'--branch','demo','--backup',str(bundle),'--output',str(out),'--filter-repo',str(tool),'--paths-file',str(paths),check=False)
        self.assertNotEqual(result.returncode,0);self.assertIn('Retained tip tree changed',result.stderr)
        self.assertFalse((out/'cleanup-report.json').exists())


if __name__ == '__main__': unittest.main()
