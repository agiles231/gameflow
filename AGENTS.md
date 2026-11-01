# Repository rules

Follow [the repository commit, push, and version policy](REPOSITORY_POLICY.md)
for every change. Workers leave Git operations to the coordinating agent.

## Compatibility and migrations

Any change that breaks compatibility must include an accompanying migration
script in the same change. This includes changes to persisted project/configuration
formats, task contracts, command-line interfaces, or previously supported behavior.
A version bump or manual upgrade instructions alone do not satisfy this rule.

The script must provide a read-only preview and explicit apply mode, preserve
unrelated user data, retain recoverable originals, and be safe to run again.
Document the affected versions, invocation and recovery procedure. Include tests
for migration from the supported old format, repeat application, invalid inputs
and preservation of unrelated state. If automatic migration cannot be completed,
the script must stop safely and report the exact remaining manual action.

For backward-compatible changes, state why existing inputs and behavior remain
supported and cover that claim with appropriate regression tests.

## Routine execution authority

Within the user-requested scope, proceed with reading, editing, tests, version
updates, commits, pushes, and local plugin refreshes without asking for repeated
confirmation. Repository-local Codex settings request no approval prompts for
trusted sessions. Honor actual runtime restrictions and explicit user limits;
ask only for missing decisions or authority that materially changes the scope.
