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

## Loop

Repeat while within limits. Tasks with `execution_mode: interactive` are held for user-directed revision: reconcile their jobs/evidence safely, but never autonomously implement or regenerate them, even if ready or executing. Continue disjoint autonomous work:

1. First recover live ownership, recorded provider jobs, accepted-but-uncommitted tasks, pending verification, and partial implementation in the checkpoint protocol order. Do not start dependent work until its accepted prerequisites have reconciled commit state. Then select the highest-priority `ready` task whose dependencies are `done`. Promote a `planned` task only when all inputs and dependencies demonstrably exist.
2. Execute the task according to its contract and the task-execution rules. Keep scope bounded; discovered work becomes a child task.
3. Move completed implementation to `verify` and write completion evidence.
4. Assign verification to a distinct subagent or separate session. If unavailable, leave the task at `verify`; do not self-accept. Re-read the acceptance criteria, inspect actual outputs, and do not treat the implementation report as proof. Keep transient images in the temporary verification directory and remove only this attempt’s captures after recording conclusions.
5. On success, record the verification result, mark the task `done`, and update the task graph and current handoff for that completed task.
6. Create the task checkpoint commit before selecting another task:
   - Review the working tree and identify only the implementation, durable verification evidence, task contract, task index, and handoff changes owned by this task.
   - Stage those paths explicitly. Never use broad staging when it could capture pre-existing or unrelated changes.
   - Inspect the staged diff, run an appropriate staged-diff sanity check, and confirm no unrelated or secret material is included.
   - Commit with `TASK-ID: imperative summary`, using the actual task ID. Include repairs in the same task commit.
   - Record the commit hash in the task completion evidence and handoff. If recording the hash changes tracked files, include that linkage in the final run bookkeeping commit; do not amend automatically or create an empty recursive commit solely to record its own hash.
   - Defer pushing to Finish after every selected run task has passed independent acceptance and its commit is reconciled. Pull requests still require separate authorization.
   - If no task changes remain, inspect Git for an already-created matching commit and recover its hash. If no matching commit exists, or staging or committing fails, record pending/failed commit state and the exact recovery action. Do not mark the checkpoint as successfully committed and do not advance to another task.
7. On verification failure, return the task to `executing`, make one bounded repair attempt when allowed, then verify again. Do not loop indefinitely on the same failure.
8. After a successful task commit, select the next ready task.

Prefer deterministic commands and application APIs over UI control. Use desktop control only for operations without a reliable programmable path, and verify the resulting application state.

## Stop conditions

Stop cleanly when a run limit is reached; no task is ready; a material creative/product decision blocks all available work; additional authorization is required; an acceptance failure persists after its allowed repair and no independent ready work remains; a verified task cannot be committed cleanly; tooling or project state is unsafe or inconsistent; or all tasks needed for the defined game completion criteria are `done`.

Do not mark the game complete merely because the current milestone or queue is empty. Completion requires every criterion in `PROJECT.md` to be satisfied with durable verification evidence.

## Finish

Write an adoptable checkpoint for unfinished work, retaining job identities, authority, hashes, and repair counts. Validate GameFlow state and update `.gameflow/sessions/CURRENT.md` with tasks completed, verification results, task commit hashes, any deliberately uncommitted baseline changes, remaining ready work, blockers, decisions required, limits consumed, and the next action. Commit final run-only bookkeeping with a clearly labeled GameFlow bookkeeping commit only if those changes are not already included in the last task commit; never mix them into unrelated user changes.

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
