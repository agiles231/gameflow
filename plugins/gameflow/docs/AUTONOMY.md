# Evidence-based autonomy

GameFlow 0.10.0 adds optional decision support through `scripts/autonomy.py`.
It runs when invoked; there is no daemon, automatic dispatch, permission grant,
acceptance writer, or background retry loop. Decisions depend on supplied evidence;
the coordinator and independent verifier still inspect the actual artifacts.

## Adoption and compatibility

Existing task graphs, checkpoints, unclassified Markdown acceptance criteria,
model routing, and CLI calls remain supported. The optional
`.gameflow/tools/autonomy.json` enables decision support for newly initialized
projects. An existing project without the file retains disabled legacy behavior,
and reinitialization never adds it. Initialization preserves authored files. To
opt an existing project in, save the printed defaults to that path, review the
thresholds, and validate it. Set `enabled: false` to opt out. This is an additive
feature, not a format migration.
Keep a copy or Git revision before editing project policy; disabling it restores
legacy scheduling and repair rules without deleting issues or evidence.

```sh
python3 scripts/autonomy.py defaults
python3 scripts/autonomy.py validate --project PROJECT
```

An invalid present configuration fails closed. Neither this policy nor category
calibration changes `model-routing.json`: failed-acceptance repair still resolves
its `repair_profile`, which defaults to Astra. Smaller models may collect evidence,
run prescribed independent checks, or write reports under their routed profile;
they do not gain repair authority from a successful check or a confidence score.

## Preservation, integration, and acceptance

Treat these as separate facts:

| Fact | Meaning |
| --- | --- |
| Preservation | A labeled partial commit protects useful work and records its failures and next action. It requires existing commit authority. |
| Provisional integration | An isolated, recoverable candidate passed explicit core and integration checks; it may be exercised within the existing authorized task scope when policy allows. |
| Verified acceptance | Every required criterion and required user judgment passed independently on the exact revision; the coordinator may then accept and reconcile its commit. |

Provisional integration never satisfies a `depends_on` edge, changes a task to
`done`, or permits release. Keep dependent production blocked until the ordinary
acceptance gate passes. It is useful for an isolated candidate, feature switch,
test fixture, or branch within the authorized scope. Default policy disables it;
`allow_provisional_integration: true` additionally requires zero assessed propagation
risk, independent passing core/integration criteria, isolation and recoverability.

Before execution, classify criteria as **core** (principal usable behavior),
**integration** (consumer compatibility and containment), **final** (complete
delivery requirements), or **polish** (remaining finish). Specify `required`
explicitly where useful. Polish is still required unless explicitly scoped out by
the authorized contract. Legacy unclassified criteria remain required final
criteria. Do not relabel a failed requirement as optional, remove it, or weaken
its threshold to qualify for acceptance. Record authorized scope changes and their
consequences before applying them. A failed criterion stays failed after a commit.

## Triage and issue records

```sh
python3 scripts/autonomy.py triage --project PROJECT --input assessment.json
python3 scripts/autonomy.py triage --project PROJECT --input assessment.json --record
```

Assessments contain `version: 1`, `task_id`, `category`, `artifacts` (path to SHA-256
map), `criteria`, `propagation_risk` and `deferral_cost` (0–3), `isolated`,
`recoverable`, `repair_authorized`, `repair_allowance_remaining`, `new_hypothesis`
(text or null), `hypothesis_evidence`, `affected_dependencies`, `issue_ids`, and
`evidence` references. Each criterion contains `id`, `result` (`pass`, `fail`,
`unknown`), `independent`, `revision`, `evidence`, optional `tier`, and optional
`required` (defaults true). Its revision is the SHA-256 of the artifact map's
canonical JSON, using the shared `model_routing.digest` function. Changed or
nonindependent evidence cannot pass a check. Include required user judgments as
pending criteria until the specific approval is recorded.

The deterministic decision is:

- Repair now when usability, propagation, containment, or deferral cost warrants
  it **and** a new evidence-backed hypothesis, authority, and repair allowance exist.
- Preserve and schedule when verified core use remains sound, work is isolated
  and recoverable, and propagation/deferral cost is below configured thresholds.
- Investigate or escalate when evidence, a useful new hypothesis, authority, or
  safe reuse is missing. Name the exact missing prerequisite; evidence gathering
  may proceed within existing authority. Do not repeat an ineffective repair.

The helper reports eligibility only. It cannot establish a real-world observation,
verify user authority, check that a claimed hypothesis is actually new, or perform
acceptance. The coordinator checks these against the contract and recent attempts.
Preservation may still be useful when core behavior fails, but that candidate must
not be reused as usable work. Keep every unresolved criterion linked to an issue.

