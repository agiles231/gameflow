# Milestones, epics, tasks and experiments

`tasks/index.json` remains the sole canonical task graph. Optional `planning.json`
defines milestones and epics; tasks may carry `epic`, `kind`, and
`experiment_outcome`. Existing `parent` means task decomposition, not epic membership.
Contracts stay in `tasks/TASK-NNNN.md`. `ROADMAP.md` and `epics/EPIC-NNNN/EPIC.md`
are generated navigation; edit the definitions/contracts and regenerate them.
Unassigned tasks remain valid and appear in the roadmap. Legacy projects without
planning.json remain valid; an epic assignment requires that file.

Milestones describe integrated deliverables; epics describe substantial outcomes;
tasks describe bounded independently verifiable changes. Milestone/epic statuses
are planned, active, accepted or deferred. Acceptance is explicit: completed child
tasks alone do not establish integrated acceptance. Summaries exclude superseded
and retired_asset dispositions and do not imply effort-weighted completion percentages.

## Usage

Run these from the installed plugin root, with PROJECT pointing to the game:

```sh
python3 scripts/planning.py validate --project PROJECT
python3 scripts/planning.py summary --project PROJECT
python3 scripts/planning.py render --project PROJECT
python3 scripts/new_task.py --project PROJECT --title "Compare distant forest proxies" --epic EPIC-0001 --kind experiment
python3 scripts/planning.py assign --project PROJECT --task TASK-0002 --epic EPIC-0001 --kind delivery
```

Define milestones and epics in planning.json before assigning tasks. IDs use
MILESTONE-NNNN and EPIC-NNNN. Milestones contain title, status, acceptance and
optional depends_on milestone IDs. Epics contain title, status, milestone, outcome,
acceptance and boundaries. The root has schema_version: 1, milestones: [], epics: [].
The native validator, resume view and context helper check planning when present.

Experiments state hypothesis, baseline, bounded variants, resource budget,
measurements and stop condition. Their outcome is pending, adopted, rejected,
superseded or inconclusive, independent of lifecycle status. A verified negative
result can be done. Unfinished obsolete work is deferred with disposition superseded,
not falsely accepted; active tasks cannot depend on deferred work. An adopted
experiment gets a delivery follow-up if production integration remains necessary.

## Explicit migration

`planning.py migrate --project PROJECT --plan PLAN.json` previews without writes.
Add `--apply` only for an explicitly requested upgrade. The plan contains an id,
planning definitions, assignments mapping every existing task ID to an epic ID
(or null), and optional patches mapping task IDs to kind/experiment_outcome only.
For example:

```json
{
  "id": "planning-v1",
  "planning": {
    "schema_version": 1,
    "milestones": [{"id": "MILESTONE-0001", "title": "First slice", "status": "planned", "acceptance": "Playable end to end", "depends_on": []}],
    "epics": [{"id": "EPIC-0001", "title": "Slice definition", "milestone": "MILESTONE-0001", "status": "planned", "outcome": "Bounded slice", "acceptance": "Scope accepted", "boundaries": "Planning only"}]
  },
  "assignments": {"TASK-0001": "EPIC-0001"},
  "patches": {}
}
```

Migration validates the candidate, backs up the original index, plan and previous
planning/views, writes generated files, then replaces the index last as its completion
marker. The original index SHA256 is recorded. Repeated application of the same ID
is a no-op. Changed task sets are rejected. An existing incomplete backup is never
overwritten; inspect it and recover in an isolated checkout before retrying.
Do not edit concurrently. Migration does not accept tasks, clear owners/checkpoints,
retire assets, remove dependencies, change Git tracking, or rewrite history.
