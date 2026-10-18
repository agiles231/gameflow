---
name: asset-pipeline
description: Track source assets, Meshy deliveries, integration artifacts, and independent acceptance through GameFlow asset manifests and bounded task contracts.
---

# Run a GameFlow asset pipeline

Use stable asset IDs in `.gameflow/assets/manifest.json`. Preserve source authority, intended engine destination, provenance/license, tool version, dependencies and delivery criteria. Keep substantial briefs in `assets/specifications/` and durable references in `assets/references/`; screenshots are not source authority.

Route every complex mesh creation through asset-generation and Meshy MCP. Explicit simple-shape exceptions may use local primitives. Existing assets may be integrated without regeneration. Meshy unavailable, unsupported, or out of allowance means the affected generation task is blocked, never a local modeling fallback. Future providers remain inactive until explicit policy changes.

Split work at recoverable generation, download, integration/export, engine-import, and independent-delivery-verification boundaries. Blender performs only noncreative integration, not creative repair. All rigging and animation production is deferred, including work offered by a currently connected provider. Keep such tasks visible as `deferred`, with reason and reactivation condition.

Record applicable units, axes, pivot, material/texture dependencies, format and import/export settings. Preserve generated originals and bind derived artifacts to them. Source replacement invalidates acceptance tied to earlier identities. Use blender-production and unreal-development only for permitted integration.

For Meshy outputs, verify cheap delivery checks independently: completed job, readable expected files, dependencies, intended import/loading, and recorded identity/provenance. Do not introduce artistic or numerical quality audits unless explicitly requested. Gameplay/build tasks retain their own tests. Implementation ends at `verify`, not `done`.

Keep existing manifest fields. Optional generation evidence includes provider/model, job ID, effective config/recipe/task overrides, input references, output hashes, allowance reservation and usage, and rights evidence. Unknown rights stay unknown. Never store secrets or authenticated URLs.

## Optional manual review

After independent acceptance, enqueue each delivered asset revision and present the newest five unreviewed assets in a dedicated Blender scene. Read [optional-review.md](references/optional-review.md) for durable queue commands, safe presentation, migration, and feedback handling. Manual approval is optional and never gates production; explicit disapproval reopens the original task for interactive revision while preserving its accepted predecessor.

Preserve task ownership and resumable exit state using the shared [checkpoint lifecycle](../task-orchestration/references/checkpoints.md); optional review state is checkpoint evidence, not an acceptance gate.
