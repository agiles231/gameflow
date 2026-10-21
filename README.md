# GameFlow marketplace

GameFlow is a Codex plugin for durable game planning, Meshy-led static asset
production, Unreal integration, and bounded autonomous work. Version 0.8.0
contains 14 skills. Plugin code stays outside game repositories; project state
lives in .gameflow with a small AGENTS.md entrypoint.

Repository changes follow [AGENTS.md](AGENTS.md): every compatibility-breaking
change must ship a migration script, recovery documentation and migration tests.

## Version 0.8.0: fixed optional prompt clauses

Meshy recipes can declare literal optional clauses with explicit boolean defaults
and on/off overrides. This avoids unconstrained wording and duplicate recipes.
Both enabled and omitted forms preserve exact whitespace and punctuation. Existing
version-1 configs and string-variable behavior remain supported unchanged; only
configs using the new field require the updated plugin. See the
[configuration reference](plugins/gameflow/skills/meshy-config/references/config-format.md).

## Install in Codex CLI

Run in the host environment where Codex CLI runs (CLI 0.163.0 inspected):

```sh
codex plugin marketplace add /mnt/c/workspace/gameflow
codex plugin add gameflow@gameflow-local
```

Native Windows users supply C:\workspace\gameflow instead. To refresh an
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
selecting new work. It fills available worker slots with independent eligible tasks,
refills them as results arrive, and reserves task-cycle capacity across active work.
Pending provider jobs can overlap without occupying idle agents. Dependencies wait
for accepted, committed prerequisites; coordinator-only Git commits remain serialized.
Recorded task ownership and artifact identities distinguish
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
python3 tests/test_task_context.py
python3 tests/test_migration.py
```

See [workflow](plugins/gameflow/docs/WORKFLOW.md),
[GameFlow glossary](plugins/gameflow/docs/GLOSSARY.md), and
[validation coverage](plugins/gameflow/docs/VALIDATION.md). No live paid generation
is required by tests, installation, or configuration.

## Version 0.6.0: context and upgrades

Task context stays in Markdown contracts. The new `scripts/task_context.py`
command returns compact references and recovery information, with direct-reading
fallback for legacy prose. New tasks share one contract template; handoffs contain
current state instead of duplicated resume procedures.

Existing schema-v1 projects remain usable without migration. Refresh the plugin,
start a fresh session, and follow the [explicit migration guide](plugins/gameflow/docs/MIGRATION.md)
to preview and apply managed guidance updates. Migration preserves authored state
and reports remaining manual reconciliation. No automatic resume-time upgrade,
agent benchmark, or token-savings claim is included.

## Version 0.7.0: planning and retention

Milestones, epics and experiments are now supported by the plugin. Fresh projects
receive empty planning definitions, generated navigation and local-only output
policies; legacy projects remain valid without migration. Task creation supports
`--epic` and `--kind experiment`. Native validation checks optional metadata.
See [planning](plugins/gameflow/docs/PLANNING.md),
[retention](plugins/gameflow/docs/ARTIFACT_RETENTION.md), and the
[upgrade guide](plugins/gameflow/docs/MIGRATION.md).

Run `python3 tests/test_planning.py` and `python3 tests/test_retention.py` from
plugins/gameflow in addition to the existing suite. No project-specific assets,
acceptance decisions or history removal lists are included.
