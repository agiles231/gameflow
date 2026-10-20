# Upgrade an existing GameFlow project

Version 0.7.0 retains schema version 1. Existing projects and legacy Markdown
contracts remain supported without migration. Refresh the installed local plugin
using the repository README's remove/add procedure and start a fresh session.
Use the refreshed plugin's scripts, not a copied script from an older installation.

## Preview and apply

From the plugin root, with the game project's path as `PROJECT`:

```sh
python3 scripts/migrate_gameflow.py --project PROJECT
python3 scripts/migrate_gameflow.py --project PROJECT --apply
python3 scripts/validate_gameflow.py --project PROJECT
```

Preview is read-only and prints a JSON report containing the managed `AGENTS.md`
diff, structural errors, warnings and manual follow-ups. Apply reruns inspection
and only changes one well-formed managed block (or appends a missing block).
Structural errors or malformed/duplicate markers stop the update. Do not edit
the project concurrently with migration. The command checks source bytes before
replacement but is not a cross-process lock.

Each change saves the original file, if present, and a receipt under
`.gameflow/migrations/`. The receipt records original/result hashes, plugin version,
changed paths and remaining follow-ups. Reapplying current guidance writes nothing.
Unrelated dirty files do not prevent migration and are never staged or committed.

Project direction, constraints, task records/contracts, handoffs, provider jobs,
checkpoint metadata, spending policy and assets are not rewritten. Review the
reported legacy handoff instructions and manually remove or reconcile copied
procedures while preserving current state and authored decisions. The managed
block owns bootstrap order; it does not override project constraints. Legacy
contracts need no bulk conversion: read them directly, or adopt the new Context
format when editing a task. Manual follow-ups remain outstanding even after a
successful managed-block update.

## Rollback

Use the project-relative receipt path printed by apply:

```sh
python3 scripts/migrate_gameflow.py --project PROJECT --rollback .gameflow/migrations/RUN/receipt.json
python3 scripts/migrate_gameflow.py --project PROJECT --rollback .gameflow/migrations/RUN/receipt.json --apply
```

Rollback previews by default. It verifies the backup and refuses to overwrite an
`AGENTS.md` whose hash differs from the migrated result. If the file did not exist
before migration, rollback removes only that unchanged generated file. Receipts
and backups remain for audit. A receipt left in `prepared` state after interruption
can be used to roll back if the file matches its result hash; otherwise inspect
the recorded state instead of forcing restoration. Project state remains usable
with the preceding plugin version; restore that installed version separately if
needed. Run validation after restoring an originally valid entrypoint.

## Planning and retention adoption

Planning migration is a separate explicit operation; see [PLANNING.md](PLANNING.md) for its complete plan format and preview/apply commands. Guidance migration does not alter task metadata, Git tracking or history. Existing retention policy takes precedence; review ignore rules and tracked outputs separately using [ARTIFACT_RETENTION.md](ARTIFACT_RETENTION.md). No Lodgepole-specific task or asset decisions are bundled.
