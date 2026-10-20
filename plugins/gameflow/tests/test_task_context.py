#!/usr/bin/env python3
"""Context packets preserve requirements and reject invalid references/graphs."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from task_context import packet, parse_context, BOOTSTRAP
from task_contract import render_contract


def main():
    with tempfile.TemporaryDirectory() as folder:
        project = Path(folder)
        subprocess.run([sys.executable, str(ROOT / "scripts/init_gameflow.py"), "--project", folder, "--name", "Context"], check=True, capture_output=True)
        before = {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        result, code = packet(project, "TASK-0001")
        assert code == 0 and result["context"]["format"] == "standard", result
        assert len(result["context"]["required"]) == 5 and not result["warnings"]
        assert result["task"]["status"] == "ready"
        assert before == {p.relative_to(project): p.read_bytes() for p in project.rglob("*") if p.is_file()}
        block = (ROOT / "templates/AGENTS.block.md").read_text()
        assert all(path in block for path in BOOTSTRAP)
        assert "tasks/index.json" not in (ROOT / "templates/gameflow/sessions/CURRENT.md").read_text()
        contract = project / ".gameflow/tasks/TASK-0001.md"
        assert contract.read_text() == render_contract("TASK-0001", "Define the first vertical slice", discovery=True)
        subprocess.run([sys.executable, str(ROOT / "scripts/new_task.py"), "--project", folder, "--title", "Second"], check=True, capture_output=True)
        assert (project / ".gameflow/tasks/TASK-0002.md").read_text() == render_contract("TASK-0002", "Second")
        (project / "reference.md").write_text("# Example heading\n\n## Example heading\n")
        def context(target):
            return f"## Context\n\n### Required\n\n- [Reference]({target})\n\n### Excluded\n\n- History.\n"
        parsed, warnings, errors = parse_context(context("reference.md#example-heading-1"), project)
        assert not warnings and not errors and parsed["excluded"] == "- History."
        for target in ("missing.md", "reference.md#missing", "../outside.md", "/etc/passwd", "https://example.com/doc", "C:/secret", "reference.md?query=1"):
            assert parse_context(context(target), project)[2], target
        (project / "outside").symlink_to("/tmp", target_is_directory=True)
        assert parse_context(context("outside/anything.md"), project)[2]
        legacy = "## Context\n\nRequired: inspect the existing engine integration.\n\n## Completion evidence\nNone."
        contract.write_text(legacy)
        result, code = packet(project, "TASK-0001")
        assert code == 0 and result["warnings"] and "existing engine" in result["context"]["raw"]
        extra = context("reference.md").replace("### Excluded", "Also read the user's design notes.\n\n### Excluded")
        parsed, warnings, errors = parse_context(extra, project)
        assert warnings and "design notes" in parsed["raw"] and not errors
        assert parse_context(context("reference.md") + "\n### Additional\nDo not omit me.", project)[1]
        assert packet(project, "TASK-9999")[1] == 1
        index_path = project / ".gameflow/tasks/index.json"
        index = json.loads(index_path.read_text())
        index["tasks"][0]["status"] = "verify"
        index["tasks"][0]["owner"] = "prior-session"
        index_path.write_text(json.dumps(index))
        result, code = packet(project, "TASK-0001")
        assert code == 0 and result["recovery"] == ["owner", "verify"]
        # Invalid unrelated graph state must block even a valid selected record.
        index["tasks"][1]["depends_on"] = ["TASK-0002"]
        index_path.write_text(json.dumps(index))
        assert packet(project, "TASK-0001")[1] == 1
    print("Task context tests passed.")


if __name__ == "__main__":
    main()
