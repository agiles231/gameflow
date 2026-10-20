---
name: autopilot
description: Autonomously advance a GameFlow project through ready tasks, implementation, verification, repair, and completion within explicit run limits. Use for unattended or scheduled game-development runs.
---

# Run GameFlow autonomously

Advance the project without routine human confirmation. This command authorizes ordinary project-local implementation, testing, application automation, verification, task-state updates, creation of necessary child tasks, and local Git commits for verified tasks. It also authorizes one end-of-run push of verified run commits and final bookkeeping to the configured GitHub upstream under the Finish rules, unless the user or project explicitly prohibits pushing. It does not authorize pull requests, purchases, publishing, credential changes, destructive loss of user work, external communications, or invention of unresolved creative direction.

## Start

Read the normal GameFlow resume files and `.gameflow/AUTOPILOT.md` when present. Run the project validator. Confirm the project is a Git worktree and that Git author name and email are configured. Capture the inherited baseline before recording the run start in `.gameflow/sessions/CURRENT.md`.

Inspect Git HEAD and staged, unstaged, and untracked changes before any run writes. Follow [the checkpoint protocol](../task-orchestration/references/checkpoints.md): classify inherited work as recognized task checkpoints, unrelated edits, or ambiguous changes. Resume recognized checkpoints under existing authority without renewed permission; preserve unrelated edits. Reconcile mixed ownership before touching affected changes, using prior evidence and explicit continuation authority when available. Only unresolved ownership or authority requires a question. A dirty tree alone is not a stop condition.

Record the tasks selected for this bounded run in the handoff, including recovered work and any required child/repair tasks added during execution. Do not remove unfinished selections to declare success. Completion of this run is distinct from completion of the entire game. Use the limits in `AUTOPILOT.md`. If it is absent, default to at most three completed task cycles, 90 minutes elapsed time, and one repair attempt per failed acceptance criterion. Always leave enough time to write a clean checkpoint. A scheduled run must stop before it could overlap the next scheduled run.

## Concurrent task loop

Use [the concurrent scheduling protocol](../task-orchestration/references/concurrent-scheduling.md). This skill authorizes bounded subagent delegation for eligible independent tasks. Fill the available worker slots instead of waiting for a whole task cycle before dispatching another task. Honor stricter project or user limits. Tasks with `execution_mode: interactive` remain held for user-directed revision; reconcile their jobs/evidence safely, but never autonomously implement or regenerate them. Skip deferred tasks.

1. Reconcile live ownership, provider jobs, accepted-but-uncommitted tasks, pending verification and partial implementation in checkpoint order. Recover before selecting new work, but healthy pending jobs or a task-local blocker do not prevent disjoint tasks from running. Dependencies require accepted prerequisites with reconciled commit state.
2. Admit eligible tasks in priority order, reserving task-cycle capacity for every selected unfinished task. Claim disjoint outputs and required application resources through the coordinator. Dispatch independent implementation workers up to actual runtime and project limits. Promote planned work only when its inputs and prerequisites exist.
3. Process worker/job results as they arrive. Do not wait for a batch barrier. Release inactive ownership after reconciliation, record the checkpoint, and dispatch the next runnable phase or independent task. Provider jobs may run concurrently after serialized coordinator reservations/submissions; waiting jobs retain their task reservation but need no idle worker.
4. Move completed implementation to `verify` and freeze its artifact revision. Assign a distinct subagent or separate session to verify actual outputs against the acceptance criteria; the implementation report is not proof. Make verifier capacity available as implementations return. If independent verification is unavailable, retain `verify` and record the limitation. Keep transient images in the temporary verification directory and remove only that attempt's captures after recording conclusions.
5. On success, the coordinator records acceptance and marks the task `done`. Serialize its checkpoint commit through the protocol below; dependent work waits for commit reconciliation. Independent workers may continue on disjoint outputs while the coordinator commits.
6. On failure, return the affected task to `executing`, apply the remaining bounded repair allowance, then assign fresh independent verification of the new revision. Preserve consumed repair counts across workers and resumes. A task-local failure does not cancel disjoint work.
7. Refill free slots after every result, resource release, and reconciled commit. When there is no runnable phase, wait on known workers/jobs within the elapsed-time limit; an empty ready queue is not completion while selected work remains active.

### Serialized task commits

Only the coordinator stages or commits. Review and explicitly stage only this task's implementation, durable evidence, contract and reviewed shared-state deltas. Never stage another live task's outputs or inherited unrelated changes. Freeze the accepted paths until commit reconciliation; stage exact shared-file deltas or a reviewed coordination-only snapshot that records other workers' status without claiming their completion. Inspect the staged diff and run an appropriate sanity check before committing `TASK-ID: imperative summary`. Include this task's repairs in its commit.

