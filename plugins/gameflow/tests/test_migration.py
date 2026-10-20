#!/usr/bin/env python3
"""Exercise byte-preserving upgrades, legacy state, and guarded rollback."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from managed_guidance import render, replace_checked
from migrate_gameflow import inspect, apply, rollback


def snapshot(root):
    return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def rejects(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("expected rejection")


def main():
    with tempfile.TemporaryDirectory() as folder:
        project = Path(folder)
        subprocess.run([sys.executable, str(ROOT / "scripts/init_gameflow.py"), "--project", folder, "--name", "Migration"], check=True, capture_output=True)
        agents = project / "AGENTS.md"
        prefix = "# Authored café\r\n\r\n".encode()
        suffix = b"\r\n\r\n# Keep trailing guidance\r\n"
        original = prefix + b"<!-- gameflow:start -->\r\nold\r\n<!-- gameflow:end -->" + suffix
        agents.write_bytes(original)
        handoff = project / ".gameflow/sessions/CURRENT.md"
        handoff.write_bytes(b"# Current handoff\r\n## Resume procedure\r\nRead tasks/index.json\r\nKeep this state.\r\n")
        index_path = project / ".gameflow/tasks/index.json"
        index = json.loads(index_path.read_text())
        index["tasks"][0].update(status="executing", owner="existing-worker", checkpoint={
            "version": 1, "phase": "executing", "authority": "existing request",
            "base_head": "a" * 40, "owner": "existing-worker", "owned_paths": {},
            "artifact_paths": [], "preserved_baseline": {}, "shared_state_review": "reviewed",
            "jobs": [{"id": "paid-existing-job", "status": "RUNNING", "reserved_credits": 12}],
            "repair_counts": {"delivery": 1}, "next_action": "poll existing job",
            "acceptance": None, "commit": {"state": "pending", "hash": None}})
        index_path.write_text(json.dumps(index))
        before = snapshot(project)
        old, new, report = inspect(project)
        assert snapshot(project) == before and report["manual_followups"] and report["diff"]
        assert new.startswith(prefix) and new.endswith(suffix)
        assert b"\n" not in new.replace(b"\r\n", b"")
        applied = apply(project, old, new, report)
        receipt = applied["receipt"]
        assert agents.read_bytes() == new
        assert all((project / path).read_bytes() == data for path, data in before.items() if str(path) != "AGENTS.md")
        once = snapshot(project)
        old, new, report = inspect(project)
        assert apply(project, old, new, report)["mode"] == "unchanged" and snapshot(project) == once
        assert rollback(project, Path(receipt))["mode"] == "rollback_preview" and snapshot(project) == once
        backup = project / Path(receipt).parent / "AGENTS.md.before"
        backup.write_bytes(original + b"tampered")
        rejects(lambda: rollback(project, Path(receipt), True))
        backup.write_bytes(original)
        agents.write_bytes(new + b"later change")
        rejects(lambda: rollback(project, Path(receipt), True))
        agents.write_bytes(new)
        rollback(project, Path(receipt), True)
        assert agents.read_bytes() == original
        old, new, report = inspect(project)
        agents.write_bytes(original + b"concurrent edit")
        rejects(lambda: apply(project, old, new, report))
        rejects(lambda: replace_checked(agents, original, new))
        for malformed in (b"<!-- gameflow:start -->", b"<!-- gameflow:end -->", b"<!-- gameflow:end --><!-- gameflow:start -->", original + original):
            agents.write_bytes(malformed)
            frozen = snapshot(project)
            rejects(lambda: inspect(project))
            assert snapshot(project) == frozen
            result = subprocess.run([sys.executable, str(ROOT / "scripts/init_gameflow.py"), "--project", folder, "--name", "Unchanged"], capture_output=True)
            assert result.returncode != 0 and snapshot(project) == frozen
        # Appending preserves all authored bytes; absent files can also be undone.
        agents.write_bytes(prefix)
        old, new, report = inspect(project)
        assert new.startswith(prefix)
        agents.unlink()
        old, new, report = inspect(project)
        assert not report["errors"]
        receipt = apply(project, old, new, report)["receipt"]
        rollback(project, Path(receipt), True)
        assert not agents.exists()
        # Structural errors block apply without creating any new backup.
        (project / ".gameflow/tasks/index.json").write_text('{"tasks":null}')
        old, new, report = inspect(project)
        assert report["errors"]
        frozen = snapshot(project)
        rejects(lambda: apply(project, old, new, report))
        assert snapshot(project) == frozen
        result = subprocess.run([sys.executable, str(ROOT / "scripts/migrate_gameflow.py"), "--project", folder, "--apply"], capture_output=True, text=True)
        assert result.returncode == 1 and json.loads(result.stdout)["errors"]
        assert snapshot(project) == frozen
    # A symlinked migration directory must not allow rollback to write outside.
    with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as outside:
        project = Path(folder)
        (project / ".gameflow").mkdir()
        (project / ".gameflow/migrations").symlink_to(outside, target_is_directory=True)
        rejects(lambda: rollback(project, Path(".gameflow/migrations/receipt.json"), True))
    print("Migration tests passed.")


if __name__ == "__main__":
    main()
