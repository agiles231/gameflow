<!-- gameflow:start -->
## GameFlow

This project uses `.gameflow/` as durable production state. At the start of a session, read:

1. `.gameflow/PROJECT.md`
2. `.gameflow/CONSTRAINTS.md`
3. `.gameflow/sessions/CURRENT.md`
4. `.gameflow/tasks/index.json`

Load only context named by the selected task. Treat screenshots in `.gameflow/verification/temporary/` as disposable observations. Do not mark implementation `done`; move it to `verify` until acceptance is independently checked. Before stopping, update the task contract, task index, durable evidence or decisions, and current handoff.
<!-- gameflow:end -->
