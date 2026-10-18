#!/usr/bin/env python3
"""Validate and resolve local Meshy recipes; never contact a provider."""

import argparse
import copy
import json
import math
import re
import sys
from pathlib import Path
from string import Template


class ConfigError(ValueError):
    pass


DEFERRED = re.compile(r"(?:^|[_\W])(?:auto[_-]?)?rig(?:ging)?(?:$|[_\W])|animat", re.IGNORECASE)
SECRET_KEYS = {"apikey", "accesstoken", "refreshtoken", "authorization", "password",
               "secret", "clientsecret", "credentials", "credential", "bearertoken", "token"}


def require(condition, message):
    if not condition:
        raise ConfigError(message)


def no_credentials(value, path="config"):
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = re.sub(r"[^a-z0-9]", "", key.lower())
            require(normalized not in SECRET_KEYS, f"{path}: credential fields are forbidden")
            no_credentials(child, f"{path}.{key}")
    elif isinstance(value, list):
        for child in value:
            no_credentials(child, path)
    elif isinstance(value, float):
        require(math.isfinite(value), f"{path}: non-finite numbers are forbidden")


def object_keys(value, allowed, path, required=()):
    require(isinstance(value, dict), f"{path} must be an object")
    require(not set(value) - set(allowed), f"{path} has unknown fields")
    require(set(required) <= set(value), f"{path} is missing required fields")


def text(value, path, empty=False):
    require(isinstance(value, str) and (empty or bool(value.strip())), f"{path} must be a string")


def validator_for(schema):
    try:
        import jsonschema
    except ImportError as exc:
        raise ConfigError("Configured snapshots require the jsonschema Python package") from exc
    # Snapshot validation is offline: remote and local references are not resolved.
    def check_refs(value):
        if isinstance(value, dict):
            require(not ({"$ref", "$dynamicRef", "$recursiveRef"} & set(value)),
                    "Snapshot references must be expanded locally before configuration")
            for child in value.values():
                check_refs(child)
        elif isinstance(value, list):
            for child in value:
                check_refs(child)
    check_refs(schema)
    try:
        if "$schema" in schema:
            require(isinstance(schema["$schema"], str), "Snapshot $schema must be a recognized dialect string")
            cls = jsonschema.validators.validator_for(schema, default=None)
            require(cls is not None, "Unknown JSON Schema dialect")
        else:
            cls = jsonschema.Draft202012Validator
        cls.check_schema(schema)
        return cls(schema, format_checker=cls.FORMAT_CHECKER)
    except jsonschema.exceptions.SchemaError as exc:
        raise ConfigError("Invalid input_schema snapshot") from exc


def validate_config(config):
    object_keys(config, {"version", "status", "operation_defaults", "schema_snapshots", "recipes"},
                "config", {"version", "status", "operation_defaults", "schema_snapshots", "recipes"})
    require(type(config["version"]) is int and config["version"] == 1, "Unsupported config version")
    require(config["status"] in ("draft", "ready"), "status must be draft or ready")
    no_credentials(config)
    defaults, snapshots = config["operation_defaults"], config["schema_snapshots"]
    require(isinstance(defaults, dict) and isinstance(snapshots, dict), "Operation maps must be objects")
    for operation, entry in defaults.items():
        text(operation, "operation")
        object_keys(entry, {"settings"}, "operation default", {"settings"})
        require(isinstance(entry["settings"], dict), "Default settings must be an object")
    for operation, snapshot in snapshots.items():
        text(operation, "operation")
        object_keys(snapshot, {"tool", "captured_at", "input_schema", "prompt_field"},
                    "snapshot", {"tool", "captured_at", "input_schema", "prompt_field"})
        text(snapshot["tool"], "snapshot.tool")
        text(snapshot["captured_at"], "snapshot.captured_at")
        require(snapshot["prompt_field"] is None or isinstance(snapshot["prompt_field"], str)
                and snapshot["prompt_field"].strip(), "prompt_field must be a nonempty string or null")
        require(isinstance(snapshot["input_schema"], dict), "input_schema must be an object")
        require(snapshot["input_schema"].get("type") == "object", "input_schema must describe an object")
        validator_for(snapshot["input_schema"])
    require(isinstance(config["recipes"], list), "recipes must be a list")
    ids = set()
    for recipe in config["recipes"]:
        object_keys(recipe, {"id", "operation", "criteria", "priority", "prompt_template", "variables",
                             "settings", "category", "tags"}, "recipe",
                    {"id", "operation", "criteria", "priority", "prompt_template", "variables", "settings"})
        for field in ("id", "operation", "criteria"):
            text(recipe[field], f"recipe.{field}")
        require(recipe["id"] not in ids, "Duplicate recipe ID")
        ids.add(recipe["id"])
        require(type(recipe["priority"]) is int, "priority must be an integer")
        text(recipe["prompt_template"], "prompt_template", empty=True)
        require(isinstance(recipe["settings"], dict), "Recipe settings must be an object")
        variables = recipe["variables"]
        require(isinstance(variables, list) and all(isinstance(v, str) and re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", v)
                for v in variables), "variables must list valid placeholder names")
        require(len(set(variables)) == len(variables), "Duplicate variable declaration")
        template = Template(recipe["prompt_template"])
        try:
            template.substitute({v: "" for v in variables})
        except (KeyError, ValueError) as exc:
            raise ConfigError("Invalid template or undeclared placeholder") from exc
        if "category" in recipe:
            text(recipe["category"], "recipe.category")
        if "tags" in recipe:
            require(isinstance(recipe["tags"], list) and all(isinstance(t, str) for t in recipe["tags"]),
                    "tags must be a string list")
        if config["status"] == "ready":
            require(recipe["operation"] in snapshots, "Ready recipe requires operation schema snapshot")
    if config["status"] == "ready":
        require(bool(config["recipes"]), "Ready config requires at least one recipe")
        require(set(defaults) <= set(snapshots), "Ready defaults require operation snapshots")
    return config


