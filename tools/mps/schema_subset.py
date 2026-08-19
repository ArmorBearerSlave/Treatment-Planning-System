"""Small, dependency-free validator for the JSON Schema subset used here.

This is intentionally not a general JSON Schema implementation. It evaluates
the keywords present in the committed MPS import schemas so local and CI checks
enforce those contracts without requiring a package installation.
"""

from __future__ import annotations

import json
import re
from typing import Any


def _is_type(value: Any, expected: str | list[str]) -> bool:
    if isinstance(expected, list):
        return any(_is_type(value, option) for option in expected)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    raise ValueError(f"unsupported schema type: {expected}")


def validate_json_schema(instance: Any, schema: dict[str, Any]) -> None:
    """Raise ValueError when *instance* violates the supported schema subset."""

    errors: list[str] = []

    def check(value: Any, rule: dict[str, Any], path: str) -> None:
        expected_type = rule.get("type")
        if expected_type is not None and not _is_type(value, expected_type):
            errors.append(f"{path}: expected {expected_type}, found {type(value).__name__}")
            return
        if "const" in rule and value != rule["const"]:
            errors.append(f"{path}: expected constant {rule['const']!r}, found {value!r}")
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{path}: value {value!r} is not in {rule['enum']!r}")

        if isinstance(value, dict):
            required = rule.get("required", [])
            for key in required:
                if key not in value:
                    errors.append(f"{path}: missing required property {key!r}")
            properties = rule.get("properties", {})
            if rule.get("additionalProperties") is False:
                extras = sorted(set(value) - set(properties))
                if extras:
                    errors.append(f"{path}: unexpected properties {extras!r}")
            for key, child_rule in properties.items():
                if key in value:
                    check(value[key], child_rule, f"{path}.{key}")

        if isinstance(value, list):
            if len(value) < rule.get("minItems", 0):
                errors.append(f"{path}: fewer than {rule['minItems']} items")
            if "maxItems" in rule and len(value) > rule["maxItems"]:
                errors.append(f"{path}: more than {rule['maxItems']} items")
            if rule.get("uniqueItems"):
                encoded = [json.dumps(item, sort_keys=True) for item in value]
                if len(encoded) != len(set(encoded)):
                    errors.append(f"{path}: items are not unique")
            item_rule = rule.get("items")
            if item_rule:
                for index, item in enumerate(value):
                    check(item, item_rule, f"{path}[{index}]")

        if isinstance(value, str):
            if len(value) < rule.get("minLength", 0):
                errors.append(f"{path}: shorter than {rule['minLength']} characters")
            pattern = rule.get("pattern")
            if pattern and re.search(pattern, value) is None:
                errors.append(f"{path}: does not match {pattern!r}")

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in rule and value < rule["minimum"]:
                errors.append(f"{path}: is less than {rule['minimum']}")

        for index, sub_rule in enumerate(rule.get("allOf", [])):
            check(value, sub_rule, f"{path}/allOf[{index}]")

        # Conditional application. Construction records require different fields
        # depending on their entity type, so if/then/else is part of the subset.
        if "if" in rule:
            branch = "then" if _matches(value, rule["if"]) else "else"
            if branch in rule:
                check(value, rule[branch], path)

    def _matches(value: Any, rule: dict[str, Any]) -> bool:
        probe: list[str] = []

        def probe_check(inner_value: Any, inner_rule: dict[str, Any], inner_path: str) -> None:
            saved = list(errors)
            errors.clear()
            check(inner_value, inner_rule, inner_path)
            probe.extend(errors)
            errors.clear()
            errors.extend(saved)

        probe_check(value, rule, "$")
        return not probe

    check(instance, schema, "$")
    if errors:
        raise ValueError("JSON Schema validation failed:\n- " + "\n- ".join(errors))

