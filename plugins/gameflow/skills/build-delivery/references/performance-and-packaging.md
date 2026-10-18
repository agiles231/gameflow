# Comparable profiling and usable packages

## Performance

Use the task's existing budgets and representative scenario. If a task asks for optimization without a numerical budget, capture baseline and candidate under the same conditions and report the measured change; do not invent a pass threshold or claim target compliance. Record machine/GPU, engine/build configuration, resolution, scalability settings, map/save state, input sequence, warm-up and measurement duration.

Use available Unreal trace/stat/profiling tools and retain a trace or structured measurement when supported. Separate frame time, CPU/GPU bottlenecks, memory, load time, and asset budgets as applicable. Avoid deriving performance conclusions from a single screenshot or comparing editor play against a packaged executable. Distinguish measurement noise from a repeatable change; rerun when variance prevents the stated conclusion. Confirm that visual/gameplay acceptance survives the optimization.

## Packaging

Read the selected target/platform/configuration and packaging settings from the task and repository. Check SDK/toolchain availability, included maps/content and required plugins before an expensive package. Use an isolated task-specific output directory and avoid deleting previous user artifacts. Do not introduce signing credentials or change distribution policy.

Collect build, cook, stage, and package results separately when available; record the final process exit status and fresh artifact path. A previously existing executable does not establish current success. Smoke-test the actual output for launch, expected initial map, critical changed behavior, input/audio where applicable, and clean exit. Retain crash/error logs and list environmental checks that could not run.

Record a checksum for a packaged archive when one is produced, along with engine version, source revision/dirty state, target/configuration, known issues, and a launch instruction. This is a local delivery artifact; uploading to a store, public host, or another person is a separate authorized action.
