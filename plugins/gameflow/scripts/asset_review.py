#!/usr/bin/env python3
"""Maintain revision-bound optional asset review; never changes task acceptance."""
import argparse
import datetime as dt
import json
from pathlib import Path

STATUSES = {"pending", "approved", "disapproved"}


def empty_queue():
    return {"schema_version": 1, "enabled": True, "window_size": 5, "entries": [],
            "presentation": {"status": "pending", "selection": [], "reason": "Not presented yet"}}


def validate(queue):
    if not isinstance(queue, dict) or queue.get("schema_version") != 1:
        raise ValueError("manual-review must have schema_version 1")
    if not isinstance(queue.get("enabled"), bool) or queue.get("window_size") != 5:
        raise ValueError("manual-review requires enabled boolean and window_size 5")
    entries = queue.get("entries")
    if not isinstance(entries, list):
        raise ValueError("manual-review entries must be a list")
    identities, current = set(), set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("review entry must be an object")
        for field in ("asset_id", "task_id", "revision", "artifact", "completed_at"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                raise ValueError(f"review entry requires {field}")
        identity = (entry["asset_id"], entry["revision"])
        if identity in identities or not isinstance(entry.get("status"), str) or entry.get("status") not in STATUSES or not isinstance(entry.get("current"), bool):
            raise ValueError("duplicate revision or invalid review status/current")
        identities.add(identity)
        if entry["current"]:
            if entry["asset_id"] in current:
                raise ValueError("more than one current revision for asset")
            current.add(entry["asset_id"])
        if entry["status"] != "pending" and not entry.get("user_feedback"):
            raise ValueError("review decision requires explicit user feedback")
    presentation = queue.get("presentation")
    if not isinstance(presentation, dict) or not isinstance(presentation.get("status"), str) or presentation.get("status") not in {"pending", "shown", "deferred"}:
        raise ValueError("invalid review presentation")
    if not isinstance(presentation.get("selection"), list) or not isinstance(presentation.get("reason"), str):
        raise ValueError("presentation requires selection and reason")


def selection(queue):
    # Append order is completion order, independent of clock skew and equal timestamps.
    return list(reversed([e for e in queue["entries"] if e["current"] and e["status"] == "pending"]))[:5] if queue["enabled"] else []


def enqueue(queue, asset_id, task_id, revision, artifact, completed_at):
    for entry in queue["entries"]:
        if (entry["asset_id"], entry["revision"]) == (asset_id, revision):
            if entry["task_id"] != task_id or entry["artifact"] != artifact:
                raise ValueError("revision already recorded with different task/artifact")
            return  # Retry must not reset approval or reorder an older revision.
    for entry in queue["entries"]:
        if entry["asset_id"] == asset_id:
            entry["current"] = False
    queue["entries"].append(dict(asset_id=asset_id, task_id=task_id, revision=revision,
        artifact=artifact, completed_at=completed_at, current=True, status="pending"))
    queue["presentation"] = {"status": "pending", "selection": [], "reason": "New delivery"}


def decide(queue, asset_id, revision, status, feedback, now):
    if status not in {"approved", "disapproved"} or not feedback.strip():
        raise ValueError("decision requires approval/disapproval and explicit user feedback")
    entry = next((e for e in queue["entries"] if e["asset_id"] == asset_id and e["revision"] == revision), None)
    if entry is None:
        raise ValueError("unknown asset revision")
    entry.setdefault("decisions", []).append({"status": status, "user_feedback": feedback, "at": now})
    entry.update(status=status, user_feedback=feedback, reviewed_at=now)
    queue["presentation"] = {"status": "pending", "selection": [], "reason": "Review decision changed selection"}
    return entry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("select")
    commands.add_parser("validate")
    add = commands.add_parser("enqueue")
    for key in ("asset-id", "task-id", "revision", "artifact"):
        add.add_argument("--" + key, required=True)
    decision = commands.add_parser("decide")
    for key in ("asset-id", "revision", "feedback"):
        decision.add_argument("--" + key, required=True)
    decision.add_argument("--status", choices=["approved", "disapproved"], required=True)
    presented = commands.add_parser("present")
    presented.add_argument("--status", choices=["shown", "deferred"], required=True)
    presented.add_argument("--reason", required=True)
    presented.add_argument("--selection", type=Path, help="JSON array of exact asset_id/revision pairs actually shown; required for shown")
    args = parser.parse_args()
    path = args.project / ".gameflow/assets/manual-review.json"
    try:
        queue = json.loads(path.read_text()) if path.exists() else empty_queue()
        validate(queue)
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        if args.command == "enqueue":
            enqueue(queue, args.asset_id, args.task_id, args.revision, args.artifact, now)
        elif args.command == "decide":
            entry = decide(queue, args.asset_id, args.revision, args.status, args.feedback, now)
            if args.status == "disapproved":
                print(json.dumps({"coordinator_action": "reopen_original_task_interactively" if entry["current"] else "record_historical_feedback_only", "task_id": entry["task_id"], "current_revision": entry["current"]}))
        elif args.command == "present":
            selected = [{"asset_id": e["asset_id"], "revision": e["revision"]} for e in selection(queue)]
            if args.status == "shown":
                if args.selection is None or json.loads(args.selection.read_text()) != selected:
                    raise ValueError("shown requires exact displayed selection matching current queue")
            queue["presentation"] = {"status": args.status, "reason": args.reason, "at": now,
                "selection": selected}
        validate(queue)
        if args.command in {"enqueue", "decide", "present"}:
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(queue, indent=2) + "\n")
            temporary.replace(path)
        print(json.dumps(selection(queue), indent=2))
        return 0
    except (ValueError, OSError) as error:
        parser.exit(1, f"asset-review: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
