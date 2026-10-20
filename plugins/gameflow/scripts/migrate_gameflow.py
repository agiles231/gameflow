#!/usr/bin/env python3
"""Preview or explicitly apply a managed-guidance upgrade; preserve authored state."""
import argparse
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import uuid

from managed_guidance import render, replace_checked
from task_context import parse_context
from validate_gameflow import validate_project

PLUGIN = Path(__file__).resolve().parent.parent


def digest(content):
    return hashlib.sha256(content).hexdigest() if content is not None else None


def confined(path, root):
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes project or is a symlink: {path}")


def inspect(project):
    agents = project / "AGENTS.md"
    confined(agents, project)
    original = agents.read_bytes() if agents.exists() else None
    updated = render(original or b"", (PLUGIN / "templates/AGENTS.block.md").read_bytes())
    errors, warnings = validate_project(project, require_entrypoint=False)
    followups = []
    if not errors:
        index = json.loads((project / ".gameflow/tasks/index.json").read_text(encoding="utf-8"))
        for task in index["tasks"]:
            context, notices, issues = parse_context((project / ".gameflow" / task["contract"]).read_text(encoding="utf-8"), project)
            if context["format"] == "legacy" or notices or issues:
                followups.append({"task": task["id"], "contract": task["contract"], "issues": notices + issues})
    handoff = project / ".gameflow/sessions/CURRENT.md"
    if handoff.is_file():
        text = handoff.read_text(encoding="utf-8")
        if "## Resume procedure" in text or "tasks/index.json" in text:
            followups.append({"path": ".gameflow/sessions/CURRENT.md", "issues": [
                "Reconcile legacy resume instructions with the managed AGENTS.md bootstrap; preserve current state and user decisions."]})
    diff = "".join(difflib.unified_diff((original or b"").decode("utf-8").splitlines(keepends=True),
                                     updated.decode("utf-8").splitlines(keepends=True),
                                     fromfile="AGENTS.md (current)", tofile="AGENTS.md (proposed)"))
    return original, updated, {"mode": "preview", "changed_paths": ["AGENTS.md"] if original != updated else [],
                               "diff": diff, "errors": errors, "warnings": warnings, "manual_followups": followups}


def apply(project, original, updated, report):
    if report["errors"]:
        raise ValueError("structural validation failed; migration was not applied")
    if original == updated:
        report["mode"] = "unchanged"
        return report
    target = project / "AGENTS.md"
    if (target.read_bytes() if target.exists() else None) != original:
        raise ValueError("AGENTS.md changed since inspection")
    migrations = project / ".gameflow/migrations"
    confined(migrations, project)
    run = migrations / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:12])
    run.mkdir(parents=True)
    if original is not None:
        (run / "AGENTS.md.before").write_bytes(original)
    receipt = {"schema_version": 1, "plugin_version": json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())["version"],
               "created_at": datetime.now(timezone.utc).isoformat(), "changed_paths": ["AGENTS.md"],
               "original_sha256": digest(original), "result_sha256": digest(updated),
               "original_exists": original is not None, "manual_followups": report["manual_followups"], "state": "prepared"}
    receipt_path = run / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    replace_checked(target, original, updated)
    receipt["state"] = "applied"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    report.update(mode="applied", receipt=str(receipt_path.relative_to(project)))
    return report


def rollback(project, receipt_path, execute=False):
    confined(project / ".gameflow/migrations", project)
    receipt_path = project / receipt_path
    confined(receipt_path, project / ".gameflow/migrations")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("schema_version") != 1 or receipt.get("changed_paths") != ["AGENTS.md"]:
        raise ValueError("unsupported migration receipt")
    target = project / "AGENTS.md"
    confined(target, project)
    current = target.read_bytes() if target.exists() else None
    if digest(current) != receipt["result_sha256"]:
        raise ValueError("AGENTS.md no longer matches the migrated hash; rollback would overwrite later edits")
    backup = receipt_path.parent / "AGENTS.md.before"
    confined(backup, project / ".gameflow/migrations")
    original = backup.read_bytes() if receipt["original_exists"] else None
    if digest(original) != receipt["original_sha256"]:
        raise ValueError("migration backup hash does not match receipt")
    if execute:
        replace_checked(target, current, original)
        receipt["state"] = "rolled_back"
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return {"mode": "rolled_back" if execute else "rollback_preview", "changed_paths": ["AGENTS.md"], "errors": []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Apply the upgrade (or rollback); otherwise preview only")
    parser.add_argument("--rollback", type=Path, metavar="RECEIPT", help="Project-relative receipt path for guarded rollback")
    args = parser.parse_args()
    try:
        project = args.project.resolve()
        if args.rollback:
            report = rollback(project, args.rollback, args.apply)
        else:
            original, updated, report = inspect(project)
            if args.apply and not report["errors"]:
                report = apply(project, original, updated, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return int(bool(report["errors"]))
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        print(json.dumps({"errors": [str(exc)]}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
