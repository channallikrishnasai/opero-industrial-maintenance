#!/usr/bin/env python3
"""Validate production.json against the canonical production policy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import PRODUCTION_POLICY, validate_config  # noqa: E402


def main() -> int:
    path = ROOT / "config" / "production.json"
    try:
        with path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (OSError, json.JSONDecodeError) as exc:
        print("Production Configuration Validation\n-----------------------------------")
        print(f"configuration: FAIL ({exc})")
        print("\nRESULT: FAIL")
        return 1

    errors = validate_config(config)
    print("Production Configuration Validation")
    print("-----------------------------------")
    if not isinstance(config, dict):
        print("configuration: FAIL (expected a JSON object)")
        print("\nRESULT: FAIL")
        return 1

    labels = {
        "critical_health_threshold": "critical threshold",
        "maintenance_threshold": "maintenance threshold",
    }
    for field, expected in PRODUCTION_POLICY.items():
        actual = config.get(field, "<missing>")
        passed = actual == expected
        label = labels.get(field, field)
        print(f"{label}: {actual}  {'PASS' if passed else 'FAIL'}")
    if errors:
        for error in errors:
            print(f"  - {error}")
    print(f"\nRESULT: {'FAIL' if errors else 'PASS'}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
