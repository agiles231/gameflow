# Native Windows engine from WSL

Establish which host executes each operation: Codex shell, Unreal process, MCP server, and build subprocess. A server may execute on Windows even when the client is in WSL. Obtain the current project path from the actual editor/tool where possible and compare it to the selected repository before mutations.

Resolve the `.uproject`, engine installation, automation/build launcher, SDK, and output locations from repository configuration and installed tools. Never assume an engine install directory or engine version. Do not use a Linux engine binary to build a Windows editor project unless the project explicitly provides that workflow.

For WSL-mounted Windows files, use `wslpath -w` when available to derive a native path, then verify existence from the Windows side. The familiar `/mnt/c/...` to `C:\...` mapping does not cover arbitrary mounts or every server host. If the repository lives in the WSL filesystem, verify that the Windows engine supports its actual path and file access; do not silently copy the project and diverge source state.

Use the native Windows build or automation launcher through a supported host process. Prefer structured argument arrays or a small inspected temporary PowerShell script when shell boundaries make quoting fragile. Treat project names, paths, and configuration values as data; preserve spaces and avoid interpolating untrusted values into executable command strings. Do not invent command flags: use established project scripts or the installed engine's help/current official documentation.

Keep shell paths and application-native paths explicit in evidence. Ensure logs and outputs are accessible to both the producing process and verifier. Propagate the actual child process exit code; the shell wrapper succeeding is insufficient. Check filesystem timestamps and artifact identity when reading logs so stale reports cannot pass a fresh build.
