#!/usr/bin/env python3
"""Optional epic/milestone layer; compatible with GameFlow's flat task graph.
Migration defaults to preview. Definitions never duplicate canonical task records.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import os
import re
import tempfile


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate(index, planning, root):
    from validate_gameflow import validate_task_graph
    errors = []
    validate_task_graph(index, root/'.gameflow', errors, check_planning=False)
    if errors: raise ValueError('; '.join(errors))
    tasks = index['tasks']
    def unique(rows, label):
        ids = [r['id'] for r in rows]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate '+label+' ID')
        return {r['id']: r for r in rows}
    if planning.get('schema_version', 1) != 1:
        raise ValueError('Unsupported planning schema version')
    for key, prefix in (('milestones', 'MILESTONE'), ('epics', 'EPIC')):
        if not isinstance(planning.get(key), list):
            raise ValueError(key + ' must be an array')
        for row in planning[key]:
            if not isinstance(row, dict) or not re.fullmatch(prefix + r'-[0-9]{4,}', str(row.get('id', ''))):
                raise ValueError('Invalid ' + prefix + ' ID')
            required = ('title', 'status', 'acceptance') + (('outcome', 'boundaries', 'milestone') if key == 'epics' else ())
            if any(not isinstance(row.get(k), str) or not row[k].strip() for k in required):
                raise ValueError('Missing/invalid fields: ' + row['id'])
            if row['status'] not in ('planned', 'active', 'accepted', 'deferred'):
                raise ValueError('Invalid planning status: ' + row['id'])
            if key == 'milestones' and (not isinstance(row.get('depends_on', []), list) or
                any(not isinstance(d, str) for d in row.get('depends_on', []))):
                raise ValueError('Invalid milestone dependencies: ' + row['id'])
    ts = unique(tasks, 'task')
    es = unique(planning['epics'], 'epic')
    ms = unique(planning['milestones'], 'milestone')
    for e in es.values():
        if e['milestone'] not in ms:
            raise ValueError('Unknown milestone: '+e['id'])
    for t in tasks:
        if t.get('kind','delivery') not in ('delivery','experiment'):
            raise ValueError('Invalid task kind: '+t['id'])
        if t.get('kind')=='experiment' and t.get('experiment_outcome') not in ('pending','adopted','rejected','superseded','inconclusive'):
            raise ValueError('Missing/invalid experiment outcome: '+t['id'])
        if t.get('epic') is not None and t['epic'] not in es:
            raise ValueError('Unknown epic: '+t['id'])
        contract = (root/'.gameflow'/t['contract']).resolve()
        if not contract.is_relative_to((root/'.gameflow').resolve()) or not contract.is_file():
            raise ValueError('Invalid task contract: '+t['id'])
        if t.get('parent') and t['parent'] not in ts:
            raise ValueError('Unknown parent: '+t['id'])
        for dep in t['depends_on']:
            if dep not in ts or ts[dep]['status'] == 'deferred':
                raise ValueError('Unknown or deferred prerequisite: '+t['id']+' -> '+dep)
        if t.get('disposition') == 'superseded' and t['status'] != 'deferred':
            raise ValueError('Superseded task must be deferred: '+t['id'])
    def acyclic(rows, field):
        remaining = {i: set(r.get(field, [])) for i, r in rows.items()}
        followers = {i: [] for i in rows}
        for i, deps in remaining.items():
            for dep in deps:
                if dep not in rows:
                    raise ValueError('Unknown dependency: '+dep)
                followers[dep].append(i)
        ready = [i for i, deps in remaining.items() if not deps]
        visited = 0
        while ready:
            current = ready.pop(); visited += 1
            for follower in followers[current]:
                remaining[follower].discard(current)
                if not remaining[follower]: ready.append(follower)
        if visited != len(rows): raise ValueError('Dependency cycle')
    acyclic(ts, 'depends_on'); acyclic(ms, 'depends_on')


def migrated(index, plan):
    result = deepcopy(index)
    if plan['id'] in result.get('planning_migrations', []):
        return result
    expected = set(plan['assignments'])
    if expected != {t['id'] for t in result['tasks']}:
        raise ValueError('Task IDs changed since plan; reconcile assignments before migrating')
    # Planning adoption cannot accept work, clear live ownership, or retire assets.
    # Those are explicit production decisions outside this metadata migration.
    if plan.get('retired'):
        raise ValueError('Planning migration cannot retire dependencies')
    for tid, patch in plan.get('patches', {}).items():
        if tid not in expected or set(patch) - {'kind', 'experiment_outcome'}:
            raise ValueError('Only kind/experiment_outcome patches are allowed')
    for t in result['tasks']:
        t['epic'] = plan['assignments'][t['id']]
        t.update(deepcopy(plan.get('patches', {}).get(t['id'], {})))
    result.setdefault('planning_migrations', []).append(plan['id'])
    return result


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                     prefix='.'+path.name+'.', delete=False) as handle:
        tmp = Path(handle.name)
        try:
            handle.write(data)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def check_destinations(root, planning, migration_id=None):
    flow = root/'.gameflow'
    paths = [flow/'tasks/index.json', flow/'planning.json', flow/'ROADMAP.md']
    paths += [flow/'epics'/e['id']/'EPIC.md' for e in planning['epics']]
    if migration_id: paths.append(flow/'migrations'/migration_id)
    for path in paths:
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Output escapes project: '+str(path))
        for part in (path, *path.parents):
            if part == root: break
            if part.is_symlink(): raise ValueError('Refusing symlink output: '+str(part))


def render(root, index, planning):
    check_destinations(root, planning)
    flow = root/'.gameflow'
    tasks = index['tasks']
    overview = ['# Project roadmap', '', 'Generated from planning.json and tasks/index.json. Run `python3 <plugin>/scripts/planning.py render --project .` after task changes.', '']
    for m in planning['milestones']:
        overview += [f"## {m['id']} — {m['title']}", '', f"State: **{m['status']}**. {m['acceptance']}", '']
        epics = [e for e in planning['epics'] if e['milestone'] == m['id']]
        for e in epics:
            rows = [t for t in tasks if t.get('epic') == e['id']]
            active = [t for t in rows if t.get('disposition') not in ('superseded','retired_asset')]
            counts = dict(Counter(t['status'] for t in active))
            overview += [f"- [{e['id']} — {e['title']}](epics/{e['id']}/EPIC.md): {e['status']}; {counts}"]
            body = [f"# {e['id']} — {e['title']}", '', f"Milestone: {m['id']}. State: **{e['status']}**.", '', '## Outcome', '', e['outcome'], '', '## Acceptance', '', e['acceptance'], '', '## Boundaries', '', e['boundaries'], '', '## Tasks', '', '| Task | State | Disposition | Experiment outcome |', '|---|---|---|---|']
            for t in rows:
                body += [f"| [{t['id']} — {t['title']}](../../{t['contract']}) | {t['status']} | {t.get('disposition','active')} | {t.get('experiment_outcome','—')} |"]
            atomic(flow/'epics'/e['id']/'EPIC.md', '\n'.join(body)+'\n')
        overview += ['']
    unassigned = [t for t in tasks if t.get('epic') is None]
    if unassigned:
        overview += ['## Unassigned tasks', ''] + [f"- [{t['id']} — {t['title']}]({t['contract']}): {t['status']}" for t in unassigned]
    atomic(flow/'ROADMAP.md', '\n'.join(overview).rstrip()+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['migrate','validate','render','summary','assign'])
    parser.add_argument('--project', type=Path, default=Path('.'))
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--task')
    parser.add_argument('--epic')
    parser.add_argument('--kind', choices=['delivery','experiment'], default='delivery')
    args=parser.parse_args();root=args.project.resolve();flow=root/'.gameflow'
    index=read(flow/'tasks/index.json')
    if args.command=='assign':
        if not args.task or not args.epic:parser.error('--task and --epic required')
        planning=read(flow/'planning.json')
        selected=next((t for t in index['tasks'] if t['id']==args.task),None)
        if selected is None:raise ValueError('Unknown task')
        selected.update(epic=args.epic,kind=args.kind)
        if args.kind=='experiment':selected.setdefault('experiment_outcome','pending')
        else:selected.pop('experiment_outcome',None)
        validate(index,planning,root)
        check_destinations(root, planning)
        atomic(flow/'tasks/index.json',json.dumps(index,indent=2)+'\n')
        render(root,index,planning)
        return
    if args.command=='migrate':
        if not args.plan:
            parser.error('--plan required')
        plan=read(args.plan)
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', str(plan.get('id', ''))):
            raise ValueError('Invalid migration ID')
        if plan['id'] in index.get('planning_migrations', []):
            print('Already applied; no changes');return
        candidate=migrated(index,plan)
        validate(candidate,plan['planning'],root)
        if candidate==index:
            print('Already applied; no changes');return
        print(json.dumps({'migration':plan['id'],'tasks':len(candidate['tasks']), 'patched':len(plan.get('patches', {})), 'apply':args.apply},indent=2))
        if not args.apply:return
        check_destinations(root, plan['planning'], plan['id'])
        backup=flow/'migrations'/plan['id']
        if backup.exists():
            raise ValueError('Backup already exists; inspect incomplete migration before retry')
        # Save all previously existing metadata before replacing generated views.
        backup.mkdir(parents=True)
        for old_path in [flow/'planning.json', flow/'ROADMAP.md', *sorted((flow/'epics').glob('*/EPIC.md'))]:
            if old_path.is_file():
                target = backup/'before'/old_path.relative_to(flow)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(old_path.read_bytes())
        original=(flow/'tasks/index.json').read_bytes()
        (backup/'tasks-index.before.json').write_bytes(original)
        (backup/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
        (backup/'manifest.json').write_text(json.dumps({'timestamp':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(original).hexdigest()},indent=2)+'\n')
        # Index is the final commit marker. Interrupted earlier writes can be recovered from backup.
        atomic(flow/'planning.json',json.dumps(plan['planning'],indent=2)+'\n')
        render(root,candidate,plan['planning'])
        atomic(flow/'tasks/index.json',json.dumps(candidate,indent=2)+'\n')
    else:
        planning=read(flow/'planning.json');validate(index,planning,root)
        if args.command=='render':render(root,index,planning)
        elif args.command=='summary':
            for e in planning['epics']:
                rows=[t for t in index['tasks'] if t.get('epic')==e['id'] and t.get('disposition') not in ('superseded','retired_asset')]
                print(e['id'],e['title'],e['status'],dict(Counter(t['status'] for t in rows)))
        else:print('Planning graph valid')

if __name__=='__main__':main()
