---
name: session-resume
description: Resume work in a GameFlow game project from durable state without relying on previous chat history. Use at the beginning of a new session or when asked what work should happen next.
---

# Resume a GameFlow session

Read, in order:

1. `.gameflow/PROJECT.md`
2. `.gameflow/CONSTRAINTS.md`
3. `.gameflow/sessions/CURRENT.md`
4. `.gameflow/tasks/index.json`

Run the GameFlow validator. Resolve inconsistencies before production work.

Select a `ready` task whose dependencies are all `done`. If none exists, determine whether a `planned` task has satisfied prerequisites and can become `ready`, or report the concrete blocker. Read its contract, then load only the files or sections listed under Context. Do not load temporary verification images or unrelated project history.

Before ending, update the task state and `.gameflow/sessions/CURRENT.md`. The handoff must state the active milestone, completed changes, next recommended task, exact blockers, verification status, and any uncommitted or externally held state needed to resume.