Optional `.gameflow/issues.json` has `version: 1` and an `issues` array. Each issue
contains `id`, `task_id`, human `title`, `status` (`open`/`resolved`), `impact` (0–3),
ISO `created` date, `affected_dependencies`, `next_action`, `revisit_when`,
`evidence`, `artifacts`, `repair_task` (task ID or null), and `eligible` boolean.
Eligibility means its existing repair contract is ready and authorized; a reason
or date alone cannot reactivate a deferred/interactive task. Record affected
consumers requiring recheck and the exact evidence that will resolve the issue.
Do not set the original task `done` while its required failure remains unresolved.
Issue scheduling is distinct from the graph's protected `deferred` lifecycle state.

## Repair capacity and demonstrated outcomes

```sh
python3 scripts/autonomy.py schedule --project PROJECT --input PROJECT/.gameflow/issues.json --as-of 2026-11-01 --capacity 3
python3 scripts/autonomy.py calibrate --project PROJECT --input outcomes.json --category engine-import
```

Scheduling ranks open issues by `10 × impact + 5 × affected dependency count +
floor(age days / age_days_per_point)`, breaking ties by oldest creation date then
ID. This gives aging issues increasing priority. Reserve the configured repair
fraction before admitting features; at the soft backlog limit admit at most one
new feature, and at the hard limit admit none. Existing selected work keeps its
reservation. Supply available admission capacity after existing reservations and
verifier needs, not the raw runtime worker count. Deduplicate issues sharing a
repair task. If reserved repairs are blocked, investigate their prerequisite;
do not silently refill their capacity with features. Limits do not authorize
additional attempts or override the bounded run deadline.

An outcome input has `version: 1` and `outcomes`: one current observation per
task/category, with `id`, `task_id`, `category`, ISO `completed` date, `success`,
`first_pass_success`, `regression`, `independent`, `model`, `reasoning_effort`,
`artifacts`, `evidence`, `rework_minutes`,
`elapsed_minutes`, and `tokens` (integer or null when unavailable). Archive prior
attempts; do not count retries as new successful tasks. Retain regressions and
failures in the current records. Use stable categories corresponding to actual
work, tools and risk (for example `engine-import` versus `character-animation`);
success in one category says nothing about another. Keep the original model and
effort attribution; a repaired success is not a first-pass success or evidence
that a smaller model can perform the repair.

Calibration uses the latest independent observations in the configured window.
The minimum sample, first-pass success rate and regression thresholds may justify
`bounded-reversible` delegation in that category; otherwise it recommends
`assisted`. This is a transparent local heuristic, not a statistically certified
success probability. No model confidence is an input. Always retain independent
verification, spending/production restrictions, permission gates and repair
routing. Regressions can reduce autonomy. Token/rework/time totals describe the
observations; compare comparable categories and workloads before claiming savings.

## Compact audit and human reports

All decision commands are read-only by default and emit structured events with
stable IDs, optional `--run-id`, policy/input hashes, relevant artifact identities, evidence references
and the decision. `--record --project PROJECT` explicitly saves an immutable event
under `.gameflow/events/` with its first-recorded UTC timestamp; repeating the
same event preserves that timestamp and is idempotent. Only the
coordinator records shared state. Keep transcript/image payloads out of events.
Maintain the current issue/outcome summaries and point to relevant event IDs in
the contract/handoff. Resume from those summaries and selected-task context;
load old events only for a specific inconsistency or causal investigation.

```sh
python3 scripts/autonomy.py report --run run.json --phase opening
python3 scripts/autonomy.py report --run run.json --phase closing
```

The run input contains `version: 1`, `run_id`, `objective`, `selected` (each with
`task_id` and recognizable `deliverable`), `results`, and a human `delivery`
statement. Each result has `task_id`, `outcome` (`accepted`, `provisional`,
`preserved`, `unfinished`, `interrupted`, `blocked`), `summary`, `next_action`,
`evidence`, and `commit` (hash or null). Preserve every selection, append children
as they enter the run, and never remove unfinished selections. Closing reports
include missing results as unfinished rather than silently dropping them. The
formatter trusts supplied observations and does not certify acceptance or pushing.

Open a user-invoked run with its objective and named deliverables, then end with
every selected deliverable's outcome, remaining action and actual Git delivery.
For a run whose next tasks are not yet known, state that uncertainty and extend
the register when selected. Scheduled runs retain these durable reports while
honoring existing quiet/no-contact policies. Reports are also useful with the
optional decision policy disabled.
