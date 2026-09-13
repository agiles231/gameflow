---
name: autopilot
description: Autonomously advance a GameFlow project through ready tasks, implementation, verification, repair, and completion within explicit run limits. Use for unattended or scheduled game-development runs.
---

# Run GameFlow autonomously

Advance the project without routine human confirmation. This command authorizes ordinary project-local implementation, testing, application automation, verification, task-state updates, creation of necessary child tasks, and local Git commits for verified tasks. It does not authorize pushes, pull requests, purchases, publishing, credential changes, destructive loss of user work, external communications, or invention of unresolved creative direction.

## Start

Read the normal GameFlow resume files and `.gameflow/AUTOPILOT.md` when present. Run the project validator. Confirm the project is a Git worktree and that Git author name and email are configured. Record the run start in `.gameflow/sessions/CURRENT.md`.

Inspect the working tree before selecting work and preserve the baseline list of modified, staged, and untracked paths. Pre-existing changes belong to the user or another task: do not stage, rewrite, discard, or include them in an autonomous commit. A dirty tree is acceptable only when the selected task can be isolated confidently. Stop before implementation if task-owned changes would overlap or cannot be distinguished from the baseline.

Use the limits in `AUTOPILOT.md`. If it is absent, default to at most three completed task cycles, 90 minutes elapsed time, and one repair attempt per failed acceptance criterion. Always leave enough time to write a clean checkpoint. A scheduled run must stop before it could overlap the next scheduled run.

## Loop

Repeat while within limits:

1. Select the highest-priority `ready` task whose dependencies are `done`. Promote a `planned` task only when all inputs and dependencies demonstrably exist.
2. Execute the task according to its contract and the task-execution rules. Keep scope bounded; discovered work becomes a child task.
3. Move completed implementation to `verify` and write completion evidence.
4. Begin a distinct verification pass. Re-read the acceptance criteria, inspect actual outputs, and do not treat the implementation report as proof. Keep transient images in the temporary verification directory and remove them after recording conclusions.
5. On success, record the verification result, mark the task `done`, and update the task graph and current handoff for that completed task.
6. Create the task checkpoint commit before selecting another task:
   - Review the working tree and identify only the implementation, durable verification evidence, task contract, task index, and handoff changes owned by this task.
   - Stage those paths explicitly. Never use broad staging when it could capture pre-existing or unrelated changes.
   - Inspect the staged diff, run an appropriate staged-diff sanity check, and confirm no unrelated or secret material is included.
   - Commit with `TASK-ID: imperative summary`, using the actual task ID. Include repairs in the same task commit.
   - Record the commit hash in the task completion evidence and handoff. If recording the hash changes tracked files, include that linkage in the next bookkeeping commit only when the project defines one; do not amend automatically or create an empty recursive commit solely to record its own hash.
   - Do not push or create a pull request unless the user separately authorizes it.
   - If there are no task-owned changes to commit, or staging or committing fails, stop and record the exact state. Do not mark the checkpoint as successfully committed and do not advance to another task.
7. On verification failure, return the task to `executing`, make one bounded repair attempt when allowed, then verify again. Do not loop indefinitely on the same failure.
8. After a successful task commit, select the next ready task.

Prefer deterministic commands and application APIs over UI control. Use desktop control only for operations without a reliable programmable path, and verify the resulting application state.

## Stop conditions

Stop cleanly when a run limit is reached; no task is ready; a material creative/product decision is absent; additional authorization is required; an acceptance failure persists after its allowed repair; a verified task cannot be committed cleanly; tooling or project state is unsafe or inconsistent; or all tasks needed for the defined game completion criteria are `done`.

Do not mark the game complete merely because the current milestone or queue is empty. Completion requires every criterion in `PROJECT.md` to be satisfied with durable verification evidence.

## Finish

Validate GameFlow state and update `.gameflow/sessions/CURRENT.md` with tasks completed, verification results, task commit hashes, any deliberately uncommitted baseline changes, remaining ready work, blockers, decisions required, limits consumed, and the next action. Commit final run-only bookkeeping with a clearly labeled GameFlow bookkeeping commit only if those changes are not already included in the last task commit; never mix them into unrelated user changes.

Scheduled runs should remain quiet during routine progress. Notify the user only on game completion, a blocker, a failed run, a required decision/authorization, or an inconsistent state that needs attention.
