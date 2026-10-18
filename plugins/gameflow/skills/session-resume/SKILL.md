---
name: session-resume
description: Resume work in a GameFlow game project from durable state without relying on previous chat history. Use at the beginning of a new session or when asked what work should happen next.
---

# Resume a GameFlow session

Read, in order:

1. `.gameflow/PROJECT.md`
2. `.gameflow/CONSTRAINTS.md`
3. `.gameflow/sessions/CURRENT.md`
4. `.gameflow/tasks/index.json`

Run the GameFlow validator. Resolve inconsistencies before production work.

Before new selection, follow [the checkpoint recovery protocol](../task-orchestration/references/checkpoints.md): reconcile live ownership and jobs, accepted-but-uncommitted work, pending verification, partial implementation, and resolved blockers. Capture the inherited baseline before any bookkeeping writes. Recognized unchanged checkpoints resume under existing authority without another adoption question. Then select a `ready` task whose dependencies are all `done`. If none exists, determine whether a `planned` task has satisfied prerequisites and can become `ready`, or report the concrete blocker. Read its contract, then load only the files or sections listed under Context. Do not load temporary verification images or unrelated project history.

Before ending, update the task state and `.gameflow/sessions/CURRENT.md`. The handoff must state the active milestone, completed changes, next recommended task, exact blockers, verification status, and any uncommitted or externally held state needed to resume.


Reconcile executing and verify tasks before selecting new work: inspect recorded worker/job identities and artifact revisions, preserve dirty user files, and do not assume an old session is still running or has finished. Continue pending independent verification without reimplementing the artifact. Keep consumed repair counts and provider reservations across resumes. Discover current application capabilities only for the selected task. Never resume billable jobs by resubmitting them.

Skip `deferred` work, including all rigging and animation production. Preserve its reason/reactivation condition; do not reactivate it because a provider appeared; deferred tasks must have no dependents. Read effective Meshy settings from `.gameflow/tools/meshy.json` via meshy-config before generation. Future providers remain inactive.

Respect `execution_mode: interactive`: resume implementation only in a user-directed interaction; unattended runs retain its next action and choose disjoint work.
