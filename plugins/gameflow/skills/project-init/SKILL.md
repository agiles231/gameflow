---
name: project-init
description: Initialize or audit the durable GameFlow state for a game project. Use when starting GameFlow in a repository or checking that its workflow files are structurally valid.
---

# Initialize a GameFlow project

Locate this plugin's root from this skill directory, then run `scripts/init_gameflow.py` with the target project, project name, and engine. Do not overwrite existing `.gameflow/` project truth; the initializer is deliberately additive and idempotent.

After initialization, run `scripts/validate_gameflow.py`. Read the generated `PROJECT.md`, `CONSTRAINTS.md`, and initial task with the user and replace undecided values only when supported by known requirements. Do not invent creative direction.

The plugin remains installed outside the game repository. Only `.gameflow/` and the managed GameFlow block in `AGENTS.md` belong in the game repository.

For an audit request, run validation without initialization. Report structural errors separately from temporary-artifact warnings.
