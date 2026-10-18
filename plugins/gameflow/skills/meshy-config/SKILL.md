---
name: meshy-config
description: Create, inspect, or update project-local Meshy prompt recipes and operation settings, and dry-run their deterministic resolution against captured MCP schemas. Use for Meshy configuration requests; this skill never submits generation jobs.
---

# Configure Meshy recipes

Use `.gameflow/tools/meshy.json` as the project-local configuration. Read the selected task, relevant art/technical brief, existing configuration, and the provider allowance section in `.gameflow/AUTOPILOT.md`. Preserve unrelated recipes and user values. Adding configuration does not authorize spending or uploads.

Discover the currently connected Meshy MCP tools and inspect their real input schemas. All Meshy operations use MCP; do not configure direct HTTP calls, credentials, API keys, account changes, or imagined tool arguments. Read [references/config-format.md](references/config-format.md) for the version 1 format and resolver contract.

Start with the shipped empty `draft` configuration when no recipes exist. Infer no model, quality tier, parameter name, or provider default. Capture the exact callable tool name, schema, capture timestamp, and explicit prompt field for each configured operation. Expand schema references locally before storing; the offline validator deliberately rejects references rather than retrieving remote resources. If discovery is unavailable, retain the draft and record what is missing. Configured snapshots are evidence of a past interface, not proof of current availability.

Create named recipes from the approved brief: declared prompt variables, human-readable selection criteria, integer priority, operation settings, and optional category/tags. Ask only about material missing creative choices. Avoid overfitting a universal recipe to one task. Keep all rigging and animation deferred under current policy, including simple assets and local Blender work, even if connected tools expose those capabilities. Record these as deferred leaves; executable tasks must not depend on them.

Run the helper using its installed plugin location:

```bash
python3 <plugin>/scripts/meshy_config.py validate .gameflow/tools/meshy.json
python3 <plugin>/scripts/meshy_config.py resolve .gameflow/tools/meshy.json --operation OPERATION --template RECIPE --variables '{"subject":"approved subject"}'
```

The helper requires `jsonschema>=4,<5` for configured snapshots, declared in `<plugin>/scripts/requirements.txt`. Use the existing environment or install that requirements file into the project's chosen Python environment when dependency installation is authorized; do not silently modify a system Python installation. Empty draft validation needs only the standard library.

For automatic selection, evaluate each candidate's human-readable criteria against the task and pass the matching IDs as repeated `--match ID` arguments. Record that reasoning in task evidence. The helper does not interpret prose. Highest priority wins; ties require explicit selection or a configuration correction. A user-requested named recipe uses `--template ID`. Render with declared `--variables` and explicit task setting `--overrides`; report the selected recipe and effective arguments for review.

The helper only validates and prints JSON; it does not write configuration, call MCP, reserve budget, or submit jobs. Save reviewed configuration changes through normal file edits. Validate with a representative local dry-run; leave unmatched, missing-variable, invalid-setting, or unavailable-tool cases as explicit errors. Before a downstream generation submission, rediscover and validate the resolved arguments against the **current** MCP schema and follow `asset-generation` allowance/reservation rules. Cached validation never bypasses those checks.

Record configuration changes, schema source/time, dry-run result, and remaining live-integration gaps in task evidence and the current handoff. Implementation goes to `verify`; independent acceptance establishes `done`.

Before stopping, follow the [shared checkpoint protocol](../task-orchestration/references/checkpoints.md), including partial or waiting work. Preserve task change ownership, actual job IDs, artifact identities and the next action independently of worker liveness and Git commit status.
