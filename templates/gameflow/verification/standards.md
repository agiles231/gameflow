# Verification standards

- Verify observable output, not the worker's claim.
- Match every acceptance criterion to evidence or mark it failed.
- Record tool/application versions and relevant view settings.
- Use stable file paths, asset identifiers, hashes, or source revisions.
- Put transient captures in `temporary/`; never cite them as durable evidence.
- A failed check returns the task to `executing` or marks it `blocked` with a concrete reason.
