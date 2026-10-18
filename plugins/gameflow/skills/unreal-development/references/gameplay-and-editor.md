# Gameplay and editor work

## C++ and gameplay

Inspect the `.uproject`, module rules, existing target files, and build scripts before choosing the engine executable or target. Keep gameplay logic consistent with the project's architecture. Honor C++-only restrictions across input, state machines, UI, AI, and test scaffolding; do not silently create a Blueprint substitute when MCP lacks a C++ operation.

Use source edits for C++ and MCP for supported inspection and editor actions. Choose the established native toolchain for builds. A Live Coding success does not establish a clean editor or packaged build; reflected type/layout changes may need the project's full compile/reload procedure. Coordinate any required shutdown rather than interrupting an unknown session.

Validate the observable contract with an existing automation/functional test or a focused new test when it adds meaningful coverage. Run tests through the exposed MCP runner when supported, otherwise the established command line. Confirm the expected test actually ran and retain result counts/logs; an exit code alone can hide zero matching tests. For input or presentation changes, observe the behavior through the intended player controls as well as relevant logic checks. Include cancellation, reload/save-resume, and invalid inputs only where the change affects them.

## Levels, materials, and audio

Use a task-owned test map or scoped actors for experiments. Preserve production map state and unrelated actors. Inspect spawn transforms, collision/navigation effects, streaming membership, and runtime references relevant to the task. Record deterministic setup or seeds when reproducing simulation behavior.

For delivered Meshy assets, limit material work to supplied-map integration and delivery checks; do not perform creative repair or unsolicited appearance/cost audits. Other explicitly scoped gameplay/material work retains its contract. For materials, inspect existing parent/instance conventions, texture color-space flags, channel packing, normal-map convention, and intended shading model before setting properties. Inspect the result under representative lighting and distance; a graph that compiles can still violate art direction or cost budgets. Do not guess a shader API from another engine version.

For audio, track original source/provenance and import/compression settings. Check playback, attenuation, spatialization, looping seams, triggers and concurrency at the intended listener positions. A waveform preview does not establish in-game integration. Route synthesis or external generation through available generation skills only when appropriate and authorized.

For UI, keep text/layout/input readable at required resolutions and control schemes. Inspect focus and pause/navigation behavior using the project's implementation language and existing UI framework.
