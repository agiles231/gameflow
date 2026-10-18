# Verification standards

- Use a distinct verifier and frozen artifact identities; never accept the worker's claim alone.
- Verify the task's applicable acceptance criteria with observed evidence. Record skipped/unavailable checks explicitly.
- Meshy acceptance is cheap delivery verification: job completion, readable expected files, required dependencies, intended import/loading, and recorded identity/provenance.
- Do not add artistic, anatomy, topology or numerical quality audits, render batches or creative repair to Meshy delivery unless explicitly requested.
- Gameplay, UI/audio, build, packaging and explicitly scoped performance tests remain required for their tasks.
- Rigging and animation production is deferred, not passed or complete.
- Record versions, stable paths/hashes and relevant reproduction steps. Transient captures go in `temporary/` and are not durable evidence.
- A failed check returns the task for an allowed bounded technical repair or leaves it blocked with a concrete reason. Never erase prior findings.
