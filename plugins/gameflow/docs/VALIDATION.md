# Version 0.4.0 validation

- Workflow initialization/task-allocation smoke and v1 preservation tests pass.
- Task graph tests cover deferred leaves, dependencies, parents, cycles, IDs,
  malformed inputs and path confinement (35 cases).
- Meshy config tests cover recipe selection, variables, merge precedence, snapshots,
  invalid dialects/nonfinite values, credential exclusion and deferral (17 cases).
- All 14 skill entrypoints validate and relative references resolve.
- Independent code and scenario reviews found and corrected malformed-schema,
  nonfinite-number, Blender fallback and deferred-dependency contradictions.
- No paid generation, rigging, animation or live quality audit was performed.
- Tests prove local configuration/lifecycle behavior, not provider output quality.

The previous 0.2.0 native Blender OBJ smoke test does not establish Meshy delivery
or current Unreal integration. Every future task records its own actual provider
job/download/import evidence. Runtime gameplay/build checks remain separate.

## Checkpoint and optional review regression coverage

- Isolated Git fixtures exercise unchanged checkpoint recovery, preserved user
  files, failed/pending commit recovery, changed acceptance identities and
  historical committed checkpoints.
- Optional-review fixtures exercise the newest-five window, retained history,
  idempotent delivery, explicit decisions, replacement revisions, stale feedback,
  exact presented selections and deferred presentation without task mutation.
- Project validation accepts legacy state without these additive records and
  checks checkpoint/review structures when present.
- Skills and relative references are checked with the skill-creator validator.

These checks do not launch Blender or demonstrate a live five-asset review scene.
Presentation uses discovered application tools at delivery time and records the
actual result; unavailable or user-owned Blender is a deferred presentation,
not an acceptance failure. Lifecycle preflight does not prove worker liveness,
user authority or ownership of shared-file edits; the coordinator reconciles them.
