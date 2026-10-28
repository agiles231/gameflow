---
name: autopilot-unbounded
description: Advance a GameFlow task graph until no authorized work remains, without default task, elapsed-time, or repair-count caps. Use when the user requests unbounded autopilot or continuing until the graph is exhausted; ordinary bounded runs use autopilot.
---

# Run GameFlow until the graph is exhausted

Read and follow [autopilot](../autopilot/SKILL.md) for startup, checkpoint recovery, concurrent scheduling, independent verification, serialized commits, blocker resolution, production policies, and final delivery. Apply the following overrides to its run limits and stopping rules, including where those rules appear in its linked protocols. This skill authorizes the same task delegation and project-local actions as autopilot; its broader run duration does not expand project scope or external permissions.

## Effective run policy

- No default maximum completed task cycles or elapsed time. Keep admitting eligible tasks as slots become available, including newly unblocked dependencies and necessary child tasks within the approved scope. Track selected tasks and ownership, but do not impose the bounded skill's task-cycle reservation cap.
- No default numeric repair cap. Continue evidence-driven repairs under the progress rule below. The bounded default of one repair per failed criterion does not apply.
- The template's limits explicitly scoped to `$gameflow:autopilot` apply only to that bounded invocation. Do not import its three-cycle, 90-minute, or one-repair defaults into this run. Preserve `.gameflow/AUTOPILOT.md`; do not rewrite policy to enable this mode.
- Honor user-specified limits and authored project-wide or unbounded-mode limits, including task-specific repair restrictions. Treat authored limits whose scope is unclear as applicable until clarified. Record the effective policy and its sources in `.gameflow/sessions/CURRENT.md` before dispatch.
- Keep runtime worker caps, scheduled overlap deadlines, provider allowances, explicit stop/no-contact policies, and spending authorization. Unbounded does not grant unlimited paid retries. Check applicable deadlines between operations and leave time to checkpoint.

Selecting this mode supplies additional repair authority beyond the bounded skill's default allowance, including on a recovered task whose default allowance was consumed. Record that authority without resetting historical repair counts. It does not override an explicit task or project restriction.

## Repair while making progress

For each failed criterion, retain the failure evidence, cumulative attempts, changed hypothesis, and next check. A further repair must address a newly understood cause, test a materially different plausible approach, or build on measurable improvement. Independently verify every repaired revision before accepting it.

Do not repeat the same ineffective action or spin on unchanged evidence. When there is no concrete useful next approach, diagnose the missing prerequisite and use the shared blocker-resolution protocol to obtain the specific input needed. Keep disjoint authorized work moving. Do not evade a restriction by resetting counts, changing workers, or creating a child task. Broader repair authority does not authorize creative provider variants or deferred production.

## Exhaust the available graph

After each result and reconciled commit, refill available slots. On an empty ready queue, inspect the entire in-scope task graph: recover selected phases, promote planned tasks with satisfied inputs, trace unmet dependencies to actionable prerequisites, and resolve recoverable blockers. Reconcile known workers and provider jobs; an outstanding job or verification phase is not graph exhaustion. Poll with bounded waits and persist job identities rather than resubmitting.

Continue until there are no runnable phases, eligible tasks, or useful authorized recovery actions left. Do not stop at a milestone boundary, arbitrary task count, or elapsed time when more approved work is available. Do not invent additional scope merely to keep running. Interactive tasks still require user direction; deferred tasks still require explicit reactivation.

If user input is the only remaining prerequisite, prepare the concrete review or decision and keep the question pending under the inherited interactive protocol. If the interface requires yielding, leave a resumable checkpoint and the precise question. Stop on explicit user stop, applicable hard limits, or global state/authority failures according to the inherited protocol. No automatic restart or background continuation is implied.

## Finish honestly

Use autopilot's Finish procedure, including safe worker/job parking, validation, bookkeeping, and its conditional single upstream push. Never drop unfinished selections to qualify for delivery. Report graph exhaustion separately from game completion: list completed work, remaining blocked/interactive/deferred work, pending jobs or verification, cumulative repairs, and the next required action. Claim game completion only when every project completion criterion has durable verification evidence.

This mode is additive: the existing `autopilot` name, defaults, policy inputs, CLI, task contracts, and persisted formats remain unchanged. Existing projects need no migration and acquire no new policy file.
