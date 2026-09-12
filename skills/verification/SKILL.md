---
name: verification
description: Independently verify a GameFlow task or game artifact against explicit acceptance criteria while keeping screenshots and intermediate renders out of durable context.
---

# Verify GameFlow work

Verify observable output against every acceptance criterion. Do not accept the implementation report as proof. Prefer automated checks and direct artifact inspection; use visual inspection only for criteria that require visual judgment.

Put screenshots, viewport captures, and intermediate renders in `.gameflow/verification/temporary/`. Inspect only the minimum views needed. Do not copy temporary image content into task contracts or session handoffs. Durable approved references and final deliverables belong in the asset manifest instead.

Write a result under `.gameflow/verification/results/` containing task ID, artifact path and revision/hash, application/tool versions, camera or viewport configuration, each check and evidence, overall result, and durable evidence paths. Then remove transient captures, leaving the directory's `.gitignore` intact.

On a pass, move the task from `verify` to `done`. On a failure, move it to `executing` with actionable findings, or to `blocked` when progress requires a missing decision/input. Update `.gameflow/sessions/CURRENT.md` and run the project validator.