def resolve(config, operation, matches=(), template_id=None, variables=None, overrides=None):
    validate_config(config)
    require(config["status"] == "ready", "Draft config cannot resolve an operation")
    require(operation in config["schema_snapshots"], "Missing operation schema snapshot")
    snapshot = config["schema_snapshots"][operation]
    require(not DEFERRED.search(operation) and not DEFERRED.search(snapshot["tool"]),
            "Meshy rigging and animation are deferred by current policy")
    require(not (matches and template_id), "Choose explicit template or criteria matches, not both")
    recipes = {r["id"]: r for r in config["recipes"]}
    selected = [template_id] if template_id is not None else list(matches)
    require(bool(selected), "Pass an explicit template or evaluated matching recipe IDs")
    require(len(set(selected)) == len(selected), "Duplicate match IDs")
    require(all(r in recipes for r in selected), "Unknown recipe ID")
    require(all(recipes[r]["operation"] == operation for r in selected), "Recipe operation mismatch")
    candidates = [recipes[r] for r in selected]
    best = max(r["priority"] for r in candidates)
    winners = [r for r in candidates if r["priority"] == best]
    require(len(winners) == 1, "Ambiguous highest-priority recipes; select --template explicitly")
    recipe = winners[0]
    variables = {} if variables is None else variables
    overrides = {} if overrides is None else overrides
    require(isinstance(variables, dict) and isinstance(overrides, dict), "Variables and overrides must be objects")
    no_credentials(variables, "variables")
    no_credentials(overrides, "overrides")
    require(set(variables) == set(recipe["variables"]), "Missing or unknown template variables")
    require(all(isinstance(v, str) for v in variables.values()), "Variable values must be strings")
    prompt = Template(recipe["prompt_template"]).substitute(variables)
    settings = copy.deepcopy(config["operation_defaults"].get(operation, {}).get("settings", {}))
    settings.update(copy.deepcopy(recipe["settings"]))
    settings.update(copy.deepcopy(overrides))
    arguments = copy.deepcopy(settings)
    prompt_field = snapshot["prompt_field"]
    if prompt_field is not None:
        require(prompt_field not in settings, "Set prompt through template variables, not settings")
        arguments[prompt_field] = prompt
    else:
        require(not prompt, "Nonempty template requires an explicit prompt_field")
    schema = snapshot["input_schema"]
    # Even permissive snapshots cannot silently authorize guessed tool parameters.
    require(set(arguments) <= set(schema.get("properties", {})), "Unknown operation settings")
    errors = list(validator_for(schema).iter_errors(arguments))
    require(not errors, "Resolved arguments do not satisfy the cached MCP input schema")
    return {"version": 1, "operation": operation, "template_id": recipe["id"],
            "tool": snapshot["tool"], "prompt": prompt, "settings": settings, "arguments": arguments,
            "schema_captured_at": snapshot["captured_at"], "runtime_schema_validation_required": True,
            "submission_performed": False, "allowance_policy": ".gameflow/AUTOPILOT.md"}


def load_json(value):
    def unique_object(pairs):
        result = {}
        for key, item in pairs:
            require(key not in result, "Duplicate JSON object key")
            result[key] = item
        return result

    def reject_constant(_):
        raise ConfigError("Non-finite JSON numbers are forbidden")

    def finite_float(value):
        result = float(value)
        require(math.isfinite(result), "Non-finite JSON numbers are forbidden")
        return result

    try:
        return json.loads(value, object_pairs_hook=unique_object, parse_constant=reject_constant,
                          parse_float=finite_float)
    except json.JSONDecodeError as exc:
        raise ConfigError("Invalid JSON") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("validate")
    check.add_argument("config", type=Path)
    render = commands.add_parser("resolve", help="Render and validate locally; never submits")
    render.add_argument("config", type=Path)
    render.add_argument("--operation", required=True)
    group = render.add_mutually_exclusive_group(required=True)
    group.add_argument("--match", action="append", default=[])
    group.add_argument("--template")
    render.add_argument("--variables", default="{}")
    render.add_argument("--overrides", default="{}")
    args = parser.parse_args(argv)
    try:
        config = load_json(args.config.read_text(encoding="utf-8"))
        if args.command == "validate":
            validate_config(config)
            output = {"valid": True, "status": config["status"], "submission_performed": False}
        else:
            output = resolve(config, args.operation, args.match, args.template,
                             load_json(args.variables), load_json(args.overrides))
        print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (ConfigError, OSError) as exc:
        print(f"Meshy config error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
