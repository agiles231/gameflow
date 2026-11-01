#!/usr/bin/env python3
"""Optional evidence-based decisions and reports. No agent dispatch or acceptance writes."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
import math
from pathlib import Path
import sys

from model_routing import (STRING, STRINGS, SCORE, array, digest, enum, obj,
                          read, validate)

DEFAULT = Path(__file__).resolve().parents[1] / 'templates/gameflow/tools/autonomy.json'
VERSION = {'type': 'integer', 'const': 1}
BOOL = {'type': 'boolean'}
NATURAL = {'type': 'integer', 'minimum': 0}
POSITIVE = {'type': 'integer', 'minimum': 1}
HASH = {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}
CONFIG = obj({
    'version': VERSION, 'enabled': BOOL, 'allow_provisional_integration': BOOL,
    'repair_risk_threshold': SCORE, 'repair_deferral_cost_threshold': SCORE,
    'backlog': obj({'soft_limit': POSITIVE, 'hard_limit': POSITIVE,
                    'repair_fraction': {'type': 'number', 'exclusiveMinimum': 0, 'maximum': 1},
                    'max_new_features': NATURAL, 'age_days_per_point': POSITIVE}),
    'calibration': obj({'window': POSITIVE, 'minimum_samples': POSITIVE,
                        'minimum_success_rate': {'type': 'number', 'minimum': 0, 'maximum': 1},
                        'maximum_regressions': NATURAL}),
})
ARTIFACTS = {'type': 'object', 'minProperties': 1, 'additionalProperties': HASH}
CRITERION = obj({
    'id': STRING, 'tier': enum(['core', 'integration', 'final', 'polish']),
    'required': BOOL, 'result': enum(['pass', 'fail', 'unknown']),
    'independent': BOOL, 'revision': HASH, 'evidence': dict(STRINGS, minItems=1),
}, ['id', 'result', 'independent', 'revision', 'evidence'])
ASSESSMENT = obj({
    'version': VERSION, 'task_id': STRING, 'category': STRING,
    'artifacts': ARTIFACTS, 'criteria': array(CRITERION, 1),
    'propagation_risk': SCORE, 'deferral_cost': SCORE,
    'isolated': BOOL, 'recoverable': BOOL, 'repair_authorized': BOOL,
    'repair_allowance_remaining': BOOL, 'new_hypothesis': {'type': ['string', 'null']},
    'hypothesis_evidence': STRINGS, 'affected_dependencies': STRINGS,
    'issue_ids': STRINGS, 'evidence': dict(STRINGS, minItems=1),
})
ISSUE = obj({
    'id': STRING, 'task_id': STRING, 'title': STRING,
    'status': enum(['open', 'resolved']), 'impact': SCORE,
    'created': STRING, 'affected_dependencies': STRINGS,
    'next_action': STRING, 'revisit_when': STRING, 'evidence': dict(STRINGS, minItems=1),
    'artifacts': ARTIFACTS, 'repair_task': {'type': ['string', 'null']},
    'eligible': BOOL,
})
ISSUES = obj({'version': VERSION, 'issues': array(ISSUE)})
OUTCOME = obj({
    'id': STRING, 'task_id': STRING, 'category': STRING, 'completed': STRING,
    'success': BOOL, 'first_pass_success': BOOL, 'regression': BOOL, 'independent': BOOL,
    'model': STRING, 'reasoning_effort': STRING,
    'artifacts': ARTIFACTS, 'evidence': dict(STRINGS, minItems=1),
    'rework_minutes': NATURAL, 'elapsed_minutes': NATURAL,
    'tokens': {'type': ['integer', 'null'], 'minimum': 0},
})
OUTCOMES = obj({'version': VERSION, 'outcomes': array(OUTCOME)})
SELECTION = obj({'task_id': STRING, 'deliverable': STRING})
RESULT = obj({
    'task_id': STRING,
    'outcome': enum(['accepted', 'provisional', 'preserved', 'unfinished', 'interrupted', 'blocked']),
    'summary': STRING, 'next_action': STRING, 'evidence': STRINGS,
    'commit': {'type': ['string', 'null']},
})
RUN = obj({'version': VERSION, 'run_id': STRING, 'objective': STRING,
           'selected': array(SELECTION, 1), 'results': array(RESULT),
           'delivery': STRING})


def unique(rows, field='id'):
    values = [row[field] for row in rows]
    if len(values) != len(set(values)):
        raise ValueError(f'Duplicate {field}')


def validate_config(config):
    validate(config, CONFIG, 'autonomy policy')
    if config['backlog']['soft_limit'] > config['backlog']['hard_limit']:
        raise ValueError('soft_limit must not exceed hard_limit')
    if config['calibration']['minimum_samples'] > config['calibration']['window']:
        raise ValueError('minimum_samples must not exceed window')
    return config


def load_config(project=None, path=None):
    candidate = Path(path) if path else (Path(project) / '.gameflow/tools/autonomy.json' if project else DEFAULT)
    if not path and not candidate.exists() and not candidate.is_symlink():
        config = read(DEFAULT)
        config['enabled'] = False  # An older project never opts in by upgrading.
        return validate_config(config)
    return validate_config(read(candidate))


def validate_issues(value, as_of=None):
    validate(value, ISSUES, 'issues')
    unique(value['issues'])
    for row in value['issues']:
        created = date.fromisoformat(row['created'])
        if as_of and created > as_of:
            raise ValueError(f'{row["id"]}: creation date is in the future')
        if row['eligible'] and not row['repair_task']:
            raise ValueError(f'{row["id"]}: eligible repair requires a task contract')
    return value


def triage(config, assessment):
    validate_config(config)
    validate(assessment, ASSESSMENT, 'assessment')
    unique(assessment['criteria'])
    revision = digest(assessment['artifacts'])
    criteria = assessment['criteria']
    # Untiered legacy criteria remain required final criteria, never become polish.
    def passed(c):
        return c['result'] == 'pass' and c['independent'] and c['revision'] == revision
    required = [c for c in criteria if c.get('required', True)]
    if not required:
        raise ValueError('At least one required criterion is necessary')
    core = [c for c in criteria if c.get('tier') == 'core']
    integration = [c for c in criteria if c.get('tier') == 'integration']
    unresolved = [c['id'] for c in criteria if not passed(c)]
    accepted = all(passed(c) for c in required)
    if unresolved and not assessment['issue_ids']:
        raise ValueError('Unresolved criteria require actionable issue IDs')
    usable = bool(core) and all(passed(c) for c in core)
    isolated = assessment['isolated'] and assessment['recoverable']
    provisional = (config['enabled'] and config['allow_provisional_integration']
                   and usable and bool(integration) and all(passed(c) for c in integration)
                   and isolated and assessment['propagation_risk'] == 0)
    hypothesis = assessment['new_hypothesis']
    can_repair = (assessment['repair_authorized'] and assessment['repair_allowance_remaining']
                  and bool(hypothesis and hypothesis.strip()) and bool(assessment['hypothesis_evidence']))
    urgent = (not usable or not isolated
              or assessment['propagation_risk'] >= config['repair_risk_threshold']
              or assessment['deferral_cost'] >= config['repair_deferral_cost_threshold'])
    if not config['enabled']:
        action, reason = 'legacy-policy', 'Optional autonomy policy is disabled; use existing task and repair rules.'
    elif accepted:
        action, reason = 'ready-for-acceptance', 'Every required criterion has independent evidence for this revision.'
    elif can_repair and urgent:
        action, reason = 'repair-now', 'A specific new hypothesis can address a usability, propagation, or deferral risk.'
    elif usable and isolated and not urgent:
        action, reason = 'preserve-and-schedule', 'Core use is verified and the remaining work can be isolated and recovered.'
    else:
        action, reason = 'investigate-or-escalate', 'Reduce the missing evidence or obtain the specific prerequisite before repair or reuse.'
    return {'action': action, 'reason': reason, 'task_id': assessment['task_id'],
            'revision': revision, 'eligible_for_acceptance': accepted,
            'provisional_integration_eligible': bool(provisional and not accepted),
            'dependency_satisfied': False, 'unresolved_criteria': unresolved,
            'issue_ids': assessment['issue_ids'],
            'affected_dependencies': assessment['affected_dependencies'],
            'repair_routing': 'Use model-routing repair_profile; default remains Astra.',
            'preservation': 'A labeled partial commit may preserve work; it does not accept it.'}


def schedule(config, issues, as_of, capacity):
    validate_config(config)
    validate_issues(issues, as_of)
    if type(capacity) is not int or capacity < 0:
        raise ValueError('capacity must be a nonnegative integer')
    backlog = config['backlog']
    rows = []
    for issue in issues['issues']:
        if issue['status'] == 'resolved':
            continue
        age = (as_of - date.fromisoformat(issue['created'])).days
        score = issue['impact'] * 10 + len(issue['affected_dependencies']) * 5 + age // backlog['age_days_per_point']
        rows.append(dict(issue, age_days=age, priority_score=score))
    rows.sort(key=lambda r: (-r['priority_score'], r['created'], r['id']))
    count = len(rows)
    reserve = min(capacity, math.ceil(capacity * backlog['repair_fraction'])) if count else 0
    features = min(backlog['max_new_features'], max(0, capacity - reserve))
    if count >= backlog['hard_limit']:
        reserve, features = capacity, 0
    elif count >= backlog['soft_limit']:
        features = min(features, 1)
        reserve = capacity - features
    eligible = [row for row in rows if row['eligible']]
    # Several issues may share one repair task; reserve a task only once.
    repair_tasks = list(dict.fromkeys(row['repair_task'] for row in eligible))[:reserve]
    return {'enabled': config['enabled'], 'as_of': as_of.isoformat(), 'open_issues': count,
            'reserved_repair_slots': reserve if config['enabled'] else 0,
            'new_feature_limit': features if config['enabled'] else None,
            'repair_tasks': repair_tasks if config['enabled'] else [], 'issues': rows,
            'note': 'Reserved repair capacity is not silently lent to features. Check graph readiness, authority, and resources before dispatch; issue deferral never reactivates deferred tasks.'}


def calibrate(config, outcomes, category):
    validate_config(config)
    validate(outcomes, OUTCOMES, 'outcomes')
    unique(outcomes['outcomes'])
    # One current independent outcome per task/category prevents inflated sample counts.
    seen = set()
    for row in outcomes['outcomes']:
        date.fromisoformat(row['completed'])
        if row['first_pass_success'] and not row['success']:
            raise ValueError('first_pass_success requires success')
        key = (row['task_id'], row['category'])
        if key in seen:
            raise ValueError('Keep one current outcome per task/category; archive prior attempts separately')
        seen.add(key)
    policy = config['calibration']
    rows = sorted([r for r in outcomes['outcomes'] if r['category'] == category and r['independent']],
                  key=lambda r: (r['completed'], r['id']), reverse=True)[:policy['window']]
    successes = sum(r['success'] and r['first_pass_success'] for r in rows)
    regressions = sum(r['regression'] for r in rows)
    rate = successes / len(rows) if rows else 0
    qualified = (len(rows) >= policy['minimum_samples'] and rate >= policy['minimum_success_rate']
                 and regressions <= policy['maximum_regressions'])
    return {'category': category, 'samples': len(rows), 'first_pass_success_rate': rate,
            'accepted_outcomes': sum(r['success'] for r in rows),
            'regressions': regressions, 'outcome_ids': [r['id'] for r in rows],
            'autonomy': 'bounded-reversible' if config['enabled'] and qualified else 'assisted',
            'rework_minutes': sum(r['rework_minutes'] for r in rows),
            'elapsed_minutes': sum(r['elapsed_minutes'] for r in rows),
            'tokens': sum(r['tokens'] for r in rows if r['tokens'] is not None),
            'token_samples': sum(r['tokens'] is not None for r in rows),
            'permissions_changed': False,
            'models_observed': sorted(set(r['model'] + '/' + r['reasoning_effort'] for r in rows)),
            'note': 'Category-local evidence is not model-selection evidence and grants no new permissions; retain independent verification, production restrictions, paid limits and repair routing.'}


def report(run, phase):
    validate(run, RUN, 'run')
    unique(run['selected'], 'task_id')
    unique(run['results'], 'task_id')
    selected = {row['task_id']: row for row in run['selected']}
    if any(row['task_id'] not in selected for row in run['results']):
        raise ValueError('Every result must remain in the selected-task register')
    results = {row['task_id']: row for row in run['results']}
    lines = [f'{"Starting" if phase == "opening" else "Ending"} run {run["run_id"]}: {run["objective"]}', '']
    for tid, row in selected.items():
        label = f'{row["deliverable"]} ({tid})'
        if phase == 'opening':
            lines.append(f'- {label}')
        elif tid not in results:
            lines.append(f'- {label}: unfinished — no outcome recorded. Next: reconcile its checkpoint.')
        else:
            result = results[tid]
            if result['outcome'] == 'accepted' and not result['evidence']:
                raise ValueError(f'{tid}: accepted report needs evidence')
            commit = f' Commit: {result["commit"]}.' if result['commit'] else ' Commit: pending or no changes.'
            lines.append(f'- {label}: {result["outcome"]} — {result["summary"]}.{commit} Next: {result["next_action"]}')
    if phase == 'closing':
        lines.extend(['', f'Delivery: {run["delivery"]}'])
    return '\n'.join(lines) + '\n'


def event(command, config, inputs, result, run_id=None):
    decision = dict(result)
    if command == 'schedule':
        decision['issues'] = [{key: row[key] for key in ('id', 'priority_score', 'age_days', 'eligible', 'repair_task')}
                              for row in result['issues']]
    rows = inputs.get('issues', inputs.get('outcomes', [inputs]))
    # Store only identities and evidence relevant to this decision, not old prose.
    selected = set(result.get('outcome_ids', [])) if command == 'calibrate' else None
    references = [{'id': row.get('id', row.get('task_id')), 'artifacts': row['artifacts'],
                   'evidence': row['evidence']} for row in rows
                  if (selected is None or row.get('id') in selected)
                  and row.get('status') != 'resolved']
    value = {'version': 1, 'kind': command, 'policy_sha256': digest(config),
             'input_sha256': digest(inputs), 'decision': decision, 'references': references,
             'run_id': run_id}
    # Stable identities make repeated record operations idempotent. Inputs stay in
    # referenced task evidence; the compact event does not copy full history.
    value['event_id'] = digest(value)
    return value


def record_event(project, value):
    root = Path(project).resolve()
    directory = root / '.gameflow/events'
    if not (root / '.gameflow/tasks/index.json').is_file():
        raise ValueError('Audit recording requires an initialized project')
    if not directory.resolve().is_relative_to(root):
        raise ValueError('Audit directory escapes project')
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (value['event_id'] + '.json')
    if target.is_symlink():
        raise ValueError('Refusing symlink audit record')
    if target.exists():
        existing = read(target)
        existing.pop('recorded_at', None)
        if existing != value:
            raise ValueError('Existing audit event differs; preserve it and investigate')
    else:
        stored = dict(value, recorded_at=datetime.now(timezone.utc).isoformat())
        content = json.dumps(stored, sort_keys=True, indent=2, allow_nan=False) + '\n'
        with target.open('x', encoding='utf-8') as handle:
            handle.write(content)
    return str(target.relative_to(root))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('defaults')
    for name in ('validate', 'triage', 'schedule', 'calibrate', 'report'):
        command = sub.add_parser(name)
        command.add_argument('--project', type=Path)
        command.add_argument('--config', type=Path)
        if name in ('triage', 'schedule', 'calibrate'):
            command.add_argument('--input', type=Path, required=True)
            command.add_argument('--record', action='store_true', help='Explicitly save one idempotent audit event')
            command.add_argument('--run-id', help='Associate the decision with its selected-task run')
        if name == 'schedule':
            command.add_argument('--as-of', type=date.fromisoformat, required=True)
            command.add_argument('--capacity', type=int, required=True)
        if name == 'calibrate':
            command.add_argument('--category', required=True)
        if name == 'report':
            command.add_argument('--run', type=Path, required=True)
            command.add_argument('--phase', choices=['opening', 'closing'], required=True)
    args = parser.parse_args(argv)
    try:
        config = load_config(getattr(args, 'project', None), getattr(args, 'config', None))
        if args.command == 'defaults':
            result = config
        elif args.command == 'validate':
            result = {'valid': True, 'enabled': config['enabled'], 'policy_sha256': digest(config)}
        elif args.command == 'report':
            print(report(read(args.run), args.phase), end='')
            return 0
        else:
            inputs = read(args.input)
            if args.command == 'triage':
                decision = triage(config, inputs)
            elif args.command == 'schedule':
                decision = schedule(config, inputs, args.as_of, args.capacity)
            else:
                decision = calibrate(config, inputs, args.category)
            result = event(args.command, config, inputs, decision, args.run_id)
            if args.record:
                if args.project is None:
                    raise ValueError('--record requires --project')
                result['record_path'] = record_event(args.project, result)
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
        return 0
    except (ValueError, TypeError, KeyError, OSError, UnicodeError) as exc:
        print(f'Autonomy error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
