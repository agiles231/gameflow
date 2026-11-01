#!/usr/bin/env python3
"""Behavioral routing fixtures; no live agents, providers or applications."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from model_routing import (ConfigError, DIMENSIONS, evaluate, load_config, read,
                           resolve, validate_config)


def assessment(operation='coding', **changes):
    value = dict(version=1, task_id='TASK-0001', role='implementation',
                 operations=[operation], components=['ui'], tools=['unreal'], tags=[],
                 dimensions={name: 0 for name in DIMENSIONS}, confidence='high',
                 failed_acceptance=False, repair_of=[],
                 evidence={name: 'Fixture: explicit known inputs and objective checks.' for name in
                           ['scope', 'failure_history', 'confidence', *DIMENSIONS]})
    value.update(changes)
    return value


def runtime():
    return {'model_selection': True, 'models': {
        'gpt-6-luna': ['medium'], 'gpt-6.1-terra': ['medium'],
        'gpt-6.1-sol': ['medium', 'high'], 'gpt-6-astra': ['high']}}


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.config, _ = load_config()
        self.runtime = runtime()

    def route(self, value, project=None):
        return resolve(self.config, value, self.runtime, project)

    def test_default_workloads(self):
        cases = [('inventory', 'gpt-6-luna'), ('delivery-check', 'gpt-6-luna'),
                 ('job-polling', 'gpt-6-luna'), ('visual-inspection', 'gpt-6.1-terra'),
                 ('material-hookup', 'gpt-6.1-terra'), ('image-edit', 'gpt-6.1-terra'),
                 ('coding', 'gpt-6.1-sol'), ('scripting', 'gpt-6.1-sol'),
                 ('integration', 'gpt-6.1-sol'), ('mesh-generation', 'gpt-6-astra'),
                 ('animation-production', 'gpt-6-astra'), ('animation-evaluation', 'gpt-6-astra')]
        for operation, model in cases:
            with self.subTest(operation=operation):
                self.assertEqual(self.route(assessment(operation))['model'], model)

    def test_application_name_does_not_force_astra(self):
        for tool in ['blender', 'unreal', 'gimp', 'meshy']:
            self.assertEqual(self.route(assessment('job-polling', tools=[tool]))['model'], 'gpt-6-luna')

    def test_complexity_and_mixed_components(self):
        a = assessment('inventory')
        a['dimensions']['complexity'] = 2
        self.assertEqual(self.route(a)['profile'], 'engineering-high')
        a['dimensions']['complexity'] = 3
        self.assertEqual(self.route(a)['profile'], 'demanding')
        a = assessment(operations=['visual-inspection', 'scripting'])
        self.assertEqual(self.route(a)['profile'], 'engineering')
        a = assessment(operations=['inventory', 'unknown-operation'])
        self.assertEqual(self.route(a)['profile'], 'engineering')
        a = assessment('inventory', confidence='low')
        self.assertEqual(self.route(a)['profile'], 'demanding')
        a = assessment('inventory'); a['dimensions']['size'] = 3
        self.assertEqual(self.route(a)['profile'], 'engineering')  # volume alone is not Astra

    def test_repair_overrides_rules_and_parent_child(self):
        for changes in [{'failed_acceptance': True}, {'repair_of': ['TASK-0042']}]:
            result = self.route(assessment('inventory', **changes))
            self.assertEqual(result['model'], 'gpt-6-astra')
            self.assertTrue(result['repair_escalated'])
        self.assertEqual(self.route(assessment('delivery-check', role='verification',
                                               failed_acceptance=True))['model'], 'gpt-6-luna')

    def test_explicit_configurable_repair_target(self):
        self.config['repair_profile'] = 'engineering-high'
        self.assertEqual(self.route(assessment(failed_acceptance=True))['model'], 'gpt-6.1-sol')

    def test_fallback_is_explicit_and_repair_blocks(self):
        del self.runtime['models']['gpt-6-luna']
        result = self.route(assessment('inventory'))
        self.assertEqual(result['model'], 'gpt-6.1-sol')
        self.assertTrue(result['fallback_used'])
        del self.runtime['models']['gpt-6-astra']
        self.assertEqual(self.route(assessment(failed_acceptance=True))['status'], 'blocked')
        self.runtime['model_selection'] = False
        self.assertEqual(self.route(assessment())['status'], 'blocked')

    def test_unsupported_reasoning_is_not_silently_changed(self):
        self.runtime['models']['gpt-6-astra'] = ['medium']
        self.assertEqual(self.route(assessment(failed_acceptance=True))['status'], 'blocked')

    def test_custom_component_rule_and_ties(self):
        custom = dict(id='physics', description='Complex vehicle physics', priority=1000,
                      match={'components_any': ['vehicle-physics'], 'roles': ['implementation'],
                             'tools_any': ['unreal'], 'tags_all': ['vehicle'],
                             'dimensions_min': {'coupling': 1}}, profile='demanding')
        self.config['rules'].append(custom)
        a = assessment(components=['vehicle-physics'], tags=['vehicle'])
        a['dimensions']['coupling'] = 1
        self.assertEqual(self.route(a)['profile'], 'demanding')
        a['tags'] = []
        self.assertEqual(self.route(a)['profile'], 'engineering')
        a['tags'] = ['vehicle']
        self.config['rules'].append(dict(custom, id='conflict', profile='focused'))
        self.assertEqual(self.route(a)['status'], 'blocked')
        self.config['rules'][-1]['profile'] = 'demanding'
        self.assertEqual(self.route(a)['status'], 'selected')

    def test_bad_configuration_and_assessments(self):
        for mutate in [lambda c: c.update(version=2), lambda c: c.update(typo=True),
                       lambda c: c.update(default_profile='missing'),
                       lambda c: c['rules'].append(copy.deepcopy(c['rules'][0])),
                       lambda c: c['rules'][0].update(match={'dimensions_min': {'bogus': 1}}),
                       lambda c: c['rules'][0].update(match={'dimensions_min': {'size': 3},
                                                           'dimensions_max': {'size': 1}})]:
            c = copy.deepcopy(self.config); mutate(c)
            with self.assertRaises(ConfigError):
                validate_config(c)
        for mutate in [lambda a: a.pop('confidence'), lambda a: a['dimensions'].update(size=True),
                       lambda a: a['dimensions'].update(size=4), lambda a: a.update(roles='verification'),
                       lambda a: a['evidence'].update(complexity='')]:
            a = assessment(); mutate(a)
            with self.assertRaises(ConfigError):
                self.route(a)

    def test_pure_deterministic_replay_and_policy_fingerprint(self):
        a = assessment(); before = copy.deepcopy((self.config, a, self.runtime))
        first = self.route(a)
        self.assertEqual(first, self.route(a))
        self.assertEqual(before, (self.config, a, self.runtime))
        cases = [dict(id='ordinary-code', assessment=a, runtime=self.runtime,
                      expected={'status': 'selected', 'model': 'gpt-6.1-sol'})]
        self.assertTrue(evaluate(self.config, cases)['passed'])
        self.config['profiles']['engineering']['candidates'][0]['model'] = 'gpt-6-astra'
        self.assertFalse(evaluate(self.config, cases)['passed'])
        self.assertNotEqual(first['config_sha256'], self.route(a)['config_sha256'])

    def test_legacy_absence_invalid_files_and_no_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            default, source = load_config(project)
            self.assertEqual(default, self.config)
            self.assertFalse(list(project.iterdir()))
            path = project / '.gameflow/tools/model-routing.json'
            path.parent.mkdir(parents=True)
            for text in ['{}', '{"version":1,"version":1}', '{"version":NaN}', 'not JSON']:
                path.write_text(text)
                with self.assertRaises(ConfigError):
                    load_config(project)
                self.assertEqual(path.read_text(), text)
            path.unlink()
            path.symlink_to(project / 'absent')
            with self.assertRaises(OSError):
                load_config(project)

    def test_initializer_preserves_custom_policy_and_unrelated_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            path = project / '.gameflow/tools/model-routing.json'
            path.parent.mkdir(parents=True)
            self.config['default_profile'] = 'demanding'
            original = (json.dumps(self.config, indent=3) + '\r\n').encode()
            path.write_bytes(original)
            unrelated = project / 'user-notes.txt'
            unrelated.write_bytes(b'Preserve my work\r\n')
            for _ in range(2):
                process = subprocess.run([sys.executable, str(ROOT / 'scripts/init_gameflow.py'),
                                          '--project', tmp, '--name', 'Routing'], capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertEqual(path.read_bytes(), original)
                self.assertEqual(unrelated.read_bytes(), b'Preserve my work\r\n')
            custom, _ = load_config(project)
            self.assertEqual(resolve(custom, assessment('unknown'), self.runtime)['profile'], 'demanding')

    def test_persisted_repair_and_project_validator(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            process = subprocess.run([sys.executable, str(ROOT / 'scripts/init_gameflow.py'),
                                      '--project', tmp, '--name', 'Routing'], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            path = project / '.gameflow/tasks/index.json'
            index = read(path)
            task = index['tasks'][0]
            task.update(status='executing', checkpoint=dict(
                version=1, phase='executing', authority='Fixture', base_head='a'*40, owner=None,
                artifact_paths=[], owned_paths={}, shared_state_review='None', preserved_baseline={},
                jobs=[], repair_counts={'criterion': 1}, next_action='Repair', acceptance=None,
                commit={'state': 'pending', 'hash': None}))
            path.write_text(json.dumps(index))
            before = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
            result = self.route(assessment('inventory'), project)
            self.assertEqual(result['model'], 'gpt-6-astra')
            self.assertTrue(result['repair_signals'])
            after = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
            self.assertEqual(before, after)
            from validate_gameflow import validate_project
            self.assertFalse(validate_project(project)[0])
            config_path = project / '.gameflow/tools/model-routing.json'
            config_path.write_text('{}')
            self.assertTrue(any('model-routing' in e for e in validate_project(project)[0]))
            config_path.unlink()
            self.assertFalse(validate_project(project)[0])

    def test_missing_task_and_invalid_checkpoint_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            subprocess.run([sys.executable, str(ROOT / 'scripts/init_gameflow.py'),
                            '--project', tmp, '--name', 'Routing'], check=True, capture_output=True)
            with self.assertRaises(ConfigError):
                self.route(assessment(task_id='TASK-9999'), project)
            path = project / '.gameflow/tasks/index.json'
            index = read(path)
            index['tasks'][0]['checkpoint'] = {'repair_counts': {'criterion': -1}}
            path.write_text(json.dumps(index))
            with self.assertRaises(ConfigError):
                self.route(assessment(), project)

    def test_cli_default_resolve_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, r, cases = (Path(tmp) / n for n in ['a.json', 'r.json', 'cases.json'])
            a.write_text(json.dumps(assessment()))
            r.write_text(json.dumps(self.runtime))
            cases.write_text(json.dumps([dict(id='code', assessment=assessment(), runtime=self.runtime,
                                             expected={'status':'selected', 'model':'gpt-6.1-sol'})]))
            for args in [('defaults',), ('validate',), ('resolve', '--assessment', str(a), '--runtime', str(r)),
                         ('evaluate', '--cases', str(cases))]:
                p = subprocess.run([sys.executable, str(ROOT/'scripts/model_routing.py'), *args],
                                   capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stderr)
                json.loads(p.stdout)
            a.write_text(json.dumps(assessment(failed_acceptance=True)))
            r.write_text(json.dumps({'model_selection': True, 'models': {}}))
            p = subprocess.run([sys.executable, str(ROOT/'scripts/model_routing.py'),
                                'resolve', '--assessment', str(a), '--runtime', str(r)],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 3)
            self.assertEqual(json.loads(p.stdout)['status'], 'blocked')


if __name__ == '__main__':
    unittest.main()
