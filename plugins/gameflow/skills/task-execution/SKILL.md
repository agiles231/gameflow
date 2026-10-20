---
name: task-execution
description: Execute one bounded GameFlow task and leave a clean, resumable checkpoint. Use when implementing gameplay, interface, art, tooling, or content work governed by a GameFlow task contract.
---

# Execute one GameFlow task

For new work confirm that the selected task is `ready`, its dependencies are `done`, and required inputs exist. Have the coordinator claim it by setting `status` to `executing` and recording ownership in the task index before making conflicting changes.

For inherited executing/verify or accepted-but-uncommitted work, recover its existing phase using [the checkpoint protocol](../task-orchestration/references/checkpoints.md); do not reset it to ready or reimplement unchanged accepted work.

Follow the project’s managed `AGENTS.md` bootstrap. After selection, run `scripts/task_context.py --project PROJECT --task TASK-ID`, then read the task contract and required references. Read legacy or unparsed Context directly; do not treat the packet as readiness or authority. Use tool-discovery to select supported native CLI, MCP, or application scripting operations for the deliverable. Use desktop UI interaction only when no reliable programmable path exists.

When delegated, honor assigned paths and application leases, return proposed shared-state changes to the coordinator, and never stage or commit. Request a resource lease before an application mutation; do independent preparation while it is unavailable. Keep changes within the contract. Create a child task for discovered work outside scope. Preserve user-authored and unrelated changes.

At the checkpoint, return evidence to the coordinator to update the contract's completion evidence with changed artifacts, commands or application actions, versions where relevant, and known risks. If implementation is complete, move the task to `verify`, clear inactive transient ownership while retaining durable checkpoint provenance, and update the session handoff. Do not self-certify it as `done`. If blocked, record the exact unmet input or decision and the safe partial state.


Route engine implementation/integration to unreal-development, noncreative asset integration or explicit simple shapes to blender-production, all complex mesh generation through Meshy MCP to asset-generation, and build/test/performance/package tasks to build-delivery. Use the existing asset-pipeline for cross-tool provenance. Load only references relevant to the task. For UI and audio, define observable interaction/playback criteria and use the engine integration references; never claim quality from file existence alone.

Record preexisting dirty files and affected source identities before work. Keep checkpoints at recoverable source/export/import boundaries. A failed tool call may have partially applied changes: inspect resulting state before retrying. Do not claim completion from a successful tool response without checking the resulting artifact.

All rigging and animation work is deferred. Do not execute or reactivate deferred tasks automatically. Future providers stay inactive. For Meshy deliveries, use cheap independent delivery checks only unless deeper review is explicitly requested; this does not reduce gameplay/build testing.

Before every exit, the coordinator records the versioned checkpoint, including authorized scope, artifact identities, jobs, repair counts and next action. This applies even to incomplete or uncommitted work. Git cleanliness does not establish acceptance.
