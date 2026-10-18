---
name: asset-generation
description: Generate complex game meshes exclusively through connected Meshy MCP tools using project defaults, task overrides, durable jobs, and independent delivery verification.
---

# Generate meshes through Meshy

Use the selected task and stable asset ID. All complex mesh creation goes through Meshy MCP. Only explicitly identified simple shapes may be authored locally. Do not replace unavailable Meshy with Blender modeling, procedural scripts, direct provider HTTP calls, UI generation, or another provider. Preserve existing assets; this rule does not require regenerating them.

Read `.gameflow/tools/meshy.json` through the meshy-config skill. Resolve project defaults, then the selected recipe (prompt template/settings), then explicit task overrides; record the effective settings. Use meshy-config to select an explicit recipe or resolve declared criteria matches by priority; ties require clarification. Do not invent a match or reset project defaults per task. Configuration is nonsecret; credentials stay in MCP configuration/environment. Inspect actual Meshy tool schemas before submitting and omit unsupported fields only when that preserves the requested result; otherwise report the incompatible setting. Never invent tool names or available features.

Rigging and animation production are deferred throughout the workflow, including provider requests and engine integration. Connected future providers such as Higgsfield remain inactive until the user explicitly revises policy. Discovery alone never activates a provider.

Follow [provider-runs.md](references/provider-runs.md) for bounded, resumable submissions and allowance handling. Preserve original downloads, request/job IDs, effective settings, provider/model version where exposed, input provenance, and output identities. Do not record credentials or signed download URLs. Resume known jobs instead of resubmitting.

Use Blender only for noncreative import/export, orientation/scale/pivot adjustment, material hookup and other integration necessities. Do not sculpt, remodel, retopologize, repaint, redesign materials, rig, or animate generated output. Failed delivery may justify a bounded technical retry; creative regeneration or additional variants need explicit direction and allowance.

Acceptance is an independent cheap delivery check: job completed, expected files downloaded and readable, required dependencies present, intended engine import/loading succeeds, and artifact identity/provenance is recorded. Do not add artistic judging, anatomy reviews, topology audits, numerical quality sweeps, render batches, or repeated generation to improve taste unless explicitly requested. Ordinary gameplay/build tests remain required for their own tasks. Leave implementation at `verify` until independent acceptance.

For existing audio integration, use [audio-integration.md](references/audio-integration.md); Meshy is not an audio provider.

Before stopping, follow the [shared checkpoint protocol](../task-orchestration/references/checkpoints.md), including partial or waiting work. Preserve task change ownership, actual job IDs, artifact identities and the next action independently of worker liveness and Git commit status.
