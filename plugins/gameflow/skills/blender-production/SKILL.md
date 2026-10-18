---
name: blender-production
description: Integrate existing or Meshy-delivered meshes in Blender with noncreative transforms, material hookups, source preservation, and export; create only explicitly allowed simple shapes.
---

# Integrate assets in Blender

Use the selected task and asset ID. Blender is an integration tool in this workflow, not a substitute creative mesh generator. All complex mesh creation uses Meshy MCP through asset-generation. Local creation is limited to explicitly designated simple shapes. Do not sculpt, remodel, retopologize, repaint, redesign materials, or creatively repair generated meshes. All rigging and animation work is deferred; see [rigging-and-animation.md](references/rigging-and-animation.md).

Discover actual connected MCP schemas. Establish Blender version, active file, scene identity, dirty state, and application ownership before edits. Preserve unrelated open work. Resolve Windows/WSL paths through the actual hosts rather than string conversion alone. Use available scripting only for permitted integration operations, never as a Meshy bypass.

Coordinate exclusive mutation access, save a task-owned working copy, and preserve accepted sources and original provider downloads. Use named collections/objects and inspect partial results before retries. Do not clear scenes, globally apply transforms, or overwrite unknown work.

Read [mesh-and-materials.md](references/mesh-and-materials.md) for allowed transforms/material hookups and the simple-shape boundary. Read [export-and-fixtures.md](references/export-and-fixtures.md) for delivery and isolated fixtures. Preserve dependencies needed to reopen the integration file and record original-to-derived artifact identities.

Check only the cheap delivery conditions needed to establish readable output and intended import. Do not conduct artistic reviews, anatomy assessments, numerical quality sweeps, render batches or repair loops unless the user explicitly requests that expanded work. Return evidence to the coordinator and leave implementation at `verify` for a distinct verifier.

## Optional review scene

For completed asset deliveries, follow [optional-review.md](../asset-pipeline/references/optional-review.md) to present the newest five revisions awaiting optional review. Use a dedicated scene with labeled review copies and usable framing/materials. Preserve delivered artifacts and the user's active Blender session; defer the refresh when ownership is unavailable. Report actual shown/deferred status to the coordinator. User inspection is optional and adds no artistic verification or approval gate.

Preserve task ownership and resumable exit state using the shared [checkpoint lifecycle](../task-orchestration/references/checkpoints.md); optional review state is checkpoint evidence, not an acceptance gate.
