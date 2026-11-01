# Configurable subagent model routing

GameFlow assesses each delegated phase, then deterministically selects a model
using `.gameflow/tools/model-routing.json`. The policy is editable JSON. It
separates **what the work requires**, **which profile handles it**, and **which
models the current runtime actually offers**. The resolver only reads files; it
never dispatches agents, edits project state, or contacts applications/providers.
The coordinator uses its result through the orchestration skill.

## Start and customize

New projects receive the default policy during initialization. Existing projects
without this file use the same bundled defaults and need no migration. To start
customizing an existing project, copy
`templates/gameflow/tools/model-routing.json` into `.gameflow/tools/` only when the
project has no policy. Alternatively, `defaults` prints a complete editable copy:

```sh
python3 scripts/model_routing.py defaults
python3 scripts/model_routing.py validate --project /path/to/project
python3 scripts/model_routing.py validate --config /path/to/candidate.json
```

Commands are relative to the plugin root. Install `scripts/requirements.txt` if
needed. Configuration files are complete policies, not deep-merge patches: every
profile, fallback and rule is visible. An existing file is authoritative, including
an intentionally empty `rules` list. Missing optional configuration uses defaults;
invalid, unreadable or unsupported configuration fails rather than using defaults.

`version: 1` identifies this configuration's format independently of task and
checkpoint versions. `description`, profile descriptions and rule descriptions
explain intent but do not execute as conditions. Unknown fields, duplicate JSON
keys, nonfinite numbers, invalid bounds and missing profile references are errors.

## Policy model and precedence

The top-level fields are `version`, `description`, `profiles`, `default_profile`,
`repair_profile` and `rules`. All are required.

- **Profiles** have a description and an ordered `candidates` list. Each candidate
  specifies exact `model` and `reasoning_effort` strings. The first candidate
  available at that effort wins. This is explicit preference order, not a guessed
  model ranking or a live price optimizer. A candidate can use a different effort
  on the same model, but only when you explicitly list that fallback.
- **Rules** have a unique `id`, description, integer priority, `match` object and
  profile. All conditions inside `match` must hold. Every rule is evaluated;
  highest priority wins. Equal-priority matches selecting the same profile agree;
  matches selecting different profiles block instead of relying on file order.
- **Default profile** handles work that matches no rule.
- **Repair profile** overrides all ordinary rules for unresolved failed acceptance
  or remediation, except during independent verification. Shipped behavior is
  Astra/high with no fallback. It cannot be disabled by a cheap high-priority rule.
  To deliberately change repair behavior, the user must direct an explicit edit
  to `repair_profile` or its profile candidates. Agents must never do this just
  to avoid a blocker. Model changes do not grant extra repair attempts.

The default profiles are `focused` (Luna), `visual` (Terra), `engineering` (Sol),
`engineering-high` (Sol/high), `demanding` (Astra/high), and `repair` (Astra/high).
Cheaper profiles list explicit Sol/Astra fallbacks. There is no implicit fallback
outside a profile. If none of its candidates is available, selection blocks.
Model IDs are configurable rather than hard-coded into the resolver.

The default rules reserve Astra for mesh generation/prompt design, authorized
rigging/animation and demanding reasoning. Low-confidence assessments also use
Astra. Substantial understood reasoning uses Sol/high. Ordinary engineering
outranks bounded visual operations; small explicit objective work can use Luna.
Size alone does not force Astra. These are conservative initial hypotheses,
not measured Unreal, Blender, GIMP or Meshy success rates.

## Describing a phase

An assessment has `version`, `task_id`, `role`, `operations`, `components`, `tools`,
`tags`, `dimensions`, `confidence`, `failed_acceptance`, `repair_of` and `evidence`.
All fields are required in the assessment file; none is added to legacy task
contracts or checkpoint schemas. Roles are `implementation`, `verification`,
`recovery`, or `planning`. A repair retains the implementation/recovery role and
sets failure history; it is not a special role that can accidentally be omitted.

Use exact case-sensitive, preferably lowercase hyphenated labels for operations,
components, tools and tags. Custom labels are supported. Components describe the
subsystems involved, e.g. `vehicle-physics`, `inventory-ui`, `animation-state-machine`.
Tools describe actual applications, e.g. `unreal`, `blender`, `gimp`, `meshy`.
Tags are project-defined facts, not statements such as `use-cheap-model`.

Default operation labels:

