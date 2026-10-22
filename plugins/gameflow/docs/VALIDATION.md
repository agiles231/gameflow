# Version 0.4.0 validation

This document retains historical coverage below. Current release additions are
recorded in the versioned sections.

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

## Version 0.5.1 concurrent scheduling

- The changed autopilot, orchestration and task-execution skills pass the skill
  validator; workflow, v1 compatibility, task graph (35 cases), checkpoint and
  resume-view regression suites pass.
- Independent scenario review covers slot filling, task-cycle reservations,
  dependent-task gating, slow provider jobs, verifier independence, shared-editor
  leases and task commit isolation. It corrected reservation-cap stopping and
  worker reuse when the runtime cannot release inactive agents.
- This is an instruction-driven scheduler inside the current Codex session.
  No background runner or automated scheduler is installed. These checks do not
  establish live parallel provider/editor operation or change spending authority.

## Version 0.6.0 context and migration

- Context fixtures cover shared contract generation, compact read-only packets,
  heading references, legacy and unparsed prose, missing references, path/symlink
  escapes, recovery visibility and full-graph validation before selection.
- Migration fixtures cover read-only preview, apply/no-op behavior, malformed
  markers, byte preservation including CRLF and Unicode, backups, source changes,
  tampered backups, structural failures and hash-guarded rollback.
- Independently constructed schema-v1 fixtures retain authored Markdown, unknown
  JSON metadata, task ownership and custom binary assets across initialization
  and migration. Existing checkpoint and provider-related regression suites pass.
- Workflow, compatibility, task graph, Meshy configuration, checkpoint, asset
  review, resume view, task context and migration suites pass. Skill entrypoints
  and local Markdown references are validated separately.
- No external game project was migrated. These are ordinary regression checks;
  no agent benchmark, quality evaluation, or token-savings measurement was run.

## Version 0.7.0 planning and retention

The nine existing executable suites and two new suites pass. Planning coverage
includes preview/apply/idempotence, exact task-set checks, backups, dependency
cycles, confined output paths, preserved task lifecycle/ownership, experimental
task creation, and native validator/resume/context rejection of bad epic references.
Retention tests exercise Git ignore behavior, tracked accepted assets/conclusions,
audit output, isolated branch preparation, preserved source refs, existing-output
rejection and changed-tip rejection. Cleanup orchestration uses controlled filter
fixtures; it is not a production history rewrite or a test of git-filter-repo itself.
Lodgepole's existing planning graph passes the native validator read-only, with
existing legacy-checkpoint and temporary-output warnings. No paid jobs, live engine
edits, automatic project migrations or history rewrites are part of this release.

## Version 0.9.0 blocker resolution and user verification

All 11 executable regression suites pass. The expanded independently constructed
v1 compatibility fixture preserves explicit stop/no-contact policy, a blocked
interactive task, pending user question, consumed repair count and provider job
through repeated initialization and guidance migration. No schemas or CLI inputs
change; existing project policies remain authoritative.

Independent read-only tabletop review exercised the updated skill instructions:

| Scenario | Required behavior reviewed |
| --- | --- |
| Missing asset brief | Draft from approved direction; ask only unresolved variant/budget questions before generation. |
| Exhausted repair allowance | Diagnose existing evidence, propose changed bounded repair, request extra allowance without resetting counts. |
| Missing motion inputs | Search deliveries and request exact compatible inputs; discovery does not reactivate deferred production. |
| Scheduled deadline with live provider job | Retain job ID/reservation and pending question; checkpoint without resubmission or background claims. |
| Prior explicit targeted-repair authority | Reuse authorization overriding plugin default; no repeated permission gate. |
| Answer arrives during independent work | Record it and resume with existing resource/task/time limits. |
| Required mesh review with unsaved Blender work | Preserve session, prepare safe separate review and confirm visibility before approval. |
| Gameplay review with screenshot only | Prepare actual Unreal interaction; screenshot cannot satisfy gameplay criteria. |
| Yes arrives after artifact change | Bind to shown revision; present and verify changed candidate again. |
| No without details | Preserve rejection, ask focused criterion feedback, repair only within scope/limits. |
| Optional review unanswered | Keep optional queue pending without blocking technical acceptance. |
| Required review unanswered after technical pass | Remain at verify, hold affected dependents, continue independent work. |

The review led to explicit wording at acceptance decision points: every required
user judgment must pass before done; replacement approval is revision-specific.
These are instruction-level scenario checks, not automated agent benchmarks or
live Blender/Unreal presentation tests. Skill frontmatter and local links are
checked separately. No paid calls, game asset changes or project-policy migration
are required for this release.
