# Subagent model selection

Before every dispatch or reuse, follow [model routing](../../../docs/MODEL_ROUTING.md).
The coordinator reads `.gameflow/tools/model-routing.json`; when absent, use the
bundled default policy. This is an optional additive configuration, not a new
required task field. Never silently ignore malformed policy. Project/user
restrictions and production permissions still apply.

## Assessment and resolution

Read the contract, required context, acceptance evidence and cumulative repair
history. Assess the actual phase, including all inseparable operations/components,
with the documented 0–3 rubric. Record evidence for each dimension and confidence.
Assess the hardest component; do not average away a difficult component or label
an unknown operation as routine. Split work only when independently deliverable.
Application names and tool access alone do not demonstrate model competence.

Prepare the version-1 assessment and current runtime model/effort inventory shown
in the guide, then run:

```sh
python3 scripts/model_routing.py resolve --project PROJECT --assessment ASSESSMENT.json --runtime RUNTIME.json
```

The runtime inventory must come from current delegation capabilities, filtered by
applicable user/project model restrictions. Do not substitute the public API
catalog or a cached availability claim. `selected` is the only dispatchable result;
`blocked` and invalid input require reconciliation while disjoint eligible work
continues. The resolver does not establish readiness, permissions or tool access.

Use the returned model and reasoning effort explicitly. Use `fork_turns="none"`
when model overrides require it, supplying the complete bounded worker packet,
relevant user authority and failure evidence. Reuse only a worker whose known
model and reasoning satisfy the resolved selection and whose context/role remain
suitable. A follow-up message cannot change its model. Checkpoint and reconcile
ownership before replacing it; interrupting a worker may not release a slot.
Never bypass blocked model selection by assigning the work to a smaller coordinator.

## Repairs and independent verification

Failed-acceptance repairs always select the configured `repair_profile` before
ordinary rules. The shipped profile is Astra/high with no smaller fallback.
Only explicit user-directed policy changes may alter that repair profile; workers
must not rewrite policy or assessments to make an unavailable model eligible.
This configuration refines the default; hard-coded model advice elsewhere must
not override an explicit authorized configuration.

Set `failed_acceptance` for unresolved failed technical or required user acceptance,
including resumed implementation after a failure. Mark remediation child tasks
with `repair_of` pointing to the failed task, even when its lifecycle was later
changed. The resolver also detects nonzero persisted repair counts for unfinished
referenced tasks when `--project` is supplied. Prose findings and failures before
any repair was attempted are not fully machine-detectable: the coordinator must
read them and assess truthfully. Do not clear escalation by renaming work or
changing sessions/workers. Tool errors or unavailable inputs alone are not failed
acceptance; reconcile effects using existing recovery/blocker rules.

Verification is routed by its own checks and does not automatically inherit the
repair profile. Keep the verifier distinct from every implementer/repairer. A
verification worker must not perform repair mutations under a cheaper verification
selection. Reassess and resolve before changing roles or scope.

Model selection never reactivates deferred animation, authorizes new generations,
changes acceptance criteria, resets repair allowances or bypasses user judgments.
Without delegation, sequential execution and separate-session verification remain
supported only when the executing model meets the applicable routing requirements.

## Evidence and tuning

Store assessment and resolver output as compact local evidence; reference their
paths and policy hash from existing contract completion notes and handoff. Record
requested and actual model/effort when observable, role, rule/profile, fallback,
artifact identity, acceptance outcome and failure cause. Unknown actual identity
must remain unknown. Preserve this evidence across repairs and resumes.

Use the guide's replay workflow and real acceptance outcomes to propose policy
improvements. Do not claim that replay proves model proficiency, invent costs, or
automatically tune policy during execution. Shared policy remains coordinator-owned
and changes require user direction; ordinary task execution cannot loosen it.