| Work | Labels |
| --- | --- |
| Objective mechanical phases | `inventory`, `log-extraction`, `job-polling`, `documentation`, `delivery-check` |
| Visual/application phases | `visual-inspection`, `application-operation`, `image-edit`, `material-hookup` |
| Engineering | `coding`, `scripting`, `integration`, `build`, `test`, `diagnosis`, `architecture` |
| Generation and animation | `mesh-generation`, `mesh-prompt-design`, `rigging`, `animation-production`, `animation-evaluation` |

List every inseparable operation. Polling an existing Meshy job is not generation;
writing a new Meshy prompt is. Running a supplied Blender export is different from
inventing a complex Blender script. Assess verification against the checks it
actually needs: delivery-only acceptance differs from temporal animation review.
Cheap default rules require all operations to belong to their known bounded set;
an unfamiliar operation in a mixed phase cannot slip through a cheap match.

## Anchored assessment rubric

Each dimension is an integer from 0 to 3. Assess the hardest inseparable component,
not the average across files. Size means scope of work, not token count or source
file length. Do not use a weighted sum: a severe risk must not be cancelled by
several easy dimensions. Rules can instead combine thresholds explicitly.

| Dimension | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| `size` | One small action/artifact | Bounded change in one area | Several artifacts or stages | Broad deliverable; consider decomposition |
| `complexity` | Prescribed mechanical steps | Familiar local implementation | Multi-step reasoning with understood methods | Difficult open-ended reasoning/algorithm |
| `coupling` | Isolated | One understood interface | Several interacting components | Tightly coupled cross-system invariants |
| `ambiguity` | Exact outcome and procedure | Minor routine choices | Incomplete approach; outcome clear | Material uncertainty in approach/criteria |
| `novelty` | Previously validated same workflow | Familiar pattern with small variation | New use of known tools | Unproven workflow or unfamiliar technical domain |
| `visual` | No visual judgment | Clear reference, objective comparison | Multiple views or subtle appearance judgment | Complex spatial/anatomical or creative judgment |
| `temporal` | No temporal judgment | Prescribed timing/playback checks | Interacting timing/state transitions | Motion quality, contact, dynamics or complex temporal reasoning |
| `consequence` | Cheap reversible local change | Limited rework | Significant integration/recovery cost | Broad or difficult-to-recover consequences |

Confidence describes confidence in this assessment, not confidence that a chosen
model will succeed: `high` means inputs and criteria inspected; `medium` means
bounded uncertainty remains; `low` means evidence is insufficient. For an unknown
dimension, record the uncertainty, use a conservative score and low confidence.
Choosing Astra does not resolve missing authority or product decisions: those
remain blockers. Evidence must explain scope, failure history, confidence and
each dimension with concrete observations or durable references.

Example assessment (save as `assessment.json`):

```json
{
  "version": 1,
  "task_id": "TASK-0042",
  "role": "implementation",
  "operations": ["coding", "test"],
  "components": ["inventory-ui"],
  "tools": ["unreal"],
  "tags": ["existing-pattern"],
  "dimensions": {
    "size": 1, "complexity": 1, "coupling": 1, "ambiguity": 0,
    "novelty": 1, "visual": 0, "temporal": 0, "consequence": 1
  },
  "confidence": "high",
  "failed_acceptance": false,
  "repair_of": [],
  "evidence": {
    "scope": "Contract: add a sort toggle using the existing inventory widget pattern.",
    "failure_history": "Contract and checkpoint inspected: no failed acceptance or repair attempts.",
    "confidence": "Inputs, widget source and observable acceptance checks inspected.",
    "size": "One widget and its behavioral test.",
    "complexity": "Existing sort comparator can be reused.",
    "coupling": "One existing inventory interface.",
    "ambiguity": "Sort order and toggle behavior specified.",
    "novelty": "Existing toggle pattern applied to sorting.",
    "visual": "Acceptance is behavioral, with no new appearance decisions.",
    "temporal": "No timing or animation changes.",
    "consequence": "Local reversible widget change."
  }
}
```

A fresh failure sets `failed_acceptance: true` even when no repair count has yet
been incremented. Keep it true during further implementation until acceptance.
A remediation child includes the failed task ID in `repair_of`. When `--project`
is provided, the resolver validates the existing task graph and checks unfinished
referenced tasks' persisted repair counts as an additional escalation signal.
It does not parse prose to decide whether acceptance failed or discover undeclared
remediation relationships; the coordinator remains responsible for those facts.

## Matching rules

Allowed selectors in a rule's `match`:

| Selector | Meaning |
| --- | --- |
| `roles`, `confidence` | Assessment value is one of the listed values |
| `operations_any`, `components_any`, `tools_any` | At least one listed value is present |
| `operations_only` | Every phase operation belongs to this list |
| `tags_all` | Every listed tag is present |
| `dimensions_min`, `dimensions_max` | Inclusive per-dimension thresholds; all specified limits apply |

