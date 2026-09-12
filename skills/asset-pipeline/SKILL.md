---
name: asset-pipeline
description: Plan and execute traceable game-asset workflows across source tools and the engine using GameFlow asset specifications, provenance, import rules, and independent verification.
---

# Run a GameFlow asset pipeline

Every asset needs a stable ID in `.gameflow/assets/manifest.json`, a source-of-truth file, intended engine destination, provenance/license, tool and version, dependencies, and technical plus artistic acceptance criteria. Store substantial briefs in `.gameflow/assets/specifications/` and references in `.gameflow/assets/references/`.

Split production at recoverable boundaries such as specification, source creation, topology, UVs, materials/textures, rigging, animation, export, engine import, and verification. Combine stages only when one worker can finish them at a clean checkpoint and verify each output.

Record coordinate system, units, transforms, pivot, naming, material slots, texture channels, collision, skeleton, animation ranges, LODs, and export settings wherever applicable. Do not allow filenames to become the sole asset identity.

Prefer Blender Python, Unreal Python/commandlets/editor scripting, GIMP batch procedures, or other deterministic application APIs. Use UI control for unsupported operations and capture the smallest possible verification set. Update the manifest at each durable boundary; never represent a temporary render or screenshot as the source asset.

Use the shared task lifecycle. Import completion moves to `verify`; technical and art-direction checks determine `done`.
