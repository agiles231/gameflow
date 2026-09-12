---
name: task-execution
description: Execute one bounded GameFlow task and leave a clean, resumable checkpoint. Use when implementing gameplay, interface, art, tooling, or content work governed by a GameFlow task contract.
---

# Execute one GameFlow task

Confirm that the selected task is `ready`, its dependencies are `done`, and required inputs exist. Claim it by setting `status` to `executing` and recording ownership in the task index before making conflicting changes.

Read only the task contract, project constraints relevant to it, and its required context. Prefer deterministic files and command-line operations, then application scripting APIs, then purpose-built tools. Use desktop UI interaction only when no reliable programmable path exists.

Keep changes within the contract. Create a child task for discovered work outside scope. Preserve user-authored and unrelated changes.

At the checkpoint, update the contract's completion evidence with changed artifacts, commands or application actions, versions where relevant, and known risks. If implementation is complete, move the task to `verify`, clear transient ownership, and update the session handoff. Do not self-certify it as `done`. If blocked, record the exact unmet input or decision and the safe partial state.
