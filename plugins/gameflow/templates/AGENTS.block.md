<!-- gameflow:start -->
## GameFlow

This project uses `.gameflow/` as durable production state. At the start of a session, read:

1. `.gameflow/PROJECT.md`
2. `.gameflow/CONSTRAINTS.md`
3. `.gameflow/sessions/CURRENT.md`
4. The compact task view from the GameFlow plugin’s `scripts/resume_view.py --project PROJECT` (or `.gameflow/tasks/index.json` if the helper is unavailable). The helper validates the entire graph before filtering; resolve errors before work. Read each selected/recovery task’s full record with `--task TASK-ID` and its contract.

Load only context named by the selected task. Treat screenshots in `.gameflow/verification/temporary/` as disposable observations. Do not mark implementation `done`; move it to `verify` until acceptance is independently checked. Before stopping, update the task contract, task index, durable evidence or decisions, and current handoff.
<!-- gameflow:end -->
