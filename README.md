# GameFlow marketplace

This repository is a local Codex plugin marketplace containing the GameFlow plugin. GameFlow develops games through durable project state, bounded tasks, explicit verification, and disposable agent sessions.

The marketplace and plugin live outside game repositories. Each game repository contains only its own `.gameflow/` state and a small managed block in `AGENTS.md`.

## Install in the Codex app

1. Open **Plugins** and select **Add plugin marketplace**.
2. Select this repository root—the directory containing `.agents/plugins/marketplace.json`.
3. Open the **GameFlow Local** marketplace and install **GameFlow**.
4. Start a new task so its bundled skills are loaded.

For this checkout, the marketplace root is `C:\workspace\GameWorkflow`. Do not select `plugins\gameflow`; that is the plugin bundle referenced by the marketplace.

In Codex CLI, add this non-default marketplace and install its plugin:

```text
codex plugin marketplace add C:\workspace\GameWorkflow
codex plugin add gameflow@gameflow-local
```

After installation, start a new Codex task in a game project and ask: `Initialize GameFlow in this project.` You can also run the deterministic initializer directly:

```text
python <marketplace>/plugins/gameflow/scripts/init_gameflow.py --project <game-project> --name "My Game" --engine unreal
```

Validate an initialized project with:

```text
python <marketplace>/plugins/gameflow/scripts/validate_gameflow.py --project <game-project>
```

## Design

- Project truth is stored in version-controlled files, never in chat history.
- `tasks/index.json` is the canonical task graph; task Markdown files contain human-readable contracts.
- Workers receive only explicitly referenced context.
- Implementation and verification are separate states.
- Temporary screenshots live under `.gameflow/verification/temporary/` and are excluded from source control.
- Application APIs and scripts are preferred over desktop automation; UI control is a fallback.

See [`plugins/gameflow/docs/WORKFLOW.md`](plugins/gameflow/docs/WORKFLOW.md) for the lifecycle and extension model.
