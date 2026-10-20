"""Render discovery and production contracts from one shared template."""
from pathlib import Path
import re


def render_contract(task_id, title, discovery=False, experiment=False):
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
    if experiment:
        values['OUTCOME'] = 'Resolve a bounded hypothesis and record the decision, including a negative result.'
        values['ACCEPTANCE'] = '- Compare against the stated baseline using the defined measurements.\n- Record adopted/rejected/superseded/inconclusive and the checked artifact identities.\n- Create a delivery follow-up if an adopted result still needs production integration.'
        values['OUTPUTS'] = '- Compact experiment conclusion in the task contract.\n- Candidate payloads and detailed measurements in ignored Experiments/ or Artifacts/.'
    content = (Path(__file__).resolve().parent.parent / "templates/task-contract.md").read_text(encoding="utf-8")
    # Single substitution prevents authored titles from being interpreted as placeholders.
    rendered = re.sub(r"\{\{([A-Z_]+)\}\}", lambda match: values[match[1]], content)

    if experiment:
        rendered += "\n## Experiment design\n\n- Hypothesis: define.\n- Baseline: identify.\n- Bounded variants: enumerate.\n- Resource budget: specify time, compute and provider spend.\n- Measurements: define comparable observations.\n- Stop condition: specify.\n- Decision: pending.\n"
    return rendered
