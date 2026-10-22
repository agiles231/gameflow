# Autopilot policy

These limits apply to one `$gameflow:autopilot` invocation. Adjust them for the project's build times and risk profile.

## Run limits

- Maximum elapsed time: 90 minutes
- Maximum completed task cycles: 3
- Maximum repair attempts per failed acceptance criterion: 1
- Stop at least 15 minutes before the next scheduled run

## Allowed unattended work

- Project-local source, content, configuration, build, and test changes
- Application scripting and bounded UI automation needed by a ready task
- Creation of bounded child tasks discovered during implementation
- Task, asset, decision, verification, and session-state updates

## Obtain human input before the affected action

- A missing creative or product decision that materially changes the result
- Purchases, publishing, external messages, account or credential changes
- Destructive or difficult-to-recover operations affecting user work
- Expansion beyond the accepted project and milestone scope

Explain the blocker and attempt useful authorized preparation before asking a
focused question. A user-invoked autopilot run may continue interactively; work on
independent tasks while awaiting input, then resume on reply without a new command.
Do not treat silence as approval or restart consumed repair allowances. Scheduled
runs checkpoint with the pending question by their deadline. Hard limits and
explicit project stop/no-contact policies still apply. A blocked-only status report
is not progress; record the recovery attempted and the precise next action.

## Completion rule

The game is complete only when every completion criterion in `PROJECT.md` has durable verification evidence and no required task remains unfinished.


## Workers and production choices

- Allow bounded subagent delegation when the runtime supports it.
- Schedule all independent eligible tasks concurrently up to available runtime worker slots; honor any explicit project worker cap. Refill slots as results arrive, with capacity for distinct verification.
- Count completed cycles plus selected unfinished tasks against the task-cycle limit; repairs and verification use their existing task reservation.
- Pending provider jobs retain reservations without occupying idle agents; reconcile and track them while disjoint work proceeds.
- Coordinator alone updates shared workflow state, reserves/submits paid work, stages and commits; serialize shared application mutations. Keep other live task artifacts out of each task commit.
- Accept work only through a distinct verifier; otherwise leave it at verify.
- Allow reversible production choices within the approved brief. Ask about material direction changes.

## Meshy-only generation

All complex meshes use connected Meshy MCP. Only explicitly designated simple shapes may be created locally. Blender handles noncreative integration, with no creative repair. Rigging and animation production is deferred. Future providers remain inactive until explicit user direction changes policy. Missing Meshy support or allowance blocks generation; do not fall back.

Use `.gameflow/tools/meshy.json` through meshy-config for nonsecret project defaults and recipes. Resolve project defaults, then the selected recipe, then task overrides. No paid generation allowance is configured by default. Connection alone does not authorize spending. When generation is relevant, obtain and record provider/account scope, allowed operations, allowance unit (currency or credits), total cap and period, per-run cap, and expiry if applicable. Do not store secrets.

Before submission, the coordinator records the task's reservation against both remaining caps in durable task evidence. Include outstanding/uncertain jobs in used capacity. If a safe maximum charge cannot be established, ask before submission. Reconcile job IDs and actual charges on completion or resume; do not reset allowances between sessions or blindly retry unknown outcomes. Only the coordinator submits/reserves paid work. Existing project policy overrides template defaults.

## Acceptance and deferred work

Meshy output needs independent cheap delivery verification only: completed job, readable expected files, dependencies, intended import/loading and recorded identity/provenance. Deeper artistic or numerical reviews require explicit user request. Do not launch creative repair or extra variants by default. Gameplay/build tests remain in force.

Skip `deferred` tasks and do not count them as completed cycles. Deferred tasks must have no dependents; combine rigging and animation into one deferred leaf per asset depending on its delivered static mesh. Rescope active contracts explicitly before removing edges, retaining durable rationale. Record reason and explicit reactivation condition; tool availability alone does not reactivate them. Deferred required work prevents claiming the game complete.

On resume, reconcile live owners/jobs, accepted work awaiting commit, pending verification and partial implementation before selecting new work. Preserve checkpoint provenance and unrelated edits; an unchanged authorized checkpoint needs no renewed adoption permission. Record task commit hashes in final nonrecursive bookkeeping.

## End-of-run Git delivery

Allow local commits for independently verified tasks and one final push of completed run commits plus bookkeeping to the current branch’s configured GitHub upstream. Follow the autopilot Finish checks: every selected task must be accepted, done and committed with no unresolved run work. Unselected backlog does not block delivery. Honor explicit no-push overrides; no force pushes, arbitrary remotes, unrelated outgoing commits or pull requests. Record missing upstream, divergence or push failure and recovery without claiming delivery.
