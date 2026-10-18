#!/usr/bin/env python3
"""Exercise task graph validation on isolated durable-state fixtures."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="gameflow-graph-") as folder:
        project = Path(folder)
        subprocess.run([sys.executable, str(ROOT / "scripts/init_gameflow.py"),
                        "--project", folder, "--name", "Graph fixture"],
                       check=True, capture_output=True)
        flow = project / ".gameflow"
        index_path = flow / "tasks/index.json"
        baseline = json.loads(index_path.read_text())
        second = copy.deepcopy(baseline["tasks"][0])
        second.update(id="TASK-0002", status="deferred", depends_on=["TASK-0001"], parent="TASK-0001")
        baseline["tasks"].append(second)
        baseline["next_id"] = 3
        baseline["custom_metadata"] = {"ui": ["preserve", 42]}
        second["custom_metadata"] = {"future": True}

        def check(index, success: bool) -> None:
            nonlocal checks
            original = (json.dumps(index, indent=2) + "\n").encode()
            index_path.write_bytes(original)
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_gameflow.py"),
                                     "--project", folder], capture_output=True, text=True)
            assert result.returncode == (0 if success else 1), result.stdout + result.stderr
            assert "Traceback" not in result.stderr, result.stderr
            assert index_path.read_bytes() == original, "Validation changed durable state"
            checks += 1

        check(baseline, True)  # Deferred leaf may have prerequisites and a parent.
        for status in ("planned", "ready", "executing", "verify", "done", "blocked"):
            index = copy.deepcopy(baseline)
            index["tasks"][1]["status"] = status
            check(index, True)  # v1 states and unknown metadata remain valid.
        index = copy.deepcopy(baseline)
        index["tasks"][0]["depends_on"] = ["TASK-0002"]
        index["tasks"][1]["depends_on"] = []
        check(index, False)  # A deferred node cannot be required by another task.
        for field, value in (("depends_on", ["TASK-9999"]), ("parent", "TASK-9999"),
                             ("depends_on", None), ("depends_on", "TASK-0001"),
                             ("depends_on", [None, {}, []]), ("parent", {}), ("status", [])):
            index = copy.deepcopy(baseline)
            index["tasks"][1][field] = value
            check(index, False)
        for value in (2, 0, -1, True, 3.5, "3", None):
            index = copy.deepcopy(baseline)
            index["next_id"] = value
            check(index, False)
        for field in ("depends_on", "parent"):
            index = copy.deepcopy(baseline)
            index["tasks"][1]["status"] = "planned"
            index["tasks"][0][field] = ["TASK-0002"] if field == "depends_on" else "TASK-0002"
            check(index, False)
            index = copy.deepcopy(baseline)
            index["tasks"][0][field] = ["TASK-0001"] if field == "depends_on" else "TASK-0001"
            check(index, False)
        outside = project / "outside.md"
        outside.write_text("An existing file outside .gameflow")
        link = flow / "tasks/escape.md"
        link.symlink_to(outside)
        for contract in ("../outside.md", str(outside), "tasks/escape.md", "tasks/missing.md", None):
            index = copy.deepcopy(baseline)
            index["tasks"][1]["contract"] = contract
            check(index, False)
        check([], False)
        index = copy.deepcopy(baseline)
        index["tasks"] = {}
        check(index, False)
        index = copy.deepcopy(baseline)
        index["tasks"].append(None)
        check(index, False)
        index = copy.deepcopy(baseline)
        index["tasks"].append(copy.deepcopy(index["tasks"][0]))
        check(index, False)
    print(f"GameFlow task graph tests passed ({checks} cases).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
