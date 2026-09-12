---
name: task-orchestration
description: Decompose, select, assign, and track bounded GameFlow tasks. Use for planning milestones, coordinating workers, or deciding whether a task is ready, blocked, or complete.
---

# Orchestrate GameFlow tasks

Treat `.gameflow/tasks/index.json` as the canonical graph. Keep task contracts in `.gameflow/tasks/TASK-*.md`. Use `scripts/new_task.py` to allocate stable task IDs.

A task is sufficiently bounded when it has one principal durable deliverable, existing inputs, explicit dependencies, observable acceptance criteria, a clean checkpoint, and a failure mode that yields a useful report. Split work that crosses ownership boundaries, combines creative decisions with implementation, or cannot be verified independently.

Use lifecycle states exactly: `planned`, `ready`, `executing`, `verify`, `done`, `blocked`. Implementation ends at `verify`. Only an acceptance pass moves work to `done`.

Give a worker the task contract, the minimum required project constraints, and the files named by `Context`. Avoid sending the whole project history. Require a return packet containing changed artifacts, commands/actions taken, acceptance evidence, residual risks, and proposed child tasks.

Prevent concurrent ownership of the same files or engine assets. Unexpected scope becomes a child task; it does not silently enlarge the active task. Stop for user direction when an unknown creative or product choice would materially alter the result.
