#!/usr/bin/env python3
"""Print task context references without loading unrelated documents or history."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from resume_view import recovery_reasons
from validate_gameflow import load_json, validate_task_graph

BOOTSTRAP = [".gameflow/PROJECT.md", ".gameflow/CONSTRAINTS.md",
             ".gameflow/sessions/CURRENT.md"]


def section(text, name, level=2):
    pattern = rf"^{'#' * level} {re.escape(name)}\s*$"
    match = re.search(pattern, text, re.M)
    if not match:
        return None
    tail = text[match.end():]
    end = re.search(rf"^#{{1,{level}}} ", tail, re.M)
    return (tail[:end.start()] if end else tail).strip()


def heading_ids(text):
    """Conventional Markdown heading slugs, including duplicate suffixes."""
    counts = {}
    result = set()
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        if fenced:
            continue
        match = re.match(r"^#{1,6}\s+(.+?)(?:\s+#+)?\s*$", line)
        if not match:
            continue
        slug = re.sub(r"[^\w\- ]", "", match[1].lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(slug + (f"-{count}" if count else ""))
    return result


def parse_context(text, project):
    raw = section(text, "Context")
    required = section(raw or "", "Required", 3)
    excluded = section(raw or "", "Excluded", 3)
    warnings, errors, references = [], [], []
    if required is None or excluded is None:
        return {"format": "legacy", "raw": raw, "required": [], "excluded": None}, [
            "Legacy or missing Context: read the full contract directly; no requirements were inferred."], []
    unparsed = []
    # Any content outside the recognized subsections must remain visible.
    headings = list(re.finditer(r"^### (.+)$", raw, re.M))
    if raw[:headings[0].start()].strip():
        unparsed.append(raw[:headings[0].start()].strip())
    for i, heading in enumerate(headings):
        if heading[1].strip() not in ("Required", "Excluded"):
            unparsed.append(raw[heading.start():headings[i+1].start() if i+1 < len(headings) else len(raw)])
    if sum(h[1].strip() == "Required" for h in headings) != 1 or sum(h[1].strip() == "Excluded" for h in headings) != 1:
        unparsed.append("Duplicate Context subsections; read the full contract.")
    for line in required.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"\s*- \[([^\]]+)\]\(([^\s)]+)\)\s*", line)
        if not match:
            unparsed.append(line)
            continue
        target = match[2]
        parsed = urlsplit(target)
        relative = unquote(parsed.path)
        path = project / relative
        if parsed.scheme or parsed.netloc or parsed.query or not relative or "\\" in relative or Path(relative).is_absolute() or ".." in Path(relative).parts or not path.resolve().is_relative_to(project.resolve()):
            errors.append(f"Required context must stay inside the project: {target}")
            continue
        entry = {"label": match[1], "path": relative}
        if parsed.fragment:
            entry["heading"] = unquote(parsed.fragment)
        references.append(entry)
        if not path.is_file():
            errors.append(f"Required context file is missing: {relative}")
        elif parsed.fragment:
            try:
                if unquote(parsed.fragment) not in heading_ids(path.read_text(encoding="utf-8")):
                    errors.append(f"Required context heading is missing: {target}")
            except (OSError, UnicodeError) as exc:
                errors.append(f"Cannot inspect heading {target}: {exc}")
    result = {"format": "standard", "required": references, "excluded": excluded}
    if unparsed:
        result.update(raw=raw, unparsed=unparsed)
        warnings.append("Unparsed Context content: read the full contract directly; do not omit these requirements.")
    return result, warnings, errors


def packet(project, task_id):
    project = project.resolve()
    flow = project / ".gameflow"
    errors = []
    index = load_json(flow / "tasks/index.json", errors)
    if not errors:
        validate_task_graph(index, flow, errors)
    if errors:
        return {"errors": errors}, 1
    by_id = {task["id"]: task for task in index["tasks"]}
    if task_id not in by_id:
        return {"errors": [f"Unknown task: {task_id}"]}, 1
    task = by_id[task_id]
    context, warnings, errors = parse_context((flow / task["contract"]).read_text(encoding="utf-8"), project)
    return {"task": task, "contract": ".gameflow/" + task["contract"],
            "bootstrap": BOOTSTRAP, "dependencies": {dep: by_id[dep]["status"] for dep in task["depends_on"]},
            "recovery": recovery_reasons(task), "context": context, "warnings": warnings, "errors": errors,
            "note": "Read the contract and required references. This packet does not establish authority, liveness, readiness or acceptance."}, int(bool(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--task", required=True)
    args = parser.parse_args()
    try:
        result, code = packet(args.project, args.task)
    except (OSError, UnicodeError, ValueError, RuntimeError) as exc:
        result, code = {"errors": [str(exc)]}, 1
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
