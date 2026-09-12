# GameFlow workflow

## Durable state

`AGENTS.md` is the entrypoint. It directs every new session to `.gameflow/PROJECT.md`, `.gameflow/CONSTRAINTS.md`, `.gameflow/sessions/CURRENT.md`, and `.gameflow/tasks/index.json`. The task graph and asset manifest are canonical machine-readable state. Markdown files explain intent and decisions.

Never depend on a prior conversation to resume work. Before stopping, update the active task, task index, relevant decision or verification record, and `sessions/CURRENT.md`.

## Task lifecycle

Tasks move through `planned`, `ready`, `executing`, `verify`, `done`, or `blocked`.

```text
planned -> ready -> executing -> verify -> done
                         |          |
                         +-> blocked <-+
```

A task is ready only when its dependencies and inputs exist. A task is small enough when it has one principal deliverable, can complete at a clean checkpoint, and has acceptance criteria that can be evaluated without inventing missing creative direction.

Workers do not expand scope. Unexpected work becomes a child task. Implementation workers move work to `verify`; an independent verification pass moves it to `done`.

## Context packets

Every task lists `context.required` and `context.excluded`. Load the project entrypoint plus only the required references. A worker completion report contains changed artifacts, commands, acceptance evidence, residual risks, and proposed follow-ups; it does not reproduce its full working context.

## Visual observations

Approved references and final artifacts are durable. Screenshots, viewport captures, and intermediate renders are observations. Put observations in `.gameflow/verification/temporary/`, inspect them in a narrow context, write conclusions to a result JSON file, then remove them. Never place temporary observations in task descriptions or session handoffs.

Verification results record the task, artifact hashes or revisions, application versions, view/camera configuration, checks, outcome, and durable evidence paths.

## Automation hierarchy

Prefer, in order:

1. Native project files and deterministic command-line tools.
2. Application scripting APIs (Unreal Python/commandlets, Blender Python, GIMP batch procedures).
3. Purpose-built MCP or function tools.
4. Desktop UI automation for operations without a reliable programmable interface.

UI runs must be bounded, cancellable, and verified from actual resulting state.

## Skill extensions

Add application-specific skills only after a real workflow is exercised. Each production skill should define inputs, outputs, application/version assumptions, deterministic path where available, UI fallback, acceptance checks, and recovery behavior. It should consume and update the shared task and asset contracts rather than inventing another state system.
