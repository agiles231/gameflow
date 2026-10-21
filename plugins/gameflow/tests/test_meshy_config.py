import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("meshy_config", ROOT / "scripts/meshy_config.py")
meshy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(meshy)


def configured():
    return {
        "version": 1, "status": "ready",
        "operation_defaults": {"mesh": {"settings": {"quality": "draft", "count": 1}}},
        "schema_snapshots": {"mesh": {
            "tool": "test_mcp_mesh", "captured_at": "2026-10-17T00:00:00Z", "prompt_field": "prompt",
            "input_schema": {"type": "object", "properties": {
                "prompt": {"type": "string", "minLength": 1},
                "quality": {"type": "string", "enum": ["draft", "final"]},
                "count": {"type": "integer", "minimum": 1, "maximum": 2}},
                "required": ["prompt", "quality", "count"], "additionalProperties": False}}},
        "recipes": [{"id": "prop", "operation": "mesh", "criteria": "Static environment prop",
                     "priority": 10, "prompt_template": "A ${subject}; cost $$5",
                     "variables": ["subject"], "settings": {"quality": "final"}}]}


class MeshyConfigTests(unittest.TestCase):
    def test_optional_clause_default_toggle_and_literal_text(self):
        config = configured()
        recipe = config["recipes"][0]
        recipe["prompt_template"] = "A ${subject} render ${fur_clause}and soft light."
        recipe["optional_clauses"] = {
            "fur_clause": {"text": "with very little fur detail ", "default": False}}
        original = copy.deepcopy(config)
        for supplied, expected in [({}, ""), ({"fur_clause": False}, ""),
                                   ({"fur_clause": True}, "with very little fur detail ")]:
            result = meshy.resolve(config, "mesh", template_id="prop",
                                   variables={"subject": "elk", **supplied})
            self.assertEqual(result["prompt"], f"A elk render {expected}and soft light.")
            self.assertNotIn("fur_clause", result["arguments"])
        self.assertEqual(config, original)
        recipe["optional_clauses"]["fur_clause"].update(default=True, text="literal $subject $$ ")
        result = meshy.resolve(config, "mesh", template_id="prop", variables={"subject": "elk"})
        self.assertEqual(result["prompt"], "A elk render literal $subject $$ and soft light.")

    def test_optional_clause_rejects_arbitrary_text_and_non_booleans(self):
        config = configured()
        config["recipes"][0].update(prompt_template="${subject}${fur}", optional_clauses={
            "fur": {"text": " with very little fur detail", "default": False}})
        for value in ("with dense fur", "", "false", 0, 1, None, [], {}):
            with self.subTest(value=value), self.assertRaisesRegex(meshy.ConfigError, "booleans"):
                meshy.resolve(config, "mesh", template_id="prop", variables={"subject": "elk", "fur": value})
        with self.assertRaisesRegex(meshy.ConfigError, "Missing or unknown"):
            meshy.resolve(config, "mesh", template_id="prop", variables={"fur": True})

    def test_optional_clause_declarations_are_strict(self):
        for clauses in ([], {"fur": {}}, {"fur": {"text": "fur"}},
                        {"fur": {"text": "fur", "default": 1}},
                        {"fur": {"text": " ", "default": False}},
                        {"fur": {"text": 1, "default": False}},
                        {"fur": {"text": "fur", "default": False, "extra": 1}},
                        {"subject": {"text": "fur", "default": False}},
                        {"bad-name": {"text": "fur", "default": False}},
                        {"unused": {"text": "fur", "default": False}}):
            config = configured()
            config["recipes"][0].update(prompt_template="${subject}${fur}", optional_clauses=clauses)
            with self.subTest(clauses=clauses), self.assertRaises(meshy.ConfigError):
                meshy.validate_config(config)

    def test_optional_clause_cli_boolean_toggle(self):
        config = configured()
        config["recipes"][0].update(prompt_template="${subject}${fur}", optional_clauses={
            "fur": {"text": " with very little fur detail", "default": False}})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "meshy.json"
            path.write_text(json.dumps(config))
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT / "scripts/meshy_config.py"), "resolve",
                                     str(path), "--operation", "mesh", "--template", "prop",
                                     "--variables", '{"subject":"elk","fur":true}'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["prompt"], "elk with very little fur detail")
            self.assertEqual(path.read_bytes(), before)

    def test_template_draft_has_no_provider_defaults(self):
        config = json.loads((ROOT / "templates/gameflow/tools/meshy.json").read_text())
        meshy.validate_config(config)
        self.assertEqual(config["operation_defaults"], {})
        self.assertEqual(config["schema_snapshots"], {})
        with self.assertRaises(meshy.ConfigError):
            meshy.resolve(config, "mesh", template_id="prop")

    def test_merge_render_and_input_unchanged(self):
        config = configured()
        original = copy.deepcopy(config)
        result = meshy.resolve(config, "mesh", ["prop"], variables={"subject": "rock"}, overrides={"count": 2})
        self.assertEqual(result["arguments"], {"prompt": "A rock; cost $5", "quality": "final", "count": 2})
        self.assertTrue(result["runtime_schema_validation_required"])
        self.assertFalse(result["submission_performed"])
        self.assertEqual(config, original)
        explicit = meshy.resolve(config, "mesh", template_id="prop", variables={"subject": "rock"},
                                 overrides={"quality": "draft"})
        self.assertEqual(explicit["settings"]["quality"], "draft")

    def test_priority_tie_and_explicit_selection(self):
        config = configured()
        second = copy.deepcopy(config["recipes"][0])
        second.update(id="hero", priority=20)
        config["recipes"].append(second)
        kwargs = {"variables": {"subject": "rock"}}
        self.assertEqual(meshy.resolve(config, "mesh", ["prop", "hero"], **kwargs)["template_id"], "hero")
        second["priority"] = 10
        with self.assertRaisesRegex(meshy.ConfigError, "Ambiguous"):
            meshy.resolve(config, "mesh", ["prop", "hero"], **kwargs)
        self.assertEqual(meshy.resolve(config, "mesh", template_id="hero", **kwargs)["template_id"], "hero")

    def test_bad_matching_and_variables(self):
        for matches, variables in [([], {"subject": "rock"}), (["unknown"], {}),
                                   (["prop", "prop"], {}), (["prop"], {}),
                                   (["prop"], {"subject": "rock", "extra": "x"}),
                                   (["prop"], {"subject": 1})]:
            with self.subTest(matches=matches, variables=variables), self.assertRaises(meshy.ConfigError):
                meshy.resolve(configured(), "mesh", matches, variables=variables)

    def test_settings_schema_enforced(self):
        for overrides in [{"quality": "ultra"}, {"count": 0}, {"count": "2"}, {"count": True},
                          {"invented": 1}, {"prompt": "bypass"}]:
            with self.subTest(overrides=overrides), self.assertRaises(meshy.ConfigError):
                meshy.resolve(configured(), "mesh", ["prop"], variables={"subject": "rock"}, overrides=overrides)

    def test_required_property_and_nonempty_prompt(self):
        config = configured()
        del config["operation_defaults"]["mesh"]["settings"]["count"]
        with self.assertRaises(meshy.ConfigError):
            meshy.resolve(config, "mesh", ["prop"], variables={"subject": "rock"})

    def test_credentials_are_forbidden_recursively(self):
        for location in ("settings", "schema", "variables", "overrides"):
            config = configured()
            kwargs = {"variables": {"subject": "rock"}}
            if location == "settings":
                config["recipes"][0]["settings"]["nested"] = {"api_key": "sensitive"}
            elif location == "schema":
                config["schema_snapshots"]["mesh"]["input_schema"]["properties"]["Authorization"] = {}
            else:
                kwargs[location] = {"credentials": {"password": "sensitive"}}
            with self.subTest(location=location), self.assertRaisesRegex(meshy.ConfigError, "credential"):
                meshy.resolve(config, "mesh", ["prop"], **kwargs)

    def test_schema_references_cannot_trigger_network(self):
        config = configured()
        config["schema_snapshots"]["mesh"]["input_schema"]["properties"]["count"] = {
            "$ref": "https://invalid.example/schema"}
        with self.assertRaisesRegex(meshy.ConfigError, "references"):
            meshy.validate_config(config)

    def test_rigging_and_animation_deferred(self):
        for tool in ("meshy_rig", "meshy_auto_rigging", "meshy_animation"):
            config = configured()
            config["schema_snapshots"]["mesh"]["tool"] = tool
            with self.subTest(tool=tool), self.assertRaisesRegex(meshy.ConfigError, "deferred"):
                meshy.resolve(config, "mesh", ["prop"], variables={"subject": "rock"})

    def test_draft_to_ready_requires_discovery(self):
        config = configured()
        config["schema_snapshots"] = {}
        config["status"] = "draft"
        meshy.validate_config(config)
        config["status"] = "ready"
        with self.assertRaises(meshy.ConfigError):
            meshy.validate_config(config)

    def test_nested_overrides_replace_and_no_prompt_operation(self):
        config = configured()
        snapshot = config["schema_snapshots"]["mesh"]
        snapshot["input_schema"]["properties"]["options"] = {"type": "object"}
        config["operation_defaults"]["mesh"]["settings"]["options"] = {"a": 1, "b": 2}
        result = meshy.resolve(config, "mesh", ["prop"], variables={"subject": "rock"},
                               overrides={"options": {"a": 3}})
        self.assertEqual(result["arguments"]["options"], {"a": 3})
        snapshot["prompt_field"] = None
        snapshot["input_schema"]["required"].remove("prompt")
        config["recipes"][0].update(prompt_template="", variables=[])
        result = meshy.resolve(config, "mesh", ["prop"])
        self.assertNotIn("prompt", result["arguments"])

    def test_operation_mismatch(self):
        config = configured()
        config["schema_snapshots"]["other"] = copy.deepcopy(config["schema_snapshots"]["mesh"])
        with self.assertRaisesRegex(meshy.ConfigError, "mismatch"):
            meshy.resolve(config, "other", ["prop"], variables={"subject": "rock"})

    def test_ambiguous_json_and_nonfinite_values_rejected(self):
        for value in ('{"id":1,"id":2}', '{"count":NaN}', '{"count":Infinity}', '{"count":1e999}'):
            with self.subTest(value=value), self.assertRaises(meshy.ConfigError):
                meshy.load_json(value)

    def test_nonfinite_public_api_values_rejected(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            config = configured()
            config["schema_snapshots"]["mesh"]["input_schema"]["properties"]["amount"] = {
                "type": "number", "minimum": 0, "maximum": 1}
            with self.subTest(value=value), self.assertRaisesRegex(meshy.ConfigError, "non-finite"):
                meshy.resolve(config, "mesh", ["prop"], variables={"subject": "rock"},
                              overrides={"amount": value})

    def test_invalid_or_unknown_schema_dialect_rejected(self):
        for dialect in ([], 1, "https://invalid.example/unknown-dialect"):
            config = configured()
            config["schema_snapshots"]["mesh"]["input_schema"]["$schema"] = dialect
            with self.subTest(dialect=dialect), self.assertRaises(meshy.ConfigError):
                meshy.validate_config(config)

    def test_invalid_templates_and_ids(self):
        for change in ("duplicate", "undeclared", "invalid"):
            config = configured()
            if change == "duplicate":
                config["recipes"].append(copy.deepcopy(config["recipes"][0]))
            else:
                config["recipes"][0]["prompt_template"] = "$other" if change == "undeclared" else "${"
            with self.subTest(change=change), self.assertRaises(meshy.ConfigError):
                meshy.validate_config(config)

    def test_cli_dry_run_does_not_modify_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "meshy.json"
            path.write_text(json.dumps(configured()))
            before = path.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT / "scripts/meshy_config.py"), "resolve",
                                     str(path), "--operation", "mesh", "--template", "prop",
                                     "--variables", '{"subject":"rock"}'], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(json.loads(result.stdout)["submission_performed"])
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(tmp).iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