Record the hash in completion evidence and the handoff; include hash linkage in final run bookkeeping without automatic amendments or recursive empty commits. When no changes remain, recover an already-created matching commit from Git. If attribution, staging or committing fails, preserve accepted work, record pending/failed commit state and the exact recovery action, and stop new dispatch while safely checkpointing active workers. Do not admit dependent work or claim a successful commit. Defer pushing to Finish.

Prefer deterministic commands and application APIs over UI control. Use desktop control only for operations without a reliable programmable path, and verify the resulting application state.

## Stop conditions

A full task-cycle reservation cap stops new task admission, not the implementation, verification, repair or commit phases already reserved. Finish those phases while time and remaining repair allowance permit. Stop cleanly when the elapsed-time limit or another applicable hard limit is reached; no task or selected phase is runnable and no tracked worker/job can make progress; a material creative/product decision blocks all available work; additional authorization is required; an acceptance failure persists after its allowed repair and no independent ready work remains; a verified task cannot be committed cleanly; tooling or project state is unsafe or inconsistent; or all tasks needed for the defined game completion criteria are `done`.

Do not mark the game complete merely because the current milestone or queue is empty. Completion requires every criterion in `PROJECT.md` to be satisfied with durable verification evidence.

## Finish

Stop dispatch before the deadline and drain or safely park active workers/jobs without losing partially applied actions. Do not clear a live owner or cancel a paid job merely to make the run appear finished. Write an adoptable checkpoint for every unfinished selection, retaining job identities, authority, hashes, and repair counts. Validate GameFlow state and update `.gameflow/sessions/CURRENT.md` with tasks completed, verification results, task commit hashes, any deliberately uncommitted baseline changes, remaining ready work, blockers, decisions required, limits consumed, and the next action. Commit final run-only bookkeeping with a clearly labeled GameFlow bookkeeping commit only if those changes are not already included in the last task commit; never mix them into unrelated user changes.

After final bookkeeping, push once when every selected run task is independently accepted, `done`, and committed, and no selected task, live worker/job, verification, ownership or commit recovery remains unresolved. A limit reached between completed task cycles may qualify; unfinished selected work does not. Other unselected backlog tasks do not require waiting for the entire game. Honor explicit no-push policy.

Use only the current branch’s configured GitHub upstream; never create an arbitrary remote, force-push, or push other refs. Fetch that upstream, confirm a fast-forward update is possible, and review the exact outgoing commits/diff for scope and secrets, including inherited commits. Do not include unrelated inherited commits without existing authority. Push the explicit current-branch-to-upstream-branch refspec. Proven unrelated uncommitted baseline edits alone do not prevent a push. If upstream is missing/non-GitHub, history diverged, scope is uncertain, or push fails, preserve local commits, record the exact blocker/recovery action, and report delivery as pending; do not rewrite history or retry blindly. Record the intended remote/ref and commit range before pushing and verify remote branch identity afterward. Report the confirmed pushed hash; a local post-push receipt may remain for next bookkeeping (do not create recursive commits/pushes merely to record the push itself).

Scheduled runs should remain quiet during routine progress. Notify the user only on game completion, a blocker, a failed run, a required decision/authorization, or an inconsistent state that needs attention.

## CLI operation and decisions

This skill runs within the current Codex session; it does not install a scheduler, restart a terminated process, or promise continuous background execution. Check elapsed time between operations and choose bounded jobs that leave checkpoint time. If a job cannot finish before the limit, record its identity and recovery/status procedure; do not submit it again on resume.

Make reversible production choices within the approved brief and record meaningful rationale. Ask only when a choice materially changes creative direction, scope, acceptance, authorization, or budget. Honor existing project policies rather than overwriting them with these defaults.

Use task-orchestration for worker ownership and independent verification, tool-discovery before application operations, and the production skill matching the task. Failed verification consumes the task's existing repair allowance, including across resumed sessions; a new worker does not reset it. If one task is blocked, advance unrelated ready work when the run remains safe and policy permits. Stop the run for global state/authority problems.

Use asset-generation for paid providers. A connected account does not grant spending authority. Coordinator records reservations and reconciles jobs before starting further billable work. At finish, record workers still running, job IDs, application/file state, limits consumed, and any reserved or uncertain charges.

## Meshy and deferred production

All complex mesh generation uses Meshy MCP with `.gameflow/tools/meshy.json` resolved through meshy-config: project defaults, selected recipe, then task overrides. Only explicit simple-shape tasks may create meshes locally. Blender performs noncreative integration only. Missing Meshy capability/allowance blocks generation; no provider, script, UI or local-modeling fallback. Future providers never autoactivate. All rigging and animation production is `deferred`; skip it; deferred tasks must have no dependents, and rigging/animation should be one combined deferred leaf per asset depending on the delivered static mesh. Resume only after explicit user direction revises the policy. Deferred tasks cannot count as complete.

Use independent cheap delivery acceptance for Meshy assets. Do not start artistic or numerical quality audits, render batches, creative repair or unrequested variations. Preserve ordinary gameplay/build validation. Reconcile inherited criteria with the approved scope durably before execution rather than silently accepting them.
