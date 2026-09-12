# Decisions

Append decisions. Do not rewrite history; supersede an earlier decision with a new entry.

## DEC-0001 — Adopt GameFlow

- Date: {{DATE}}
- Status: accepted
- Context: The project requires resumable, bounded agent workflows.
- Decision: Project state and task progress are stored under `.gameflow/`.
- Consequences: Sessions are disposable; state changes must be recorded before stopping.
