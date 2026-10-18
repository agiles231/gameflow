# GameFlow glossary

These terms describe the current GameFlow workflow. The project-local
`.gameflow/GLOSSARY.md` is for the game's own vocabulary; it is separate from
this plugin glossary. Definitions clarify existing instructions and do not add
task states or grant new authority.

## Checkpoints and source control

**Checkpoint:** A recorded, recoverable point in work. It identifies the current
task and phase, actual artifacts, verification status, outstanding jobs or
decisions, and the next action. A checkpoint may contain incomplete or
uncommitted work. The word alone does **not** mean a Git commit, successful
acceptance, or a clean working tree.

**Checkpoint commit:** A Git commit that preserves identified task changes.
Autopilot requires a task checkpoint commit after independent acceptance and
before selecting another task. A commit preserves a revision; Git itself does
not establish correctness or acceptance. A task may be accepted while its commit
is still pending or failed; record that distinction explicitly.

**Bookkeeping commit:** A Git commit of run records, handoff updates and task
commit references not already included in task commits. It must not capture
unrelated user changes. Recording a commit's hash does not require recursively
committing the hash of each bookkeeping commit.

**Baseline:** The repository's starting state for an operation or run, including
HEAD and staged, unstaged and untracked changes. A list of dirty paths describes
what already existed; it does not prove who owns each change.

**Adopted task changes:** Previously existing changes explicitly reconciled as
part of the task being continued, under sufficient user authority. Adoption
does not erase unrelated edits or replace verification. Resume reconciles recorded identities, existing authority, prior-owner liveness
and shared-file deltas before adoption. Recognized same-task checkpoints do not
require renewed permission; unresolved mixed ownership still requires reconciliation.

**Handoff:** The concise durable record in `.gameflow/sessions/CURRENT.md` that
allows the next session to continue. It records current work, completed changes,
verification status, blockers, outstanding jobs, uncommitted state and next
actions. It should distinguish current truth from historical events.

## Tasks and acceptance

**Task:** One bounded deliverable with a stable ID, contract, dependencies,
acceptance criteria and recoverable checkpoint. The canonical task graph is
`.gameflow/tasks/index.json`.

**Implementation complete / `verify`:** The implementer has produced the
deliverable and evidence. Independent acceptance is still pending. Successful
tool calls, file existence and the implementer's own tests do not by themselves
move the task to `done`.

**Independent acceptance / `done`:** A distinct verifier has checked every
required criterion against the identified artifact revision and the coordinator
has recorded the pass. Acceptance applies to that revision; changing relevant
artifacts can invalidate it. `done` records acceptance, not necessarily a
successful Git commit. Deferred required features are not complete.

**`planned`:** A defined task not yet established as ready to execute.

**`ready`:** Dependencies are done and required inputs exist. A coordinator may
claim the task for execution. A resumed task may already have partial artifacts;
ready does not imply that implementation must start from scratch.

**`executing`:** A coordinator has claimed the task and implementation is in
progress. Recorded ownership must be reconciled on resume; a status label is not
proof that a worker or application process is still running.

**`blocked`:** Work cannot currently proceed because of a specific missing input,
decision, capability or other recorded obstacle. Resolve the obstacle and check
prerequisites before resuming. A blocked task need not prevent unrelated work.

**`deferred`:** Work deliberately postponed by scope or policy. Deferred tasks
must have no dependents and retain a reason and reactivation condition. They
remain unfinished. Explicit user direction is required to reactivate deferred
rigging/animation; a newly available tool alone is insufficient.

**Repair attempt:** A bounded correction after a failed acceptance criterion.
Consumed repair allowances survive sessions and worker changes. Preserve prior
findings rather than resetting the counter when a task resumes.

## Runs, workers and jobs

**Run:** One bounded autopilot invocation, governed by elapsed-time, completed
cycle and repair limits. Ending a run does not imply that all tasks or external
jobs have finished, or that a background agent will continue working.

**Completed task cycle:** Within autopilot, selection or recovery of a task,
implementation as needed, independent acceptance, and the required successful
task checkpoint commit. Only then may autopilot advance to another task. A
partial checkpoint, provider submission, deferred task or failed commit is not
a completed cycle.

**Job:** An external provider operation, such as a Meshy generation request,
identified by its actual provider job ID. A job can outlive a run. Resume it by
checking its status and recovering outputs; do not resubmit because a session
ended or progress appears slow. Job success is not full task acceptance.

**Owner / coordinator:** The agent responsible for assigned work. Only one
coordinator writes shared workflow state at a time. Worker ownership is not a
process lock, and shared editor access requires separate serialization. An old
owner must be checked for liveness before reassignment.

**Checkpoint metadata:** The optional versioned task-index checkpoint records
resume phase, authority, change ownership, artifact identities, jobs, repair
counts and commit state separately from task status. Legacy records remain
valid and are reconciled when resumed. Structural validation does not establish
live worker ownership or confer authority to overwrite changes.

## Optional manual asset review

**Awaiting optional review:** A completed asset revision has not received explicit
manual approval. It remains in the review queue without blocking technical
acceptance, task completion, commits or unrelated production. Silence is neither
approval nor disapproval.

**Review queue:** Durable revision-bound records of delivered assets and explicit
user decisions. Blender presents the five most recently completed unapproved
current revisions; older entries stay tracked. A replacement revision requires
its own review record and does not inherit the previous revision's approval.

**Review scene:** A dedicated Blender presentation of copies or linked sources,
labeled by asset and revision. It does not replace production source authority.
Refresh is deferred when it would disturb user work or a live application owner.

**Disapproval / interactive revision:** Explicit user feedback reopening the
asset's original task to address a named issue. Preserve prior acceptance and
artifacts as history, record downstream impact, and revise interactively.
Unrelated work may continue; the rejected task is not selected for unattended
regeneration. New delivery requires fresh technical acceptance.
