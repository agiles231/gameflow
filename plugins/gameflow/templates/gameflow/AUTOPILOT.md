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

## Always stop for human input

- A missing creative or product decision that materially changes the result
- Purchases, publishing, external messages, account or credential changes
- Destructive or difficult-to-recover operations affecting user work
- Expansion beyond the accepted project and milestone scope

## Completion rule

The game is complete only when every completion criterion in `PROJECT.md` has durable verification evidence and no required task remains unfinished.
