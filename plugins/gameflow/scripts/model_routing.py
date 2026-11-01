#!/usr/bin/env python3
"""Explain project-local subagent routing. Read-only; never dispatches agents."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from meshy_config import ConfigError, load_json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'templates/gameflow/tools/model-routing.json'
DIMENSIONS = ('size', 'complexity', 'coupling', 'ambiguity', 'novelty',
              'visual', 'temporal', 'consequence')
ROLES = ['implementation', 'verification', 'recovery', 'planning']
EFFORTS = ['none', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra']
STRING = {'type': 'string', 'minLength': 1, 'pattern': r'\S'}
STRINGS = {'type': 'array', 'items': STRING, 'uniqueItems': True}
SCORE = {'type': 'integer', 'minimum': 0, 'maximum': 3}


def obj(properties, required=None):
    return {'type': 'object', 'properties': properties, 'additionalProperties': False,
            'required': list(properties) if required is None else required}


def enum(values):
    return {'enum': values}


def array(items, minimum=0):
    return {'type': 'array', 'items': items, 'minItems': minimum}


SCORES = obj({name: SCORE for name in DIMENSIONS})
LIMITS = obj({name: SCORE for name in DIMENSIONS}, [])
MATCH = obj({
    'roles': array(enum(ROLES), 1),
    'operations_any': dict(STRINGS, minItems=1),
    'operations_only': dict(STRINGS, minItems=1),
    'components_any': dict(STRINGS, minItems=1),
    'tools_any': dict(STRINGS, minItems=1),
    'tags_all': dict(STRINGS, minItems=1),
    'confidence': array(enum(['low', 'medium', 'high']), 1),
    'dimensions_min': LIMITS, 'dimensions_max': LIMITS,
}, [])
CANDIDATE = obj({'model': STRING, 'reasoning_effort': enum(EFFORTS)})
CONFIG = obj({
    'version': {'const': 1, 'type': 'integer'},
    'description': STRING,
    'profiles': {'type': 'object', 'minProperties': 1, 'additionalProperties': obj({
        'description': STRING, 'candidates': array(CANDIDATE, 1)})},
    'default_profile': STRING,
    'repair_profile': STRING,
    'rules': array(obj({'id': STRING, 'description': STRING, 'priority': {'type': 'integer'},
                        'match': MATCH, 'profile': STRING})),
})
ASSESSMENT = obj({
    'version': {'const': 1, 'type': 'integer'}, 'task_id': STRING,
    'role': enum(ROLES), 'operations': dict(STRINGS, minItems=1),
    'components': STRINGS, 'tools': STRINGS, 'tags': STRINGS,
    'dimensions': SCORES, 'confidence': enum(['low', 'medium', 'high']),
    'failed_acceptance': {'type': 'boolean'}, 'repair_of': STRINGS,
    'evidence': obj({name: STRING for name in [
        'scope', 'failure_history', 'confidence', *DIMENSIONS]}),
})
RUNTIME = obj({
    'model_selection': {'type': 'boolean'},
    'models': {'type': 'object', 'additionalProperties': array(enum(EFFORTS), 1)},
})


def validate(value, schema, label):
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise ConfigError('Install scripts/requirements.txt to validate model routing') from exc
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda e: str(e.path))
    if errors:
        error = errors[0]
        path = '.'.join(str(part) for part in error.absolute_path)
        raise ConfigError(f'{label}{"." + path if path else ""}: {error.message}')
    return value


def read(path):
    return load_json(Path(path).read_text(encoding='utf-8'))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def validate_config(config):
    validate(config, CONFIG, 'config')
    profiles = config['profiles']
    for name in profiles:
        if not name.strip():
            raise ConfigError('Profile names must be nonempty')
    for name in [config['default_profile'], config['repair_profile'],
                 *(rule['profile'] for rule in config['rules'])]:
        if name not in profiles:
            raise ConfigError(f'Unknown profile: {name}')
    ids = [rule['id'] for rule in config['rules']]
    if len(ids) != len(set(ids)):
        raise ConfigError('Duplicate rule ID')
    for rule in config['rules']:
        match = rule['match']
        for name, minimum in match.get('dimensions_min', {}).items():
            if minimum > match.get('dimensions_max', {}).get(name, 3):
                raise ConfigError(f'{rule["id"]}: contradictory bounds for {name}')
    for name, profile in profiles.items():
        candidates = [(c['model'], c['reasoning_effort']) for c in profile['candidates']]
        if len(candidates) != len(set(candidates)):
            raise ConfigError(f'{name}: duplicate candidate')
    return config


def load_config(project=None, config_path=None):
    path = Path(config_path) if config_path is not None else (
        Path(project) / '.gameflow/tools/model-routing.json' if project is not None else DEFAULT)
    # Only absence uses defaults. An unreadable/malformed/dangling configuration fails closed.
    if config_path is None and not path.exists() and not path.is_symlink():
        path = DEFAULT
    return validate_config(read(path)), str(path)


def match_rule(match, assessment):
    reasons = []
    for selector, field in [('roles', 'role'), ('confidence', 'confidence')]:
        if selector in match and assessment[field] not in match[selector]:
            reasons.append(f'{field}={assessment[field]} is not in {match[selector]}')
    for selector, field in [('operations_any', 'operations'), ('components_any', 'components'),
                            ('tools_any', 'tools')]:
        if selector in match and not set(match[selector]) & set(assessment[field]):
            reasons.append(f'{field} has no overlap with {match[selector]}')
    if not set(match.get('tags_all', [])) <= set(assessment['tags']):
        reasons.append('required tags are missing')
    if 'operations_only' in match and not set(assessment['operations']) <= set(match['operations_only']):
        reasons.append('phase includes operations outside operations_only')
    for name, minimum in match.get('dimensions_min', {}).items():
        if assessment['dimensions'][name] < minimum:
            reasons.append(f'{name}<{minimum}')
    for name, maximum in match.get('dimensions_max', {}).items():
        if assessment['dimensions'][name] > maximum:
            reasons.append(f'{name}>{maximum}')
    return reasons


def project_repair_signals(project, assessment):
    """Read structured counts; prose failure evidence remains the coordinator's responsibility."""
    if project is None:
        return []
    from validate_gameflow import validate_task_graph
    flow = Path(project) / '.gameflow'
    index = read(flow / 'tasks/index.json')
    errors = []
    validate_task_graph(index, flow, errors)
    if errors:
        raise ConfigError('Cannot reconcile repair history: ' + '; '.join(errors))
    tasks = {task['id']: task for task in index['tasks']}
    signals = []
    for task_id in [assessment['task_id'], *assessment['repair_of']]:
        if task_id not in tasks:
            raise ConfigError(f'Unknown task in assessment: {task_id}')
        task = tasks[task_id]
        counts = (task.get('checkpoint') or {}).get('repair_counts', {})
        if task['status'] != 'done' and any(value > 0 for value in counts.values()):
            signals.append(f'{task_id}: persisted repair counts {counts}')
    return signals


