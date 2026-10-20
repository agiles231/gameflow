"""Render discovery and production contracts from one shared template."""
from pathlib import Path
import re


def render_contract(task_id, title, discovery=False):
    values = {
        "TASK_ID": task_id, "TITLE": title,
        "OUTCOME": "Define one principal deliverable.",
        "INPUTS": "- Define required inputs.",
        "OUTPUTS": "- Define durable outputs.",
        "ACCEPTANCE": "- Define an observable pass/fail condition.",
        "REQUIRED": "- [Project constraints](.gameflow/CONSTRAINTS.md)\n\nList additional exact project-relative Markdown links before making this task ready.",
    }
    if discovery:
        names = ("PROJECT", "CONSTRAINTS", "ART_DIRECTION", "GAMEPLAY", "INTERFACE")
        values.update(
            OUTCOME="A bounded vertical-slice definition with demonstrable gameplay, art, and interface outcomes.",
            INPUTS="\n".join(f"- `{name}.md`" for name in names),
            OUTPUTS="- Updated project definition documents\n- Child tasks in `tasks/index.json`",
            ACCEPTANCE="- The slice can be demonstrated end to end.\n- Each child task has one principal deliverable.\n- Dependencies and acceptance criteria are explicit.\n- Unknowns that materially change scope are decisions or blocked tasks.",
            REQUIRED="\n".join(f"- [{name}](.gameflow/{name}.md)" for name in names),
        )
    content = (Path(__file__).resolve().parent.parent / "templates/task-contract.md").read_text(encoding="utf-8")
    # Single substitution prevents authored titles from being interpreted as placeholders.
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda match: values[match[1]], content)
