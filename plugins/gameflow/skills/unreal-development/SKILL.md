---
name: unreal-development
description: Implement and inspect Unreal gameplay, levels, delivered static assets, materials, and audio through connected MCP tools and native project builds within a GameFlow task.
---

# Develop in Unreal

Use the selected task contract and its named context. Follow repository constraints, including C++-only gameplay when required; an available Blueprint tool does not override that constraint. Material assets are not permission to introduce gameplay Blueprints. All rigging and animation production/integration is deferred; preserve existing artifacts and do not create or repair them.

## Establish the execution target

Discover connected Unreal tools and inspect their actual schemas. Use read-only queries to establish engine version, project path, current map, dirty packages, and editor/play state where supported. Cross-check the reported `.uproject` against the task's repository. If identity cannot be established, do source-only work and record why editor mutations are blocked. A registered server is not proof of a connected editor.

Resolve Windows editor paths separately from WSL shell paths. For example, `/mnt/c/...` may map to `C:\...`, but confirm the mount and query the application before relying on it. Unreal object/package paths such as `/Game/...` are neither filesystem path format. Do not submit WSL paths to a Windows tool without evidence it accepts them.

Use discovered MCP operations for supported editor, static-asset, and test actions. Do not guess tool names or assume Python execution is exposed. If a needed action is unsupported, use the repository's native build/commandlet workflow or an available documented editor API. Record a precise capability gap if no route exists; do not install plugins or restart an editor merely to gain a tool.

## Implement and check

- Inspect the existing module, asset references, and neighboring behavior before changing gameplay. Read [gameplay-and-editor.md](references/gameplay-and-editor.md) for C++ work, levels, materials, or audio.
- For delivered static-mesh import, read [asset-import.md](references/asset-import.md). Use the asset manifest's identity and source authority.
- Serialize shared-editor and overlapping-package mutations with the coordinator. A read-only request that switches maps, selections, or playback still changes shared session state and must be coordinated.
- Save only owned changes. Do not use global save-all, delete existing packages, stop another worker's PIE session, or close an editor with unknown dirty work.
- Check the actual resulting property, asset, or runtime behavior after tool success. A successful RPC establishes delivery, not acceptance.

## Evidence and handoff

Record affected source/package identities, engine/build target, commands or tool operations, import settings, test results, and unresolved limitations in the task evidence. Preserve full diagnostics as durable artifacts when they explain failure. Move completed implementation to `verify`; independent acceptance controls `done`.

For a new integration, use [fixture-validation.md](references/fixture-validation.md) before claiming live support. Keep unavailable live checks explicitly unverified.

Before stopping, follow the [shared checkpoint protocol](../task-orchestration/references/checkpoints.md), including partial or waiting work. Preserve task change ownership, actual job IDs, artifact identities and the next action independently of worker liveness and Git commit status.
