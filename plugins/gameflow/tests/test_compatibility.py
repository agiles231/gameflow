#!/usr/bin/env python3
"""Exercise additive initialization against independently constructed v1 state."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(script: str, project: Path, *args: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), "--project", str(project), *args],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="gameflow-v1-compatibility-") as folder:
        project = Path(folder)
        flow = project / ".gameflow"

        def write(relative: str, content: bytes) -> None:
            path = flow / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        # Construct legacy state directly, without deriving the fixture from the
        # current initializer or its templates. Existing files are authoritative.
        for relative in (
            "PROJECT.md", "CONSTRAINTS.md", "ART_DIRECTION.md", "GAMEPLAY.md",
            "INTERFACE.md", "ARCHITECTURE.md", "DECISIONS.md", "GLOSSARY.md",
            "verification/standards.md", "sessions/CURRENT.md", "tasks/TASK-0041.md",
        ):
            write(relative, f"# Legacy {relative}\r\n\r\nAuthored content: café.\r\n".encode())
        write("AUTOPILOT.md", b"# Existing project policy\n\nMaximum cycles: 7\nProvider allowance: 12 credits per week\n")
        write("verification/temporary/.gitignore", b"*\n!.gitignore\n")
        write("assets/source/custom.bin", b"\x00\xff\x80legacy source\r\n")
        metadata = {"external_ui": {"labels": ["keep", "v1"], "revision": 17}}
        documents = {
            "tasks/index.json": {
                "schema_version": 1, "next_id": 42, **metadata,
                "tasks": [{"id": "TASK-0041", "title": "Existing work", "status": "verify",
                           "parent": None, "depends_on": [], "owner": "legacy-session",
                           "contract": "tasks/TASK-0041.md", **metadata}],
            },
            "assets/manifest.json": {"schema_version": 1, "assets": [], **metadata},
            "tools/capabilities.json": {"schema_version": 1, "capabilities": [], **metadata},
            "tools/applications.json": {"schema_version": 1, "applications": [], **metadata},
        }
        for relative, value in documents.items():
            write(relative, (json.dumps(value, indent=3) + "\n").encode())

        prefix = b"# Existing instructions\n\nPreserve this guidance.\n\n"
        suffix = b"\n\n# Additional instructions\nKeep this trailing content.\n"
        agents = project / "AGENTS.md"
        agents.write_bytes(prefix + b"<!-- gameflow:start -->\nLegacy managed block\n<!-- gameflow:end -->" + suffix)
        before = {p.relative_to(flow): p.read_bytes() for p in flow.rglob("*") if p.is_file()}

        for _ in range(2):
            run("init_gameflow.py", project, "--name", "Must not replace legacy truth", "--engine", "other")
            for relative, original in before.items():
                assert (flow / relative).read_bytes() == original, f"Existing file changed: {relative}"
            content = agents.read_bytes()
            actual_prefix, managed = content.split(b"<!-- gameflow:start -->", 1)
            _, actual_suffix = managed.split(b"<!-- gameflow:end -->", 1)
            assert actual_prefix == prefix, "Authored AGENTS prefix changed"
            assert actual_suffix == suffix, "Authored AGENTS suffix changed"
            run("validate_gameflow.py", project)

        # Migration preserves independently authored v1 state, not just current templates.
        run("migrate_gameflow.py", project)
        run("migrate_gameflow.py", project, "--apply")
        for relative, original in before.items():
            assert (flow / relative).read_bytes() == original, f"Migration changed legacy state: {relative}"
        run("validate_gameflow.py", project)

    print("GameFlow v1 compatibility tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
