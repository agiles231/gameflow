---
name: task-orchestration
description: Decompose, select, assign, and track bounded GameFlow tasks. Use for planning milestones, coordinating workers, or deciding whether a task is ready, blocked, or complete.
---

# Orchestrate GameFlow tasks

Treat `.gameflow/tasks/index.json` as the canonical graph. Keep task contracts in `.gameflow/tasks/TASK-*.md`. Use `scripts/new_task.py` to allocate stable task IDs and the shared contract format. Keep required context in the Markdown contract as project-relative links under `## Context` → `### Required`; optional fragments identify Markdown headings. Keep descriptive exclusions under `### Excluded`. Specify observable acceptance, verification methods and expected evidence before readiness; record checked artifact identities in completion evidence.

A task is sufficiently bounded when it has one principal durable deliverable, existing inputs, explicit dependencies, observable acceptance criteria, a clean checkpoint, and a failure mode that yields a useful report. Split work that crosses ownership boundaries, combines creative decisions with implementation, or cannot be verified independently.

Use lifecycle states exactly: `planned`, `ready`, `executing`, `verify`, `done`, `blocked`, `deferred`. Implementation ends at `verify`. Only an acceptance pass moves work to `done`. Follow [the checkpoint protocol](references/checkpoints.md) for durable ownership, ordered recovery, acceptance revisions, amendments and commit state. This protocol also governs checkpoints returned by production/configuration skills; clearing an active worker never discards change provenance.

After selection, use `scripts/task_context.py --project PROJECT --task TASK-ID` to identify references, then read the contract and any legacy or unparsed Context directly. Give a worker the task contract, the minimum required project constraints, and the files named by `Context`. Use `fork_turns="none"` for fresh workers when supported, supplying context explicitly rather than inheriting conversation history. Include relevant user decisions and authority verbatim or by durable reference; do not reduce model quality or omit constraints. Reuse a worker only while its task context remains relevant. Require a return packet containing changed artifacts, commands/actions taken, acceptance evidence, residual risks, and proposed child tasks.

Prevent concurrent ownership of the same files or engine assets. Unexpected scope becomes a child task; it does not silently enlarge the active task. Stop for user direction when an unknown creative or product choice would materially alter the result.

## Codex workers and shared applications

When delegation is available and authorized, use bounded subagents for all runnable independent tasks and a distinct verifier. Autopilot authorizes this delegation by default; honor explicit user/project restrictions. Follow [concurrent scheduling](references/concurrent-scheduling.md) to refill available slots, reserve task-cycle capacity, and reconcile independent results without a batch barrier. Respect the runtime's concurrency limit; do not assume a fixed agent count. The coordinator alone allocates task IDs and writes the canonical index, asset manifest, shared policy, and current handoff. Workers return proposed state changes. Never run new_task.py concurrently.

Before dispatch, record the worker/session identifier in owner, its task, assigned files/assets, application ownership, and checkpoint in the contract. Ownership is not a process lock: one coordinator may orchestrate a project at a time. If another coordinator is active, do not write shared state. A stale owner requires checking whether the worker/job is still live and reconciling artifacts before reassignment.

Parallelize disjoint source work or read-only reviews. The coordinator alone stages and commits; workers never mutate the Git index, commit, or push. Serialize writes to a shared Unreal/Blender instance even when asset names differ: selection, active file, PIE, and save state are shared. Separate worktrees do not isolate an editor. Give each verifier immutable artifact hashes/revisions and acceptance criteria; a changed artifact invalidates the corresponding result.

Worker packets include task ID, role, required context, inputs and hashes, assigned outputs, acceptance criteria, authority, application ownership, and stopping limits. Return task ID, worker/session ID, changes, checks, artifacts/hashes, unresolved jobs, blockers, and next action. Record concise durable results, not transcripts. Stable IDs and ownership support later UI consumption; do not create a second task database.

Without delegation, implement sequentially and leave work at verify for a separate verifier session. Do not describe a second self-review as independent verification.

## Deferred work

Use `deferred` for deliberately postponed work, including all rigging and animation production. Record the reason and explicit reactivation condition in its contract; clear active ownership only after reconciling running work. Deferred is not done. Deferred tasks must be leaves in the dependency graph: no task may depend on them. Before deferring, explicitly rescope affected active contracts and remove their dependence on deferred work; preserve the rationale in durable state. Combine rigging and animation into one deferred task per asset depending on its delivered static mesh. Skip deferred tasks during selection. A new provider/tool or session never reactivates it. Only explicit user direction satisfying the reactivation condition permits return to `planned`, followed by normal prerequisite checks. Do not delete historical artifacts or silently rewrite accepted evidence.
