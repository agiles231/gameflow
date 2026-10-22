# Prepare required user verification

Use this workflow when the task contract or user explicitly requires the user's
judgment or approval. Do not invent a manual gate for ordinary technical checks
or optional asset review. User judgment covers the named criteria; it does not
replace required independent technical verification.

## Set up the actual review

1. Identify the task, exact candidate revision and observable criteria that need
   user approval. Finish authorized implementation and technical preparation first.
   Freeze the reviewed artifact and record its identity; do not keep modifying it
   while an approval question is pending.
2. Discover the appropriate application and check file/project identity, dirty
   state and ownership before opening or changing anything. Use a task-owned
   review scene/instance or a separate instance when safe. Never discard unsaved
   work, replace an unrelated file, take over the user's editor or stop their play
   session to simplify review.
3. Open and prepare the candidate for the specific checks. For a mesh/material,
   open Blender with dependencies loaded, usable shading and relevant framed views;
   use labeled review copies preserving the production source. For gameplay,
   open the correct Unreal project/map and prepare the relevant player start or
   test state with explicit controls. Start PIE only when safe and appropriate.
   For audio or interaction, prepare actual playback/use; an image cannot prove
   those criteria. Use other applications when the artifact requires them.
4. Verify the candidate is actually displayed and inspectable. A saved scene,
   launch command, background process or screenshot file alone does not prove the
   user can see the review. State the application/window, asset or level, short
   revision and starting view. If remote/host access is uncertain, establish that
   the user can access it before requesting approval.

If presentation fails, explain the exact failure, attempt a safe recovery and
prepare a reopenable review artifact plus precise opening steps. Ask for the
missing setup action or location using blocker resolution; do not ask for approval
of unseen work. Do not substitute a static preview for required interaction.

## Ask explicit Yes/No questions

Prefer an available prompted-input tool that supports approval questions, with
`Yes — approve` and `No — needs changes` choices. Never treat a preselected choice
as an answer. If no suitable tool is available, ask the same Yes/No question in
ordinary chat. Keep the question self-contained: identify the displayed revision,
give concrete inspection actions and list the exact approval criteria. Avoid
vague prompts such as “Does it look good?” or “Approved?”

Group only criteria that can reasonably receive one decision. Split unrelated
assets or distinct checks into separate questions, typically one to three at a
time. Example after actually presenting the corresponding candidate:

> In Blender, review `PawRepair` revision `abc123`, framed on the four paws.
> Orbit each paw and check: exactly five claws per paw, no loose fragments, and
> no new visible gaps or stretched texture around the edit. Do you approve this
> revision for these three criteria? Yes — approve / No — needs changes.

Use the task's actual criteria, not the example's anatomy or an invented quality
bar. Say what a Yes approves and what remains to be verified. On No, preserve the
rejected revision and ask which criterion failed if not already clear; a No alone
does not authorize arbitrary regeneration or spending. Continue authorized targeted
revision interactively, within remaining limits, then present the new revision and
ask again. Never carry an approval to changed artifacts.

## Record and continue

The coordinator records the actual presentation, exact question/criteria, candidate
identity, user answer and any feedback in the existing contract and current handoff.
Keep screenshots and detailed inspection output local-only under retention policy.
Optional queue records may accompany an accepted asset, but are not the sole record
of a required gate on an unfinished task.

No answer means pending, not approved or rejected. Keep a required review task at
`verify` while awaiting judgment when implementation is complete; only affected
dependents wait. Continue independent work and resume on reply without requiring
another command. Bind the answer to the frozen revision and recheck identity before
acceptance. An ambiguous answer or changed revision requires clarification/review.
Mark done only when every required user criterion and independent technical check
passes. Scheduled runs preserve the review setup and pending questions by their
deadline; no promise of background waiting.
