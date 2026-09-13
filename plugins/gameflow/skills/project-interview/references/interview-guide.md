# GameFlow project interview guide

Use this as a decision map, not a fixed questionnaire. Ask only questions whose answers could change direction, scope, architecture, acceptance criteria, or the first vertical slice.

## 1. Intent and player experience

Establish the premise, player fantasy and emotional arc, intended player and play context, pillars and non-goals, and comparable works—including what to borrow and avoid. Write accepted conclusions to `PROJECT.md`; record choices between credible alternatives in `DECISIONS.md`.

Checkpoint: a contributor can describe the intended feeling and reject an attractive idea that does not belong.

## 2. Gameplay

Establish the core loop, player verbs and meaningful decisions, challenge and recovery, mastery and progression, session structure and pacing, player count, and minimum mechanics needed to prove the premise. Write accepted conclusions to `GAMEPLAY.md`.

Checkpoint: the loop is observable player action and feedback, not aspiration.

## 3. Art and audio direction

Establish visual thesis, shape language, proportions, value, palette, materials, camera/composition, motion/effects/animation language, audio's role, motifs, references, and anti-references. Write accepted conclusions to `ART_DIRECTION.md`. Register durable references in `assets/manifest.json`; transient search or comparison images are not project truth.

Checkpoint: an asset brief can make inclusion and exclusion decisions without relying only on adjectives.

## 4. Interface and accessibility

Establish information hierarchy, inputs, interaction conventions, presentation density, state feedback, accessibility and remapping, and flows required by the first slice. Write accepted conclusions to `INTERFACE.md`.

Checkpoint: the slice can be played and evaluated without unexplained debug-only controls.

## 5. Production and technical boundaries

Establish application versions, target platforms, performance budgets, team/schedule/budget/licensing/source-control constraints, major system requirements, ownership, naming, scale, axes, pivots, import conventions, and deterministic automation versus justified UI-only operations.

Write hard limits to `CONSTRAINTS.md` and implementation structure to `ARCHITECTURE.md`.

Checkpoint: the first slice can be scoped without unknown platform, pipeline, or staffing assumptions.

## 6. First vertical slice

Define the smallest end-to-end experience that proves the riskiest combination of gameplay, art direction, and interface. Establish its playable entry and exit, required actions and feedback, representative content, technical proof, exclusions, placeholders, objective exit criteria, and review method.

Update `PROJECT.md` milestone criteria and `TASK-0001.md`, then use task orchestration to create the child graph.

Checkpoint: a reviewer can run one demonstration and decide pass or fail from written criteria.

## Handling uncertainty

- **Experiment:** a time-bounded task whose output enables a decision.
- **Assumption:** record impact and a review trigger.
- **Blocker:** name the missing input and block the affected task.
- **Deferred:** record why it is outside the milestone.

Do not force a premature answer when a cheap experiment would produce better evidence.

## Resume marker

In `sessions/CURRENT.md`, record the last accepted phase, current unresolved questions, contradictions, next recommended question or decision, and files updated at the checkpoint.
