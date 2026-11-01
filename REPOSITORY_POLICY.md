# Commit, push, and version policy

For every completed repository change, update the applicable release version,
commit all work belonging to that change, and push the resulting commits to the
current branch's configured remote. This policy applies to the current release
and future work in this repository. It is not a policy for game projects created
by the plugin.

Use standard Semantic Versioning: increment major for incompatible changes,
minor for backward-compatible features, and patch for backward-compatible fixes.
Update the plugin manifest and current-version documentation together. Repository
compatibility and migration requirements in `AGENTS.md` still apply.

Commit usable incomplete or interrupted work as an explicitly labeled partial/WIP
checkpoint with its limitations and next action. A commit or push preserves work;
it does not establish verification, acceptance, game completion, or publication.
Never claim failed or untested criteria pass to make a commit possible.

The coordinator reviews and stages only the intended change, runs appropriate
checks, and performs Git operations. Preserve unrelated edits, secrets, and other
workers' live outputs. Workers return changes for the coordinator to commit.
Before pushing, check the configured remote, branch, outgoing commit scope, and
fast-forward relationship. Never force-push, rewrite unrelated history, invent a
remote, or bypass explicit user restrictions or execution approvals.

If a commit or push cannot safely complete, retain the work and report the exact
blocker and recovery action. Do not report delivery until the remote branch has
been checked. A delivery blocker is not permission to discard work.
