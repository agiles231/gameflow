---
name: autopilot
description: Autonomously advance a GameFlow project through ready tasks, implementation, verification, repair, and completion within explicit run limits. Use for unattended or scheduled game-development runs.
---

# Run GameFlow autonomously

Advance the project without routine human confirmation. This command authorizes ordinary project-local implementation, testing, application automation, verification, task-state updates, and creation of necessary child tasks. It does not authorize purchases, publishing, credential changes, destructive loss of user work, external communications, or invention of unresolved creative direction.

## Start

Read the normal GameFlow resume files and `.gameflow/AUTOPILOT.md` when present. Run the project validator. Record the run start in `.gameflow/sessions/CURRENT.md`.

Use the limits in `AUTOPILOT.md`. If it is absent, default to at most three completed task cycles, 90 minutes elapsed time, and one repair attempt per failed acceptance criterion. Always leave enough time to write a clean checkpoint. A scheduled run must stop before it could overlap the next scheduled run.

## Loop

Repeat while within limits:

1. Select the highest-priority `ready` task whose dependencies are `done`. Promote a `planned` task only when all inputs and dependencies demonstrably exist.
2. Execute the task according to its contract and the task-execution rules. Keep scope bounded; discovered work becomes a child task.
3. Move completed implementation to `verify` and write completion evidence.
4. Begin a distinct verification pass. Re-read the acceptance criteria, inspect actual outputs, and do not treat the implementation report as proof. Keep transient images in the temporary verification directory and remove them after recording conclusions.
5. On success, record the verification result and mark the task `done`.
6. On failure, return the task to `executing`, make one bounded repair attempt when allowed, then verify again. Do not loop indefinitely on the same failure.
7. Update the task graph and current handoff, then select the next ready task.

Prefer deterministic commands and application APIs over UI control. Use desktop control only for operations without a reliable programmable path, and verify the resulting application state.

## Stop conditions

Stop cleanly when a run limit is reached; no task is ready; a material creative/product decision is absent; additional authorization is required; an acceptance failure persists after its allowed repair; tooling or project state is unsafe or inconsistent; or all tasks needed for the defined game completion criteria are `done`.

Do not mark the game complete merely because the current milestone or queue is empty. Completion requires every criterion in `PROJECT.md` to be satisfied with durable verification evidence.

## Finish

Validate GameFlow state and update `.gameflow/sessions/CURRENT.md` with tasks completed, verification results, changes, remaining ready work, blockers, decisions required, limits consumed, and the next action.

Scheduled runs should remain quiet during routine progress. Notify the user only on game completion, a blocker, a failed run, a required decision/authorization, or an inconsistent state that needs attention.