Omitted selectors impose no constraint. An empty `match` matches every phase.
Use separate rules for alternatives (OR). For example, add this project rule to
route bounded vehicle work more conservatively without upgrading every Unreal task:

```json
{
  "id": "vehicle-integration",
  "description": "Vehicle physics spans control, collision and movement; use Astra for coupled changes.",
  "priority": 750,
  "match": {
    "roles": ["implementation", "recovery"],
    "components_any": ["vehicle-physics"],
    "operations_any": ["coding", "integration", "diagnosis"],
    "dimensions_min": {"coupling": 2}
  },
  "profile": "demanding"
}
```

Priorities are policy decisions: shipped generation rules use 900, demanding
scores 800, low confidence 700, substantial scores 600, engineering 500, bounded
visual work 400, and focused work 300. An explicit higher-priority project rule
can override a generation default, but cannot override repair escalation. Inspect
the full trace before approving such a policy change.

## Runtime availability and dispatch

Capture current delegation models and supported efforts, filtered by user/project
restrictions, in `runtime.json`. An example inventory, not an availability promise:

```json
{
  "model_selection": true,
  "models": {
    "gpt-6-luna": ["low", "medium", "high"],
    "gpt-6.1-terra": ["low", "medium", "high"],
    "gpt-6.1-sol": ["low", "medium", "high"],
    "gpt-6-astra": ["low", "medium", "high"]
  }
}
```

```sh
python3 scripts/model_routing.py resolve --project /path/to/project --assessment assessment.json --runtime runtime.json
```

Output includes status, profile, model/effort, matched and rejected rules with
reasons, repair signals, skipped fallback candidates, and SHA-256 fingerprints of
policy, assessment and runtime. It never reports that an agent was dispatched.
Exit codes: 0 for valid/selected or passing replay; 1 for replay expectation
mismatches; 2 for invalid input; 3 for blocked routing. `--config candidate.json`
may be combined with `--project` to preview a candidate policy against current
repair state without installing it. Re-resolve if scope, phase, history, policy or
runtime availability changes; never reuse a stale result for a different role.

## Tuning against results

Save the assessment and decision alongside local task evidence. In contract notes
retain a compact reference with policy hash, role, rule/profile, requested model
and effort, actual identity if observable, and artifact revision. After independent
verification, record pass/fail/not-tested, failed criteria, cause (quality,
tool/environment, missing input or unclear requirement), repair attempts, and
observed elapsed time/token/cost measurements when available. Unknown costs remain
unknown. Keep original attempts separate from repairs; a repair pass does not turn
the initial model's failure into a first-pass success.

Tune by comparable operation/component/rubric/role cohorts. Compare first-pass
acceptance and total effort through accepted delivery, including Astra repair and
re-verification. Keep tool outages separate from quality failures and report sample
counts. A single success does not establish general competence; different task
mixes do not establish a causal model advantage. Start with narrow changes backed
by repeated observations; do not automatically weaken policy while executing tasks.

Use saved assessments and runtime snapshots as offline regression cases. Each case
has `id`, `assessment`, `runtime` and `expected`. `expected` requires `status` and
may assert `profile`, `model` and `reasoning_effort`. Put these in a JSON array:

```sh
python3 scripts/model_routing.py evaluate --config candidate.json --cases routing-cases.json
```

Replay reports each selection, mismatched expectation and full trace. Include
ordinary successes, failures, mixed operations, uncertain assessments, repairs
and unavailable-model cases. Expectations express intended routing, not measured
model ability. Proficiency changes need actual task outcomes, not just passing
replay. Have the coordinator install a reviewed candidate only under user direction;
preserve the previous policy in version control or a recoverable copy, and do not
alter already-running assignments. Restoring that copy restores the previous
routing on the next resolution.

## Compatibility and limits

This is additive: absent configuration retains the prior routing defaults, old
project/index/checkpoint/contract formats and CLI commands remain supported, and
no required metadata is added to those formats. Initializer reruns preserve an
existing policy byte-for-byte. The project validator checks it only when present.
No migration is required; no existing project file is rewritten by resolution.
The tests cover these claims, deterministic decisions, malformed inputs, policy
customization, repair recovery, runtime fallback and offline replay.

The policy does not change production permissions, tool access, deferred work,
provider allowance, independent verification, repair caps or required user checks.
It cannot guarantee a model's competence, discover actual runtime models by itself,
or enforce a coordinator's compliance with dispatch instructions.
