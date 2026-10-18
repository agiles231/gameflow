---
name: tool-discovery
description: Discover and validate GameFlow production tools, connected MCP applications, and cross-host paths before application work or after a connection change. Use for Unreal, Blender, or Meshy MCP readiness.
---

# Establish production capabilities

Read the selected task and project constraints. Discover exposed tools in the current Codex session; installed configuration or a previous handoff is not proof that a tool is callable. Keep discovery scoped to the task. Do not print credentials or connection secrets.

For Unreal, list available toolsets, then describe only relevant toolsets and use their actual input schemas. For Blender, inspect file path/save state and relevant scene metadata using dedicated tools first. Read bundled API documentation when scripting is necessary. For Meshy, distinguish a missing capability from a reachable server, authentication failure, quota failure, and a failed job.

Before mutations, establish the connected project/file identity, app version, dirty state, and whether another worker owns the application. If a server cannot expose identity, establish it through a supported read-only application API or launch configuration; otherwise block mutations. An unsaved Blender scene is not an empty disposable scene: inspect its contents and preserve it. Never switch files, stop another worker's play session, or save all packages merely to simplify setup.

Resolve paths on the host that executes the action. For WSL controlling Windows apps, retain both the WSL filesystem path and verified Windows path. Check a known file through both hosts; path-string conversion alone does not establish access. Unreal /Game package paths are not filesystem paths. Do not hard-code drive letters, executable versions, server names, tool signatures, or ports from another project.

Choose the supported operation best suited to the deliverable: native CLI for compilation/builds, connected MCP for supported application inspection and edits, application scripting for gaps, UI only where no reliable programmable route exists. All complex meshes use Meshy MCP through asset-generation; config is `.gameflow/tools/meshy.json` via meshy-config. Blender is limited to noncreative integration and explicit simple shapes. Do not use native scripts, HTTP or UI to bypass a missing Meshy capability. Rigging/animation are deferred. Future providers may be recorded as observed but never autoactivated. Verify Meshy delivery cheaply and independently; broader checks require explicit scope.

Record only useful observed capabilities in `.gameflow/tools/capabilities.json` and applications in `applications.json`, preserving unrelated entries and schema_version. Existing files remain valid. Optional capability entries may record operation, tool/server identity, observed_at, status, limitations, and application identity. Never record a speculative capability as available. These records are observations, not authorization or runtime configuration; refresh before relevant mutations and after reconnects.

If a required capability is absent, record the specific blocker and continue independent work. For non-generation work, a known viable alternate must satisfy both the contract and production policy. No complex-mesh generation fallback is allowed. Do not silently lower acceptance criteria, install servers, alter MCP configuration, or start billable jobs as a discovery probe.
