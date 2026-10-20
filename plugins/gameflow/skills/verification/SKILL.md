---
name: verification
description: Independently verify a GameFlow task or game artifact against explicit acceptance criteria while keeping screenshots and intermediate renders out of durable context.
---

# Verify GameFlow work

Verify observable output against every acceptance criterion. Do not accept the implementation report as proof. Prefer automated checks and direct artifact inspection; use visual inspection only for criteria that require visual judgment.

Put screenshots, viewport captures, and intermediate renders in `.gameflow/verification/temporary/`. Inspect only the minimum views needed. Do not copy temporary image content into task contracts or session handoffs. Durable approved references and final deliverables belong in the asset manifest instead.

Write a result under `.gameflow/verification/results/` containing task ID, artifact path and revision/hash, application/tool versions, camera or viewport configuration, each check and evidence, overall result, and durable evidence paths. Then remove only captures owned by this verification attempt, leaving inherited files and `.gitignore` intact.

Return pass/fail findings to the coordinator. On a pass, the coordinator moves `verify` to `done`; on failure it records actionable findings and moves to `executing` for an allowed repair or `blocked` for missing decisions/inputs. The coordinator updates `.gameflow/sessions/CURRENT.md` and runs the project validator.


## Independent acceptance

A verifier must be a distinct subagent or separate session from the implementer. Receive the task criteria and frozen artifact identities; independently inspect outputs rather than repeating the author's conclusion. Return results to the coordinator, which alone changes shared task state. If no distinct verifier is available, leave the task at verify.

For each criterion record pass, fail, or not-tested, the observation/measurement, reproduction procedure, and exact artifact identity. Overall acceptance requires every required criterion to pass. Unavailable live tools or an unperformed packaged-play test are not passes. Rigging and animation production are deferred. Verify UI/audio through actual interaction/playback when available. Static images cannot establish timing or audible quality.

Store durable logs, measurements, and concise findings separately from disposable captures. Only remove temporary captures owned by this verification attempt after recording conclusions; preserve inherited files. On resumed verification, the independent verifier may reuse its durable passing observations only after confirming unchanged criteria, artifact/dependency hashes, provenance, and relevant application/environment versions. Cite original evidence and identity checks; unknown identity or changed context requires repeating affected checks. Author reports and stale screenshots are not reusable acceptance evidence. Required interaction, gameplay, build and package tests remain required; rerun when affected inputs/environment changed or the contract requires a fresh run. Recheck artifact identities before acceptance. Failed or changed outputs return for bounded repair or remain blocked/verify as appropriate; retain prior attempt findings and counts.

## Meshy delivery acceptance

For Meshy assets, independent acceptance is intentionally cheap: independently confirm the job completed, expected downloads are readable, required dependencies exist, intended engine import/loading succeeds, and artifact identity/provenance is recorded. Do not run artistic/anatomy/topology reviews, numerical quality sweeps, render batches, or creative repairs unless the user explicitly requested those checks. Missing delivery is a failure, not a reason for creative regeneration. Keep verification independent even for this reduced scope. Existing gameplay, UI/audio, build and package contracts retain meaningful tests. If inherited mesh criteria conflict with the approved delivery-only policy, have the coordinator record the scoped criteria change before executing; do not pretend old audits passed.

## Optional user inspection

Technical acceptance and manual review are separate. After an asset passes, the coordinator follows [optional-review.md](../asset-pipeline/references/optional-review.md) to enqueue its frozen revision and open the newest five pending assets in Blender. A deferred presentation or absent user approval does not fail verification. Do not interpret a technical pass as manual approval. Explicit user disapproval is a revision request handled by the coordinator, preserving prior evidence and returning that asset to interactive work.

Preserve task ownership and resumable exit state using the shared [checkpoint lifecycle](../task-orchestration/references/checkpoints.md); optional review state is checkpoint evidence, not an acceptance gate.

## Planning and retention

Follow [planning](../../docs/PLANNING.md) and [artifact retention](../../docs/ARTIFACT_RETENTION.md). Respect project-authored overrides. Keep detailed verification and experiment payloads local-only, with compact revision-bound conclusions in tracked contracts. Do not infer acceptance from task migration or missing local evidence.
