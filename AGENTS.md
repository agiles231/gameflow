# Repository rules

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
