# GameFlow

GameFlow is a portable Codex plugin for developing games through durable project state, bounded tasks, explicit verification, and disposable agent sessions.

The plugin lives outside game repositories. Each game repository contains only its own `.gameflow/` state and a small managed block in `AGENTS.md`.

## Install

Add this repository as a local Codex plugin source, or copy/link it into your personal plugin directory. Installation mechanics vary by Codex release; the invariant is that the directory containing `.codex-plugin/plugin.json` is the plugin root.

After installation, start a new Codex task and ask: `Initialize GameFlow in this project.` You can also run the deterministic initializer directly:

```text
python <gameflow-plugin>/scripts/init_gameflow.py --project <game-project> --name "My Game" --engine unreal
```

Validate an initialized project with:

```text
python <gameflow-plugin>/scripts/validate_gameflow.py --project <game-project>
```

## Design

- Project truth is stored in version-controlled files, never in chat history.
- `tasks/index.json` is the canonical task graph; task Markdown files contain human-readable contracts.
- Workers receive only explicitly referenced context.
- Implementation and verification are separate states.
- Temporary screenshots live under `.gameflow/verification/temporary/` and are excluded from source control.
- Application APIs and scripts are preferred over desktop automation; UI control is a fallback.

See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for the lifecycle and extension model.