def resolve(config, assessment, runtime, project=None):
    validate_config(config)
    validate(assessment, ASSESSMENT, 'assessment')
    validate(runtime, RUNTIME, 'runtime')
    signals = project_repair_signals(project, assessment)
    if assessment['failed_acceptance']:
        signals.append('assessment: failed acceptance remains unresolved')
    if assessment['repair_of']:
        signals.append('assessment: remediation of ' + ', '.join(assessment['repair_of']))
    repair = bool(signals) and assessment['role'] != 'verification'
    trace = []
    for rule in config['rules']:
        reasons = match_rule(rule['match'], assessment)
        trace.append({'id': rule['id'], 'priority': rule['priority'], 'profile': rule['profile'],
                      'description': rule['description'], 'matched': not reasons,
                      'mismatches': reasons})
    result = {'version': 1, 'task_id': assessment['task_id'], 'role': assessment['role'],
              'config_sha256': digest(config), 'assessment_sha256': digest(assessment),
              'runtime_sha256': digest(runtime), 'repair_escalated': repair,
              'repair_signals': signals, 'rules': trace, 'dispatch_performed': False}
    matched = [rule for rule in trace if rule['matched']]
    if repair:
        profile = config['repair_profile']
        selected = ['repair_profile']
    elif matched:
        priority = max(rule['priority'] for rule in matched)
        winners = [rule for rule in matched if rule['priority'] == priority]
        selected = [rule['id'] for rule in winners]
        profiles = {rule['profile'] for rule in winners}
        if len(profiles) != 1:
            return dict(result, status='blocked', reason='Conflicting highest-priority rules',
                        selected_rules=selected)
        profile = profiles.pop()
    else:
        profile = config['default_profile']
        selected = ['default_profile']
    result.update(profile=profile, selected_rules=selected,
                  profile_description=config['profiles'][profile]['description'])
    if not runtime['model_selection']:
        return dict(result, status='blocked', reason='Runtime cannot select a subagent model')
    skipped = []
    for candidate in config['profiles'][profile]['candidates']:
        model, effort = candidate['model'], candidate['reasoning_effort']
        if model not in runtime['models']:
            skipped.append(dict(candidate, reason='Model unavailable or restricted'))
        elif effort not in runtime['models'][model]:
            skipped.append(dict(candidate, reason='Reasoning effort unavailable'))
        else:
            return dict(result, status='selected', model=model, reasoning_effort=effort,
                        fallback_used=bool(skipped), skipped_candidates=skipped)
    return dict(result, status='blocked', reason='No configured candidate is available',
                skipped_candidates=skipped)


