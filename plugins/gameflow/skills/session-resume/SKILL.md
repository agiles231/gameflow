---
name: session-resume
description: Resume work in a GameFlow game project from durable state without relying on previous chat history. Use at the beginning of a new session or when asked what work should happen next.
---

# Resume a GameFlow session

Follow the bootstrap procedure in the project's managed GameFlow block in `AGENTS.md`. It owns the reading sequence; do not substitute historical handoff instructions. Run the GameFlow validator and resolve inconsistencies before production work. The compact view never establishes authority, worker liveness, acceptance, or commit verification. Read full selected/recovery records and their contracts.

Resume is read-only with respect to tooling upgrades: do not run migration automatically. For an explicit upgrade request, use the project-init skill's migration procedure.

Before new selection, follow [the checkpoint recovery protocol](../task-orchestration/references/checkpoints.md): reconcile live ownership and jobs, accepted-but-uncommitted work, pending verification, partial implementation, and resolved blockers. Capture the inherited baseline before any bookkeeping writes. Recognized unchanged checkpoints resume under existing authority without another adoption question. Then select a `ready` task whose dependencies are all `done`. If none exists, determine whether a `planned` task has satisfied prerequisites and can become `ready`, or follow [blocker resolution](../task-orchestration/references/blocker-resolution.md): attempt an authorized prerequisite and ask for the precise missing input rather than ending with a blocked queue. Run `scripts/task_context.py --project PROJECT --task TASK-ID`, read its contract, then load the required files or sections. Read legacy or unparsed context directly; a packet never replaces the contract. Do not load temporary verification images or unrelated project history.

Before ending, update the task state and `.gameflow/sessions/CURRENT.md`. The handoff must state the active milestone, completed changes, next recommended task, exact blockers, verification status, and any uncommitted or externally held state needed to resume.


Reconcile executing and verify tasks before selecting new work: inspect recorded worker/job identities and artifact revisions, preserve dirty user files, and do not assume an old session is still running or has finished. Continue pending independent verification without reimplementing the artifact. Keep consumed repair counts and provider reservations across resumes. Discover current application capabilities only for the selected task. Never resume billable jobs by resubmitting them.

Skip `deferred` work, including all rigging and animation production. Preserve its reason/reactivation condition; do not reactivate it because a provider appeared; deferred tasks must have no dependents. Read effective Meshy settings from `.gameflow/tools/meshy.json` via meshy-config before generation. Future providers remain inactive.

Respect `execution_mode: interactive`: resume implementation only in a user-directed interaction; unattended runs retain its next action and choose disjoint work.

## Planning and retention

Follow [planning](../../docs/PLANNING.md) and [artifact retention](../../docs/ARTIFACT_RETENTION.md). Respect project-authored overrides. Keep detailed verification and experiment payloads local-only, with compact revision-bound conclusions in tracked contracts. Do not infer acceptance from task migration or missing local evidence.
