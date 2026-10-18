# GameFlow marketplace

GameFlow is a Codex plugin for durable game planning, Meshy-led static asset
production, Unreal integration, and bounded autonomous work. Version 0.5.0
contains 14 skills. Plugin code stays outside game repositories; project state
lives in .gameflow with a small AGENTS.md entrypoint.

## Install in Codex CLI

Run in the host environment where Codex CLI runs (CLI 0.163.0 inspected):

```sh
codex plugin marketplace add /mnt/c/workspace/GameWorkflow
codex plugin add gameflow@gameflow-local
```

Native Windows users supply C:\workspace\GameWorkflow instead. To refresh an
installed local plugin, remove gameflow@gameflow-local and add it again, then
start a fresh session. Existing MCP connections are reused, never reconfigured.

## Production workflow

Ask GameFlow to initialize or resume the project. Use gameflow:meshy-config to
enter the project's prompt recipes, matching criteria, explicit model/settings,
and spending allowance. Config is nonsecret JSON at .gameflow/tools/meshy.json;
credentials remain exclusively in the configured Meshy MCP. No direct API client
or background runner is included.

Meshy MCP creates complex meshes. Codex may author explicitly simple-shape assets
and perform mechanical integration. Blender is not a complex-authoring fallback.
Rigging and animation are deferred for ALL providers and local tools. Deferred
tasks are leaves and are never selected automatically. Reactivation needs explicit
user direction and a revised supported workflow.

Meshy acceptance checks job success, usable downloads, and engine import when
required, with an independent verifier. Visual/artistic and dense geometry/motion
audits are omitted unless explicitly requested. Gameplay/build tests still apply.
Optional manual review is separate from technical acceptance: completed assets
remain tracked until explicitly approved, and Blender presents the newest five
unreviewed assets when safe. Silence never blocks production; disapproval reopens
the asset task for interactive revision. A dedicated review scene preserves source
assets and user-owned editor work.

Autopilot reconciles pending checkpoints and accepted-but-uncommitted tasks before
selecting new work. Recorded task ownership and artifact identities distinguish
resumable changes from unrelated baseline edits.

One coordinator owns shared state and paid-job reservations; shared editors are
serialized. Unknown charged jobs are reconciled, never blindly resubmitted.

Recipes resolve operation defaults < selected recipe < explicit task overrides.
The helper prints a dry-run request and validates against a captured schema;
actual submission requires a callable tool and validation against its current MCP schema. Schemas inspected in the same unchanged connection may be reused; reconnects, tool changes, schema errors or uncertain freshness require rediscovery.
Install scripts/requirements.txt into the chosen Python environment for configured
schema validation. Empty draft configs need only the standard library.

Existing projects without Meshy config remain structurally valid. Complex-mesh
production waits for configuration; no model or recipe is invented. Task schema
version 1 gains the deferred state. Before deferring an existing task, remove
active dependency gates through explicit scope reconciliation; never silently
claim its former requirements are satisfied.

## Validation

From plugins/gameflow:

```sh
python3 tests/test_workflow.py
python3 tests/test_compatibility.py
python3 tests/test_task_graph.py
python3 tests/test_meshy_config.py
python3 tests/test_checkpoints.py
python3 tests/test_asset_review.py
python3 tests/test_resume_view.py
```

See [workflow](plugins/gameflow/docs/WORKFLOW.md),
[GameFlow glossary](plugins/gameflow/docs/GLOSSARY.md), and
[validation coverage](plugins/gameflow/docs/VALIDATION.md). No live paid generation
is required by tests, installation, or configuration.
