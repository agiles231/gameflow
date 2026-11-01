#!/usr/bin/env python3
"""Decision behavior and compatibility; no live models, application or provider calls."""
from copy import deepcopy
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from autonomy import (calibrate, digest, event, load_config, read, record_event,
                      report, schedule, triage, validate_config, validate_issues)
from validate_gameflow import validate_project


def assessment():
    artifacts = {'Content/Fixture.asset': 'a' * 64}
    return dict(version=1, task_id='TASK-0001', category='engine-import', artifacts=artifacts,
                criteria=[dict(id=tier, tier=tier, required=True,
                               result='fail' if tier == 'final' else 'pass',
                               independent=True, revision=digest(artifacts), evidence=['checks/import.json'])
                          for tier in ('core', 'integration', 'final')],
                propagation_risk=0, deferral_cost=0, isolated=True, recoverable=True,
                repair_authorized=True, repair_allowance_remaining=True,
                new_hypothesis=None, hypothesis_evidence=[], affected_dependencies=['TASK-0002'],
                issue_ids=['ISSUE-1'], evidence=['tasks/TASK-0001.md'])


def issue(n=1, **changes):
    value = dict(id=f'ISSUE-{n}', task_id='TASK-0001', title='Incomplete package',
                 status='open', impact=1, created='2026-10-01',
                 affected_dependencies=[], next_action='Check missing dependency',
                 revisit_when='Before package acceptance', evidence=['tasks/TASK-0001.md'],
                 artifacts={'Content/Fixture.asset': 'a' * 64}, repair_task=f'TASK-{n:04}', eligible=True)
    value.update(changes)
    return value


def outcome(n=1, **changes):
    value = dict(id=f'OUTCOME-{n}', task_id=f'TASK-{n:04}', category='engine-import',
                 completed=f'2026-10-{n:02}', success=True, first_pass_success=True,
                 regression=False, independent=True, model='gpt-6.1-sol', reasoning_effort='medium',
                 artifacts={'Content/Fixture.asset': 'a' * 64}, evidence=['checks/import.json'],
                 rework_minutes=0, elapsed_minutes=10, tokens=100)
    value.update(changes)
    return value


class AutonomyTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()

    def test_failed_final_can_be_preserved_without_acceptance(self):
        result = triage(self.config, assessment())
        self.assertEqual(result['action'], 'preserve-and-schedule')
        self.assertFalse(result['eligible_for_acceptance'])
        self.assertFalse(result['dependency_satisfied'])
        self.assertEqual(result['unresolved_criteria'], ['final'])

    def test_repair_requires_new_hypothesis_authority_and_allowance(self):
        a = assessment()
        a.update(propagation_risk=3, new_hypothesis='Missing package reference', hypothesis_evidence=['checks/package.log'])
        self.assertEqual(triage(self.config, a)['action'], 'repair-now')
        for field, value in [('new_hypothesis', None), ('new_hypothesis', ' '),
                             ('hypothesis_evidence', []), ('repair_authorized', False),
                             ('repair_allowance_remaining', False)]:
            candidate = dict(a, **{field: value})
            self.assertEqual(triage(self.config, candidate)['action'], 'investigate-or-escalate')

    def test_failed_core_risky_reuse_and_expensive_deferral_need_investigation(self):
        for field, value in [('recoverable', False), ('isolated', False), ('deferral_cost', 3)]:
            a = dict(assessment(), **{field: value})
            self.assertEqual(triage(self.config, a)['action'], 'investigate-or-escalate')
        a = assessment(); a['criteria'][0]['result'] = 'fail'
        self.assertEqual(triage(self.config, a)['action'], 'investigate-or-escalate')

    def test_provisional_is_explicit_and_never_satisfies_dependencies(self):
        self.assertFalse(triage(self.config, assessment())['provisional_integration_eligible'])
        self.config['allow_provisional_integration'] = True
        result = triage(self.config, assessment())
        self.assertTrue(result['provisional_integration_eligible'])
        self.assertFalse(result['dependency_satisfied'])
        a = assessment(); a['criteria'][1]['revision'] = 'b' * 64
        self.assertFalse(triage(self.config, a)['provisional_integration_eligible'])
        a = assessment(); a['propagation_risk'] = 1
        self.assertFalse(triage(self.config, a)['provisional_integration_eligible'])

    def test_exact_revision_and_independence_gate_acceptance(self):
        a = assessment()
        for c in a['criteria']: c['result'] = 'pass'
        self.assertTrue(triage(self.config, a)['eligible_for_acceptance'])
        for field, value in [('independent', False), ('revision', 'b' * 64), ('result', 'unknown')]:
            candidate = deepcopy(a); candidate['criteria'][0][field] = value
            self.assertFalse(triage(self.config, candidate)['eligible_for_acceptance'])
        a['artifacts']['Content/Fixture.asset'] = 'b' * 64
        self.assertFalse(triage(self.config, a)['eligible_for_acceptance'])

    def test_legacy_untiered_criteria_remain_required(self):
        a = assessment()
        for c in a['criteria']:
            c.pop('tier'); c.pop('required')
        self.assertFalse(triage(self.config, a)['eligible_for_acceptance'])
        self.assertEqual(triage(self.config, a)['action'], 'investigate-or-escalate')
        for c in a['criteria']: c['result'] = 'pass'
        self.assertTrue(triage(self.config, a)['eligible_for_acceptance'])

    def test_failures_require_actionable_issues_and_invalid_policy_rejected(self):
        a = assessment(); a['issue_ids'] = []
        with self.assertRaises(ValueError): triage(self.config, a)
        a = assessment(); a['criteria'].append(deepcopy(a['criteria'][0]))
        with self.assertRaises(ValueError): triage(self.config, a)
        self.config['backlog']['soft_limit'] = 100
        with self.assertRaises(ValueError): validate_config(self.config)
        with self.assertRaises(ValueError): validate_issues({'version': 1, 'issues': [issue(next_action='')]})

    def test_issue_priority_uses_impact_dependencies_and_age(self):
        values = [issue(1), issue(2, impact=2), issue(3, affected_dependencies=['TASK-0004'] * 0),
                  issue(4, created='2025-01-01'), issue(5, status='resolved', impact=3)]
        values[2]['affected_dependencies'] = ['TASK-0005', 'TASK-0006']
        result = schedule(self.config, {'version': 1, 'issues': values}, date(2026, 11, 1), 4)
        self.assertEqual(result['issues'][0]['id'], 'ISSUE-4')
        self.assertEqual(result['open_issues'], 4)
        self.assertEqual(result['reserved_repair_slots'], 2)
        self.assertEqual(result['new_feature_limit'], 2)
        self.assertEqual(result['repair_tasks'][0], 'TASK-0004')

    def test_soft_hard_limits_blocked_repairs_and_duplicate_tasks(self):
        values = [issue(i, eligible=False) for i in range(5)]
        result = schedule(self.config, {'version': 1, 'issues': values}, date(2026, 11, 1), 4)
        self.assertEqual((result['new_feature_limit'], result['reserved_repair_slots']), (1, 3))
        self.assertEqual(result['repair_tasks'], [])
        values += [issue(i, repair_task='TASK-0009') for i in range(5, 10)]
        result = schedule(self.config, {'version': 1, 'issues': values}, date(2026, 11, 1), 4)
        self.assertEqual((result['new_feature_limit'], result['reserved_repair_slots']), (0, 4))
        self.assertEqual(result['repair_tasks'], ['TASK-0009'])
        with self.assertRaises(ValueError): schedule(self.config, {'version': 1, 'issues': [issue(created='2027-01-01')]}, date(2026, 11, 1), 2)
        with self.assertRaises(ValueError): schedule(self.config, {'version': 1, 'issues': []}, date.today(), -1)

    def test_calibration_is_independent_category_local_and_repaired_success_not_first_pass(self):
        outcomes = {'version': 1, 'outcomes': [outcome(i) for i in range(1, 6)]}
        result = calibrate(self.config, outcomes, 'engine-import')
        self.assertEqual(result['autonomy'], 'bounded-reversible')
        self.assertFalse(result['permissions_changed'])
        self.assertEqual(calibrate(self.config, outcomes, 'animation')['autonomy'], 'assisted')
        outcomes['outcomes'][0]['first_pass_success'] = False
        self.assertEqual(calibrate(self.config, outcomes, 'engine-import')['autonomy'], 'assisted')
        outcomes['outcomes'][0]['first_pass_success'] = True
        outcomes['outcomes'][0]['regression'] = True
        self.assertEqual(calibrate(self.config, outcomes, 'engine-import')['autonomy'], 'assisted')
        outcomes['outcomes'][0]['independent'] = False
        self.assertEqual(calibrate(self.config, outcomes, 'engine-import')['samples'], 4)
        outcomes['outcomes'].append(dict(outcome(1), id='duplicate-task'))
        with self.assertRaises(ValueError): calibrate(self.config, outcomes, 'engine-import')

    def test_reports_cover_named_missing_interrupted_and_preserved_selections(self):
        run = dict(version=1, run_id='RUN-1', objective='Build playable slice',
                   selected=[dict(task_id=f'TASK-{i:04}', deliverable=name) for i, name in enumerate(['Forest trail', 'Bear import', 'Menu'], 1)],
                   results=[dict(task_id='TASK-0001', outcome='preserved', summary='Trail usable; lighting failed', next_action='Repair lighting', evidence=['checks/trail.json'], commit='a' * 40),
                            dict(task_id='TASK-0002', outcome='interrupted', summary='Import parked', next_action='Resume recorded job', evidence=[], commit=None)], delivery='Local only; selected work remains unfinished')
        self.assertIn('Forest trail', report(run, 'opening'))
        closing = report(run, 'closing')
        self.assertIn('Menu (TASK-0003): unfinished', closing)
        self.assertIn('Bear import (TASK-0002): interrupted', closing)
        self.assertIn('Trail usable; lighting failed', closing)
        run['selected'].pop(0)
        with self.assertRaises(ValueError): report(run, 'closing')

    def test_audit_is_read_only_until_record_idempotent_and_time_bound(self):
        a = assessment()
        value = event('triage', self.config, a, triage(self.config, a), 'RUN-1')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root / '.gameflow/tasks').mkdir(parents=True)
            (root / '.gameflow/tasks/index.json').write_text('{}')
            self.assertFalse((root / '.gameflow/events').exists())
            target = root / record_event(root, value)
            before = target.read_bytes()
            self.assertIn('recorded_at', read(target))
            self.assertEqual(read(target)['run_id'], 'RUN-1')
            record_event(root, value)
            self.assertEqual(before, target.read_bytes())
            value['decision']['reason'] = 'tampered'
            with self.assertRaises(ValueError): record_event(root, value)

    def test_cli_read_only_invalid_input_and_record(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'assessment.json'
            source.write_text(json.dumps(assessment()))
            command = [sys.executable, str(ROOT / 'scripts/autonomy.py'), 'triage', '--input', str(source)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(list(root.iterdir()), [source])
            self.assertEqual(json.loads(result.stdout)['decision']['action'], 'preserve-and-schedule')
            result = subprocess.run(command + ['--record'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            source.write_text('{"version":NaN}')
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)

    def test_fresh_enabled_legacy_absent_and_authored_policy_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.assertFalse(load_config(root)['enabled'])
            command = [sys.executable, str(ROOT / 'scripts/init_gameflow.py'), '--project', str(root), '--name', 'Fixture']
            subprocess.run(command, check=True, capture_output=True)
            self.assertTrue(load_config(root)['enabled'])
            policy = root / '.gameflow/tools/autonomy.json'
            custom = load_config(root); custom['backlog']['hard_limit'] = 50
            policy.write_text(json.dumps(custom)); before = policy.read_bytes()
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(policy.read_bytes(), before)
            policy.unlink()
            graph = (root / '.gameflow/tasks/index.json').read_bytes()
            subprocess.run(command, check=True, capture_output=True)
            self.assertFalse(policy.exists())
            self.assertFalse(load_config(root)['enabled'])
            self.assertEqual((root / '.gameflow/tasks/index.json').read_bytes(), graph)
            self.assertEqual(validate_project(root)[0], [])
            result = triage(load_config(root), assessment())
            self.assertEqual(result['action'], 'legacy-policy')
            policy.write_text('{}')
            with self.assertRaises(ValueError): load_config(root)
            self.assertTrue(validate_project(root)[0])


if __name__ == '__main__':
    unittest.main()
