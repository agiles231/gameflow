# GameFlow workflow

## Durable state

The managed GameFlow block in `AGENTS.md` owns the project bootstrap sequence. Follow it rather than copying its procedure into handoffs or skills. `scripts/resume_view.py` supplies the compact graph and full selected/recovery records; it does not establish authority or replace project validation. The task graph and asset manifest are canonical machine-readable state. Markdown files explain intent and decisions.

Never depend on a prior conversation to resume work. Before stopping, update the active task, task index, relevant decision or verification record, and `sessions/CURRENT.md`.

## Task lifecycle

Tasks move through `planned`, `ready`, `executing`, `verify`, `done`, `blocked`, or `deferred`.

```text
planned -> ready -> executing -> verify -> done
                         |          |
                         +-> blocked <-+
```

A task is ready only when its dependencies and inputs exist. A task is small enough when it has one principal deliverable, can complete at a clean checkpoint, and has acceptance criteria that can be evaluated without inventing missing creative direction.

Workers do not expand scope. Unexpected work becomes a child task. Implementation workers move work to `verify`; an independent verification pass moves it to `done`.

## Context packets

Markdown task contracts own context; task-index JSON does not duplicate it. New contracts use `## Context` with `### Required` Markdown links and descriptive `### Excluded` guidance. Required links are project-root-relative local paths, optionally with conventional Markdown heading fragments; percent-encode spaces. Do not use absolute paths, URLs, parent traversal, or links escaping through symlinks. List one link per bullet; additional prose is preserved as unparsed context for direct reading.

After selection, run `scripts/task_context.py --project PROJECT --task TASK-ID`. It validates the graph and returns the selected record, bootstrap references, dependency statuses, recovery reasons, required references and warnings without concatenating files or following links recursively. Missing files/headings and invalid paths return a nonzero status. Legacy prose remains valid and is returned for direct reading; the helper does not infer or omit requirements. An incomplete context packet never establishes readiness. Load the contract and only the applicable references. A worker completion report contains changed artifacts, commands, acceptance evidence, residual risks, and proposed follow-ups; it does not reproduce its full working context.

## Visual observations

Approved references and final artifacts are durable. Screenshots, viewport captures, and intermediate renders are observations. Put observations in `.gameflow/verification/temporary/`, inspect them in a narrow context, write conclusions to a result JSON file, then remove them. Never place temporary observations in task descriptions or session handoffs.

Verification results record the task, artifact hashes or revisions, application versions, view/camera configuration, checks, outcome, and durable evidence paths.

## Capability-based automation

Use native CLI for builds, supported MCP operations for connected application work,
application scripting for gaps, and UI only when needed. Discover actual schemas
and verify project/file identity and host paths before edits. Prefer suitable
Meshy MCP for every complex mesh within configured allowance. Local creation is limited to explicit simple shapes; Blender integration is noncreative. No direct HTTP, UI, local modeling or other-provider generation fallback. All rigging/animation production is deferred and future providers never autoactivate.

## CLI and worker boundary

Skills operate inside Codex sessions, not a background service. The coordinator is
the single writer of shared task/asset/handoff state and owns application leases
recorded in task contracts. Workers report proposed transitions and evidence.
Autopilot schedules independent eligible tasks concurrently within runtime slots,
project limits and reserved task cycles, refilling as each phase finishes. Tracked
provider jobs may overlap while coordinator submissions, shared application
mutations and Git commits remain serialized. Workers never stage or commit.
Only a distinct verifier can accept frozen artifacts. Preserve IDs and optional
worker/provenance metadata for future UI readers without a new task database.

## Skill extensions

Qualify application-specific skills with real workflows and explicitly identify stages not yet live-tested. Each production skill should define inputs, outputs, application/version assumptions, permitted execution routes, acceptance checks, and recovery behavior. It should consume and update the shared task and asset contracts rather than inventing another state system.

## Meshy configuration and delivery

Use meshy-config to maintain nonsecret `.gameflow/tools/meshy.json`. Effective settings resolve project defaults, then the selected recipe, then explicit task overrides. Inspect actual Meshy MCP schemas, preserve job IDs/downloads/settings/provenance, and reconcile uncertain jobs before resubmitting. Credentials remain outside project state. Missing provider support or allowance blocks only dependent work.

Meshy acceptance remains independent but cheap: completed job, expected readable files, dependencies, intended import/loading and recorded identity/provenance. Artistic/anatomy/topology reviews, numerical quality audits, render batches and creative repair require an explicit request. Gameplay/build tests are unchanged. Record approved acceptance-scope changes rather than claiming inherited audits passed.

## Deferred work

Use `deferred` for postponed work, including every rigging/animation production task. Preserve artifacts, reason and explicit reactivation condition; reconcile live ownership before clearing it. Deferred is not done and is excluded from autonomous selection. Deferred tasks must have no dependents. Rescope affected active task contracts explicitly before removing edges; record the decision. Combine rigging and animation into one deferred leaf per asset depending on delivery of its static mesh. Only explicit direction satisfying its reactivation condition returns it to `planned`; normal prerequisites govern readiness. New provider availability does not reactivate work. Required deferred work prevents overall completion.

## Optional manual asset review

Manual review is independent of technical acceptance and never an approval gate.
After each completed asset delivery, retain a revision-bound review entry and
refresh a dedicated Blender review scene with the five newest unapproved assets.
Older entries remain tracked. Silence changes neither technical acceptance nor
queue membership. Explicit approval applies only to the displayed revision.

Protect user-owned Blender sessions and defer presentation when unsafe; record a
pending refresh so it can be retried without blocking unrelated production. A
presentation failure is not an asset acceptance failure. Show stable asset IDs,
revision labels and materials; never alter the production sources for display.

Explicit disapproval reopens the original task for interactive revision, preserves
the prior accepted files and evidence, and records downstream consumers requiring
recheck. Unrelated autonomous work may continue. Replacement artifacts need fresh
independent acceptance and a new optional review entry. See the
[asset pipeline](../skills/asset-pipeline/SKILL.md) for queue and presentation rules.

## Recoverable checkpoints

Task acceptance and Git commit status are distinct. Resume pending provider jobs,
implementation, verification, repairs, or an accepted task's pending commit before
selecting new work. A valid checkpoint records phase, task-owned changes, evidence,
actual jobs and the next action. Preserved unrelated changes remain protected.

Reconcile a previous worker's liveness and changes before adopting ownership; do
not reject a checkpoint merely because its own recorded files are dirty. Review
shared-state deltas and stop only the affected ambiguous action when attribution
is unresolved. Historical projects can be reconciled into checkpoint metadata
without discarding work or repeating already-paid jobs. See
[autopilot](../skills/autopilot/SKILL.md) for the lifecycle protocol.

Autopilot pushes verified commits and final bookkeeping once all tasks selected for its bounded run are complete, using the configured GitHub upstream after scope and fast-forward checks. Explicit no-push policy overrides this default. Incomplete runs retain local checkpoints; delivery does not wait for the entire game.


## Guidance upgrades

Fresh initialization uses the current shared contract and handoff templates. Existing projects remain schema-v1 compatible. Tooling migration is explicit and preserves authored state; see [migration](MIGRATION.md) when upgrading a project. Handoffs retain current facts and evidence identities, not copied workflow procedures or conversation history.
