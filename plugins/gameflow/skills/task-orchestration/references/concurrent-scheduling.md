# Concurrent scheduling

Autopilot is a coordinator-driven worker queue inside the current session, not a
background scheduler. Use every available slot for runnable independent work,
subject to the existing run limits and resource ownership. A project may impose
a lower worker cap. Count the coordinator and any other live agents against the
runtime's total limit; do not hard-code a team size or launch nested workers
outside the coordinator's accounting. If delegation is unavailable, implement
sequentially and leave acceptance to a distinct session.

## Admission and recovery

Reconcile the inherited baseline and all live owners/jobs before assigning their
resources. Poll recorded provider IDs instead of repeating submissions. Recovery
phases have priority over new tasks, but waiting on a healthy known job does not
block unrelated work. Keep interactive and deferred work out of autonomous
implementation; reconcile its existing jobs/ownership without regenerating it.

For each free worker slot, choose the highest-priority runnable phase whose inputs
exist, dependencies are accepted and commit-reconciled, and required outputs and
resources are unclaimed. If a candidate conflicts, scan the remaining queue for
independent work. Promote planned tasks only after checking their prerequisites.
Do not dispatch dependent tasks together because both appear in the backlog.

Reserve one task cycle on first selection, including recovered unfinished work
and independently accepted-but-uncommitted recovery. Completed cycles plus
selected unfinished tasks must not exceed the run's task-cycle limit. Repairs,
verification and job polling do not reserve additional cycles. Child tasks do.
If inherited unfinished work already exceeds the limit, reconcile/checkpoint all
of it, admit no new tasks, and do not discard selections to manufacture capacity.
When delegation or independent verification is unavailable, avoid accumulating
more new implementations than the run's reserved task capacity allows.

Before spawning, reserve the task and disjoint output scope under the coordinator;
record the returned worker ID before permitting writes (a worker may load its
packet while awaiting this claim). Record application leases in the task contract,
not a second scheduler database. Include the existing orchestration worker packet,
remaining repair/time limits, and explicit prohibition on shared-state/Git writes.
Workers return proposed state changes. Only the coordinator allocates child IDs,
writes canonical workflow state, stages/commits, or reserves/submits paid jobs.

## Progress and resource release

React to each result; do not wait for the slowest member of a dispatch batch.
Prioritize recovered work and pending verification/commit phases over admitting
new implementation so completed outputs do not starve. Release or close finished
agents through the runtime's supported lifecycle before replacement; idle agents
may still consume runtime slots. If no close/release API exists, reuse an inactive
worker for an eligible phase using a newly supplied task packet; do not assume
interrupting it frees a slot or erases its conversation. A worker may verify
another task only with a verification-specific context packet and no implementation
involvement in the artifact under review. If no eligible independent worker or
slot exists, retain verify for a separate session instead of exceeding the cap. Never
have an implementer accept its own task or repair. A separate fresh verifier is
preferred, with frozen hashes and acceptance criteria rather than implementation
claims.

Hold output ownership through verification and commit reconciliation. Release a
shared application lease at a safe saved boundary, after confirming no worker is
still mutating it. Unreal/Blender instances, PIE, imports, saves and overlapping
build outputs are exclusive resources even for different asset names. An editor
verification also needs the lease; a nominally read-only inspection that changes
selection, opens a file or runs PIE is not isolated from concurrent mutation.
Truly disjoint source work or immutable-file inspection may continue. Never
interrupt user-owned applications to obtain a lease.

Apply the effective user/project allowance policy; explicit overrides may replace
local reservations/accounting with credential-enforced limits. Otherwise, for paid
work the coordinator serially reconciles allowance, records each safe
maximum reservation and submits each authorized independent request, persisting
its job ID/outcome before the next submission. Provider jobs may then run at the
same time if provider limits and the remaining shared allowance permit. Include
outstanding and uncertain charges; an uncertain submission blocks further work
against that allowance until safely reconciled. A waiting job keeps its task
reservation and output scope but requires no dedicated idle agent. Coordinate
bounded polling while other workers advance. No duplicate submissions, extra
variants, provider fallback or reduced delivery acceptance.

## Verification and commits

Each returned implementation ends at verify. Record its output revision and give
an independent verifier the criteria and actual artifact. Any intervening change
invalidates affected acceptance. Serialize repairs against verification, retaining
repair counts across workers and resumes. Refill other slots with independent
phases while this task is repaired or verified.

Only the coordinator may touch the Git index. Commit a task after independent
acceptance, while its output paths are frozen. Other workers may continue only on
disjoint paths. Explicitly stage that task's changes and inspect the staged diff;
never stage another active task's outputs or preexisting unrelated changes.
Shared index/handoff changes require reviewed deltas or a coordination-only
snapshot that honestly records every participant's current phase. Such a snapshot
may record another active task's ownership/status without staging its artifacts
or claiming its acceptance. Do not let a worker rewrite a shared file while it is
being reviewed/staged. If isolation cannot be established, park conflicting
writers and reconcile before staging. Record hashes in final bookkeeping.

An accepted but uncommitted prerequisite still blocks its dependents. A commit
failure stops new dispatch globally; checkpoint active work safely instead of
abandoning workers or allowing their uncontrolled mutations. Task-local provider,
acceptance or product blockers otherwise block only affected dependencies and
resources, not independent runnable work.

## Stop and finish

Before the elapsed-time deadline, stop dispatching, request bounded checkpoints
from active workers and reconcile in-flight actions. Do not treat an empty ready
queue as a stop while runnable selected phases or known jobs remain. Do not clear
live ownership just because the coordinator is ending; record worker/job identity,
artifact state, remaining reservations, repair counts and exact next actions.
A worker timeout is not proof that its application/provider action stopped.

Finish reconciles every selected task, including repaired and newly created child
tasks. Keep unfinished selections in the handoff. Final push is possible only
under the autopilot Finish checks: all selected work independently accepted and
committed, with no unresolved live worker/job, ownership, verification or commit
recovery. There is no batch-success shortcut or self-acceptance fallback.
