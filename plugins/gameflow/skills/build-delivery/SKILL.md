---
name: build-delivery
description: Build, test, profile, and package an Unreal game under a GameFlow task contract, including Windows and WSL execution boundaries. Use for local validation and delivery artifacts; publishing or distribution requires an explicit request.
---

# Validate and package a game

Read the selected task, project constraints, relevant acceptance standards, and existing build/test instructions. Inspect the project's engine association, target definitions, platform, configuration, and current changes. Use the repository's established build scripts and pinned engine; do not upgrade engine/toolchains or rewrite build configuration merely to get a green result.

Discover actual Unreal MCP capabilities and verify the connected project before editor operations. Use available automation-test, inspection, and profiling operations where they match the task, and native Unreal build/automation tools where needed. Tool availability does not establish successful execution. Follow [references/windows-wsl.md](references/windows-wsl.md) when the agent and engine run on different operating systems.

Before a build, agree ownership through the coordinator: editor automation, cook/package processes, and overlapping output directories must not be mutated concurrently. Account for unsaved editor work; never force-close an editor or kill unrelated processes to unblock a build. Prefer the documented workflow for Live Coding/editor contention and report a precise blocker when it cannot be resolved safely.

Select validation from the change and task acceptance:

- Native/gameplay changes: compile the required target, execute relevant automated tests, and exercise the changed runtime behavior. An editor compile alone does not establish a packaged build.
- Content/import changes: validate asset loading, references, applicable data validation, and representative in-engine behavior. Cook the relevant content when package compatibility is part of acceptance.
- Performance work: read [references/performance-and-packaging.md](references/performance-and-packaging.md) to capture comparable baseline and candidate measurements.
- Delivery: read [references/performance-and-packaging.md](references/performance-and-packaging.md), package the requested platform/configuration to an isolated output directory, then smoke-test the artifact when the environment supports execution.

Record exact commands or tool operations, engine version, source revision plus dirty-state note, target/platform/configuration, result codes, logs, test reports and artifact paths. For timed-out or interrupted work, inspect process/job state before rerunning; do not start duplicate cooks. An accepted asynchronous request or a log line containing “success” is not proof of final process success.

Store durable summaries and enough retained evidence for a verifier to reproduce acceptance. Record skipped or unsupported checks explicitly, including missing SDKs, display/audio access, hardware, or target devices. Do not claim a package was launched when only packaging passed. Update the task and current handoff; leave implementation at `verify`. Distribution, store upload, signing-account changes, deployment, and publishing are outside this skill unless the user explicitly authorized them.

Before stopping, follow the [shared checkpoint protocol](../task-orchestration/references/checkpoints.md), including partial or waiting work. Preserve task change ownership, actual job IDs, artifact identities and the next action independently of worker liveness and Git commit status.
