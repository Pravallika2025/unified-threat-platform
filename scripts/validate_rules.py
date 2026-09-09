#!/usr/bin/env python3
"""Validate every YAML rule against detection-content/schemas/rule.schema.json.

Run before committing a rule:  python scripts/validate_rules.py
"""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "detection-content"
REQUIRED = {"id", "title", "severity", "logic"}
VALID_SEVERITIES = {"critical", "high", "medium", "low", "info"}
VALID_TYPES = {"threshold", "match", "sequence", "anomaly"}
VALID_OPS = {"eq", "ne", "gt", "gte", "lt", "lte", "in", "not_in", "contains", "regex"}


def validate(path: Path, rule: dict) -> list[str]:
    errors = []
    prefix = f"{path.name} [{rule.get('id', '?')}]"

    for key in REQUIRED - rule.keys():
        errors.append(f"{prefix}: missing required key '{key}'")

    if rule.get("severity") not in VALID_SEVERITIES:
        errors.append(f"{prefix}: severity must be one of {sorted(VALID_SEVERITIES)}")

    logic = rule.get("logic", {})
    if logic.get("type") not in VALID_TYPES:
        errors.append(f"{prefix}: logic.type must be one of {sorted(VALID_TYPES)}")

    if logic.get("type") == "threshold":
        if not logic.get("count"):
            errors.append(f"{prefix}: threshold rules need a 'count'")
        window = str(logic.get("window", ""))
        if not window or window[-1] not in "smhd":
            errors.append(f"{prefix}: window must look like '5m', '1h', '30s'")

    for condition in logic.get("where", []) or []:
        if condition.get("op") not in VALID_OPS:
            errors.append(f"{prefix}: unknown operator '{condition.get('op')}'")
        if not condition.get("field"):
            errors.append(f"{prefix}: a condition is missing 'field'")

    return errors


def main() -> int:
    rules_dir = CONTENT / "rules"
    if not rules_dir.exists():
        print(f"No rules directory at {rules_dir}")
        return 1

    all_errors: list[str] = []
    seen_ids: dict[str, str] = {}
    count = 0

    for path in sorted(rules_dir.rglob("*.yml")):
        with path.open() as fh:
            for rule in yaml.safe_load_all(fh):
                if not rule:
                    continue
                count += 1
                all_errors.extend(validate(path, rule))
                rule_id = rule.get("id")
                if rule_id in seen_ids:
                    all_errors.append(f"Duplicate rule id '{rule_id}' ({seen_ids[rule_id]})")
                elif rule_id:
                    seen_ids[rule_id] = path.name

    schema_path = CONTENT / "schemas" / "rule.schema.json"
    if schema_path.exists():
        json.loads(schema_path.read_text())  # fail loudly if the schema itself is broken

    if all_errors:
        print(f"{len(all_errors)} problem(s) found in {count} rules:\n")
        for error in all_errors:
            print(f"  - {error}")
        return 1

    print(f"All {count} rules valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
