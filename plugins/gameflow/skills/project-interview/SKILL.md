---
name: project-interview
description: Interview a game creator to turn an initial concept into durable GameFlow project direction and a bounded first vertical slice. Use after GameFlow initialization, when project definition is incomplete, or when major creative direction must be clarified.
---

# Conduct a GameFlow project interview

Run a progressive, resumable interview that updates the project's existing `.gameflow/` state. Do not produce a separate design document or require the user to answer a large questionnaire at once.

Before asking questions, read `.gameflow/PROJECT.md`, `.gameflow/CONSTRAINTS.md`, `.gameflow/ART_DIRECTION.md`, `.gameflow/GAMEPLAY.md`, `.gameflow/INTERFACE.md`, `.gameflow/ARCHITECTURE.md`, `.gameflow/DECISIONS.md`, `.gameflow/sessions/CURRENT.md`, and `.gameflow/tasks/index.json`. Identify confirmed facts, tentative assumptions, contradictions, and unknowns. Preserve existing decisions unless the user explicitly changes them.

Read [references/interview-guide.md](references/interview-guide.md) for phase goals, question selection, document mapping, and completion criteria.

## Interview behavior

- Ask one to three related questions per turn. Prefer one when the answer will determine the next branch.
- Explain a tradeoff only when it helps the user make a decision.
- Offer concrete options when the user may not know the design vocabulary, while allowing their own answer.
- Ask for examples and anti-examples when adjectives such as "stylized," "immersive," or "fast" are too ambiguous to guide production.
- Separate requirements, preferences, experiments, assumptions, and unresolved questions.
- Do not invent creative direction or silently convert a suggestion into a decision.
- Revisit contradictions directly and cite the conflicting project statements.
- Skip questions already answered by durable project state.

## Checkpoints

At the end of each phase, summarize the proposed conclusions and ask the user to correct them. Once accepted, update the relevant `.gameflow/` documents and append material choices to `DECISIONS.md`. Update `.gameflow/sessions/CURRENT.md` so a new session can resume at the next unanswered phase.

Do not store the conversational transcript. Store only concise decisions, constraints, open questions, and rationale that will affect future work.

## Completion

The interview is complete when the project has a coherent vision, product pillars, target player and experience, core loop and player verbs, art and interface direction, production constraints, technical boundaries, and a demonstrable first vertical slice with explicit exclusions and exit criteria.

Use the task-orchestration workflow to split the accepted slice into bounded tasks. Each task must have one principal deliverable, explicit dependencies and context, observable acceptance criteria, and a clean stopping point. Leave tasks `planned` until their inputs exist; mark only genuinely actionable tasks `ready`.

Finish by running the GameFlow validator and giving the user a compact review of confirmed direction, unresolved risks, and the first recommended task.
