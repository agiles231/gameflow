---
name: project-init
description: Initialize or audit the durable GameFlow state for a game project. Use when starting GameFlow in a repository or checking that its workflow files are structurally valid.
---

# Initialize a GameFlow project

Locate this plugin's root from this skill directory, then run `scripts/init_gameflow.py` with the target project, project name, and engine. Do not overwrite existing `.gameflow/` project truth; the initializer is deliberately additive and idempotent.

After initialization, run `scripts/validate_gameflow.py`. Read the generated `PROJECT.md`, `CONSTRAINTS.md`, and initial task with the user and replace undecided values only when supported by known requirements. Do not invent creative direction.

The plugin remains installed outside the game repository. Only `.gameflow/` and the managed GameFlow block in `AGENTS.md` belong in the game repository.

For an audit request, run validation without initialization. Report structural errors separately from temporary-artifact warnings.


For CLI setup, keep plugin code outside the game, reuse configured MCP servers, and follow the repository README for host-specific install commands. Use tool-discovery when application work is selected. Existing schema-v1 projects remain valid without an upgrade; do not replace established settings. For an explicit tooling upgrade, read [migration instructions](../../docs/MIGRATION.md), preview `scripts/migrate_gameflow.py --project PROJECT`, then use `--apply` within the authorized upgrade scope. Report unresolved authored-guidance follow-ups separately. Never run migration automatically on resume.

## Planning and retention

Follow [planning](../../docs/PLANNING.md) and [artifact retention](../../docs/ARTIFACT_RETENTION.md). Respect project-authored overrides. Keep detailed verification and experiment payloads local-only, with compact revision-bound conclusions in tracked contracts. Do not infer acceptance from task migration or missing local evidence.

Fresh initialization creates empty planning definitions and local-only output ignore rules. Existing projects adopt planning through the explicit planning migration; general guidance migration does not rewrite task metadata or Git history.