def evaluate(config, cases):
    expected_schema = obj({'status': enum(['selected', 'blocked']), 'profile': STRING,
                           'model': STRING, 'reasoning_effort': enum(EFFORTS)}, ['status'])
    validate(cases, array(obj({'id': STRING, 'assessment': ASSESSMENT, 'runtime': RUNTIME,
                               'expected': expected_schema}), 1), 'cases')
    ids = [case['id'] for case in cases]
    if len(ids) != len(set(ids)):
        raise ConfigError('Duplicate case ID')
    outputs = []
    for case in cases:
        result = resolve(config, case['assessment'], case['runtime'])
        differences = {key: {'expected': value, 'actual': result.get(key)}
                       for key, value in case['expected'].items() if result.get(key) != value}
        outputs.append({'id': case['id'], 'passed': not differences,
                        'differences': differences, 'decision': result})
    return {'passed': all(case['passed'] for case in outputs), 'cases': outputs,
            'note': 'Offline routing replay only; not evidence of model task success.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('defaults', help='Print the complete editable default policy')
    for name in ('validate', 'resolve', 'evaluate'):
        command = commands.add_parser(name)
        command.add_argument('--config', type=Path, help='Candidate policy; overrides project policy for this read-only run')
        command.add_argument('--project', type=Path)
        if name == 'resolve':
            command.add_argument('--assessment', type=Path, required=True)
            command.add_argument('--runtime', type=Path, required=True)
        if name == 'evaluate':
            command.add_argument('--cases', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        config, source = load_config(getattr(args, 'project', None), getattr(args, 'config', None))
        code = 0
        if args.command == 'defaults':
            result = config
        elif args.command == 'validate':
            result = {'valid': True, 'config_source': source, 'config_sha256': digest(config)}
        elif args.command == 'resolve':
            result = resolve(config, read(args.assessment), read(args.runtime), args.project)
            result['config_source'] = source
            code = 0 if result['status'] == 'selected' else 3
        else:
            result = evaluate(config, read(args.cases))
            result['config_source'] = source
            code = 0 if result['passed'] else 1
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return code
    except (ConfigError, OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(f'Model routing error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
