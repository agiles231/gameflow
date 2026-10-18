# Recoverable checkpoints

Task status and Git commit status are separate facts. A checkpoint is resumable
state, not acceptance. Apply this exit/resume protocol to all production and
configuration work, including interactive turns.

## Durable record

The coordinator stores `checkpoint` on the existing task entry in
`.gameflow/tasks/index.json`; the contract contains the human-readable evidence.
Use this version-1 shape when creating or updating a checkpoint:

```json
{
  "version": 1,
  "phase": "verify",
  "authority": "sessions/CURRENT.md: authorized task scope",
  "base_head": "full Git commit hash before work",
  "owner": null,
  "artifact_paths": ["SourceAssets/example.glb"],
  "owned_paths": {"SourceAssets/example.glb": "sha256 hex digest"},
  "shared_state_review": "tasks/TASK-0001.md: serialized shared-state delta review",
  "preserved_baseline": {"notes.txt": "sha256 hex digest"},
  "jobs": [],
  "repair_counts": {},
  "next_action": "Assign a distinct verifier to the frozen artifact",
  "acceptance": null,
  "commit": {"state": "pending", "hash": null}
}
```

Paths are project-relative; use null for an intentional deletion. Hash only files,
never directories. `artifact_paths` names the complete output scope for acceptance, all present in
`owned_paths`. Accepted checkpoints require nonempty artifact scope covered by
the verifier revision. `owned_paths` includes outputs and evidence; index/CURRENT and
other shared records are covered by `shared_state_review`, which records the
specific reviewed delta, participating tasks, and serialization—not blanket
ownership. Do not hash the checkpoint into itself. `preserved_baseline` records
unrelated dirty identities; mixed edits in a shared file require a reviewed delta
or isolated staging. `owner` is null or a worker/session identifier; clear it only
after liveness reconciliation, retaining all durable provenance. `jobs` retains
provider IDs and recovery procedures (objects); `repair_counts` maps criteria to
consumed integer attempts. `acceptance`, when present, contains `revision` (the
owned-path hash map given to the verifier), `verifier`, and `evidence` references.
`phase` is the canonical task status; it is not a new task state. `commit.state`
is pending, failed, or committed; committed requires a Git hash.

Capture the inherited Git HEAD and staged/unstaged/untracked baseline **before**
run bookkeeping writes. At exit refresh checkpoint identities, jobs, counts,
owner, and next action. Replace current handoff status rather than accumulating
contradictory current states; archive history separately. Commit accepted changes
when locally authorized. Partial commits may be explicitly labeled partial and
never imply acceptance. Without commit authority, leave an adoptable record.

## Recovery order

1. Check actual coordinator/worker and application liveness. A live competing
   coordinator stops shared-state writes; an old owner string alone does not.
2. Reconcile recorded provider jobs; poll their IDs, never resubmit on restart.
3. Reconcile done tasks with pending/failed commits before dependent work. Keep
   current independent acceptance; retry commit, not implementation. If Git
   already contains the exact task changes (for example a crash before recording
   its hash), recover the hash from Git instead of requiring another commit.
4. Continue verification of unchanged outputs; resume partial implementation.
5. Reassess resolved blockers, then select ready work with satisfied prerequisites.

Run `scripts/checkpoint_preflight.py --project PATH` for file/acceptance/commit
identity checks of pending work. Historical committed tasks are not scanned against
today’s files; use `--task TASK-ID` only for targeted investigation or before
reusing an old accepted output. Legacy done work is reconciled only when selected
or when evidence identifies a missing commit. This read-only helper does not prove authority, live ownership,
or shared-delta isolation: inspect those operational facts separately. Recognized
unchanged checkpoints under existing authority resume without another adoption
question. Preserve unrelated edits. Changed/mixed ownership requires reconciliation;
ask only if evidence and existing user authority cannot resolve it. Legacy tasks
without metadata remain valid: reconstruct once from contracts, evidence, Git and
prior authority, then save a checkpoint. A filename alone does not prove ownership.

Changing an accepted output invalidates the affected acceptance. Reopen the task
at executing (implementation) or verify (verification-only amendment), identify
its new revision, reassess dependents that consumed the old output, and preserve
prior accepted artifacts/evidence. Do not reset repair counts merely on resume.
Task-specific blockers need not stop disjoint work; unresolved coordinator or
shared ownership conflicts do.

After task commits, record their hashes in one final bookkeeping commit. It does
not record its own hash; verify its success through Git. Unrelated dirty files may
remain and must be documented, not staged to manufacture a clean tree.

Optional manual asset review never blocks technical acceptance merely because no
approval arrived. Explicit disapproval reopens the original task as blocked with
the feedback and an interactive next action; move to executing when interactive
revision starts. Do not autonomously regenerate a disapproved asset.
