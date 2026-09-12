#!/usr/bin/env python3
"""End-to-end smoke tests for GameFlow scripts and templates."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], text=True, capture_output=True, check=False)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="gameflow-test-") as folder:
        project = Path(folder)
        (project / "AGENTS.md").write_text("# Existing guidance\n", encoding="utf-8")
        init = run(str(ROOT / "scripts/init_gameflow.py"), "--project", str(project), "--name", "Fixture", "--engine", "unreal")
        assert init.returncode == 0, init.stderr
        first_project = (project / ".gameflow/PROJECT.md").read_text(encoding="utf-8")
        assert "Fixture" in first_project and "unreal" in first_project

        # Idempotency: existing project truth survives a repeated initialization.
        custom = first_project + "\nUser-authored state.\n"
        (project / ".gameflow/PROJECT.md").write_text(custom, encoding="utf-8")
        again = run(str(ROOT / "scripts/init_gameflow.py"), "--project", str(project), "--name", "Ignored")
        assert again.returncode == 0, again.stderr
        assert (project / ".gameflow/PROJECT.md").read_text(encoding="utf-8") == custom
        assert (project / "AGENTS.md").read_text(encoding="utf-8").count("<!-- gameflow:start -->") == 1

        task = run(str(ROOT / "scripts/new_task.py"), "--project", str(project), "--title", "Build fixture")
        assert task.returncode == 0, task.stderr
        assert task.stdout.strip() == "TASK-0002"
        index = json.loads((project / ".gameflow/tasks/index.json").read_text(encoding="utf-8"))
        assert index["tasks"][-1]["status"] == "planned"

        valid = run(str(ROOT / "scripts/validate_gameflow.py"), "--project", str(project))
        assert valid.returncode == 0, valid.stdout + valid.stderr
        assert not list((project / ".gameflow/verification/temporary").glob("*.png"))

    print("GameFlow end-to-end tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
