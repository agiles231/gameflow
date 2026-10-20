import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parent.parent/'scripts/planning.py'
sys.path.insert(0, str(SCRIPT.parent))
spec=importlib.util.spec_from_file_location('planning',SCRIPT);p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        (self.root/'.gameflow/tasks').mkdir(parents=True)
        (self.root/'.gameflow/tasks/TASK-0001.md').write_text('contract')
        self.index={'schema_version':1,'next_id':2,'tasks':[{'id':'TASK-0001','title':'Example','status':'verify','parent':None,'owner':'old','depends_on':[],'contract':'tasks/TASK-0001.md'}]}
        self.planning={'milestones':[{'id':'MILESTONE-0001','title':'MILESTONE-0001','status':'active','depends_on':[],'acceptance':'accept'}],'epics':[{'id':'EPIC-0001','title':'EPIC-0001','milestone':'MILESTONE-0001','status':'active','outcome':'outcome','acceptance':'accept','boundaries':'bounded'}]}
        self.plan={'id':'test-v1','authority':'user','assignments':{'TASK-0001':'EPIC-0001'},'retired':[],'patches':{'TASK-0001':{'kind':'experiment','experiment_outcome':'pending'}},'planning':self.planning}
        (self.root/'.gameflow/tasks/index.json').write_text(json.dumps(self.index));(self.root/'plan.json').write_text(json.dumps(self.plan))
    def command(self,*extra):
        return subprocess.run([sys.executable,str(SCRIPT),'migrate','--project',str(self.root),'--plan',str(self.root/'plan.json'),*extra],capture_output=True)
    def test_preview_apply_backup_idempotence(self):
        path=self.root/'.gameflow/tasks/index.json';before=path.read_bytes()
        self.assertEqual(self.command().returncode,0);self.assertEqual(path.read_bytes(),before)
        self.assertFalse((self.root/'.gameflow/planning.json').exists())
        self.assertEqual(self.command('--apply').returncode,0)
        after=path.read_bytes();self.assertEqual(self.command('--apply').returncode,0);self.assertEqual(path.read_bytes(),after)
        self.assertEqual((self.root/'.gameflow/migrations/test-v1/tasks-index.before.json').read_bytes(),before)
        task=json.loads(after)['tasks'][0];self.assertEqual(task['status'],'verify');self.assertEqual(task['owner'],'old');self.assertEqual(task['kind'],'experiment')
    def test_invalid_reference_no_write(self):
        self.plan['assignments']['TASK-0001']='bad';(self.root/'plan.json').write_text(json.dumps(self.plan))
        self.assertNotEqual(self.command('--apply').returncode,0)
        self.assertFalse((self.root/'.gameflow/migrations').exists())
    def test_changed_task_set_rejected(self):
        self.plan['assignments']['TASK-0002']='EPIC-0001'
        with self.assertRaises(ValueError):p.migrated(self.index,self.plan)
    def test_cycles_rejected(self):
        self.planning['milestones'][0]['depends_on']=['MILESTONE-0001']
        with self.assertRaises(ValueError):p.validate(p.migrated(self.index,self.plan),self.planning,self.root)
    def test_migration_cannot_accept_or_clear_owner(self):
        self.plan['patches']={'TASK-0001':{'status':'done','owner':None}}
        with self.assertRaises(ValueError): p.migrated(self.index,self.plan)
    def test_path_traversal_rejected_without_writes(self):
        self.plan['id']='../escape'
        (self.root/'plan.json').write_text(json.dumps(self.plan))
        self.assertNotEqual(self.command('--apply').returncode,0)
        self.assertFalse((self.root/'.gameflow/migrations').exists())
    def test_invalid_epic_id_rejected(self):
        self.plan['planning']['epics'][0]['id']='../../escape'
        with self.assertRaises(ValueError):p.validate(p.migrated(self.index,self.plan),self.planning,self.root)
    def test_symlink_output_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root/'.gameflow/epics').symlink_to(outside, target_is_directory=True)
            self.assertNotEqual(self.command('--apply').returncode,0)
            self.assertFalse((self.root/'.gameflow/migrations').exists())
            self.assertEqual(list(Path(outside).iterdir()),[])
    def test_prior_planning_backed_up(self):
        path=self.root/'.gameflow/planning.json';path.write_text('previous planning')
        self.assertEqual(self.command('--apply').returncode,0)
        self.assertEqual((self.root/'.gameflow/migrations/test-v1/before/planning.json').read_text(),'previous planning')
    def test_task_creation_and_native_validation(self):
        root = self.root/'full'; root.mkdir()
        scripts=SCRIPT.parent
        def call(name, *args):
            return subprocess.run([sys.executable,str(scripts/name),'--project',str(root),*args],capture_output=True,text=True)
        result=call('init_gameflow.py','--name','Fixture');self.assertEqual(result.returncode,0,result.stderr)
        (root/'.gameflow/planning.json').write_text(json.dumps(self.planning))
        before=(root/'.gameflow/tasks/index.json').read_bytes()
        self.assertNotEqual(call('new_task.py','--title','Bad','--epic','EPIC-9999').returncode,0)
        self.assertEqual((root/'.gameflow/tasks/index.json').read_bytes(),before)
        self.assertFalse((root/'.gameflow/tasks/TASK-0002.md').exists())
        result=call('new_task.py','--title','Trial','--epic','EPIC-0001','--kind','experiment')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        task=json.loads((root/'.gameflow/tasks/index.json').read_text())['tasks'][-1]
        self.assertEqual(task['experiment_outcome'],'pending');self.assertEqual(task['epic'],'EPIC-0001')
        self.assertIn('Stop condition',(root/'.gameflow/tasks/TASK-0002.md').read_text())
        for name in ['validate_gameflow.py','resume_view.py','task_context.py']:
            args=['--task','TASK-0002'] if name=='task_context.py' else []
            result=call(name,*args);self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        data=json.loads((root/'.gameflow/tasks/index.json').read_text());data['tasks'][-1]['epic']='EPIC-9999'
        (root/'.gameflow/tasks/index.json').write_text(json.dumps(data))
        for name in ['validate_gameflow.py','resume_view.py','task_context.py']:
            args=['--task','TASK-0002'] if name=='task_context.py' else []
            result=call(name,*args);self.assertNotEqual(result.returncode,0,name)
    def test_repeat_migration_after_new_tasks_is_noop(self):
        self.assertEqual(self.command('--apply').returncode,0)
        path=self.root/'.gameflow/tasks/index.json';data=json.loads(path.read_text())
        data['tasks'].append(dict(data['tasks'][0],id='TASK-0002'));data['next_id']=3
        path.write_text(json.dumps(data));before=path.read_bytes()
        self.assertEqual(self.command('--apply').returncode,0);self.assertEqual(path.read_bytes(),before)

if __name__=='__main__':unittest.main()
