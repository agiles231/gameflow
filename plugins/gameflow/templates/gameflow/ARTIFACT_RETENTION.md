# Asset, experiment and verification retention

Track accepted production source/runtime assets, code, generator recipes, task/epic
contracts and compact conclusions, decisions and acceptance notes. Preserve source
inputs needed to reproduce accepted assets. Verification standards remain tracked.

Keep experimental payloads and detailed verification local-only: screenshots,
renders, per-frame measurements, logs, comparison meshes, failed exports and duplicate
snapshots. Use ignored Experiments/, Artifacts/ or .gameflow/verification/ outputs.
Never force-add these during routine work. Promote accepted assets to production
paths, preserving stable runtime references where practical. Keep experiment design
and outcomes in task records even when payloads are discarded.

A fresh clone intentionally lacks detailed historical evidence. Acceptance notes
must identify criteria, outcome, checked revision/hash and reproduction commands,
not rely solely on a local report link. Missing local evidence is not proof of failure
or a new verification pass; repeat checks when current acceptance requires them.
Keep a separate backup for local-only files that matter. No LFS or external artifact
service is configured automatically.

Fresh initialization ignores /Artifacts/, /Experiments/ and detailed verification.
For existing projects, review authored ignore rules and tracked contents explicitly.
Ignoring an already tracked file does not untrack it or remove historical blobs.
Do not remove tracked assets or rewrite history as part of initialization/resume.
Use scripts/artifact_audit.py --project PROJECT for a read-only inventory.

For an explicitly requested history cleanup, identify accepted source/runtime
references, preserve local payloads, make and verify an external all-ref bundle,
and review the exact branch/tag scope and removal paths. scripts/prepare_history_cleanup.py
requires --project, --output (new external directory), --branch, --backup,
--filter-repo (supplied official script) and --paths-file (reviewed removal list).
It prepares an isolated single-branch clone, checks retained tip-tree equality,
and never updates the source repository or pushes. Untrack selected outputs in a
reviewed policy commit first so retained tip equality can hold. Other refs still
retain their old history. Publishing a rewrite requires explicitly authorized scope,
a branch-specific lease and verification that unrelated refs stayed unchanged.
