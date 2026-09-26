"""Application settings loaded from the repository's production JSON file."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "production.json"
REQUIRED_FIELDS = {
    "environment": str,
    "debug": bool,
    "log_level": str,
    "critical_health_threshold": int,
    "maintenance_threshold": int,
}


@dataclass(frozen=True)
class Settings:
    environment: str
    debug: bool
    log_level: str
    critical_health_threshold: int
    maintenance_threshold: int

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "Settings":
        errors = _validate_schema(data)
        if errors:
            raise ValueError("Invalid configuration: " + "; ".join(errors))
        return cls(**{key: data[key] for key in REQUIRED_FIELDS})


def validate_config(data: Any) -> list[str]:
    """Return human-readable schema and production-safety validation errors."""
    errors = _validate_schema(data)
    if errors:
        return errors
    errors = []
    if not data["environment"].strip():
        errors.append("environment must not be empty")
    if data["log_level"] not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        errors.append("log_level must be DEBUG, INFO, WARNING, ERROR, or CRITICAL")
    if data["environment"].lower() == "production":
        if data["debug"]:
            errors.append("debug must be false in production (found true)")
        if data["log_level"] == "DEBUG":
            errors.append("log_level must not be DEBUG in production (found DEBUG)")
    critical = data["critical_health_threshold"]
    maintenance = data["maintenance_threshold"]
    if not 0 <= critical <= 100:
        errors.append("critical_health_threshold must be between 0 and 100")
    if not 0 <= maintenance <= 100:
        errors.append("maintenance_threshold must be between 0 and 100")
    if critical >= maintenance:
        errors.append("critical_health_threshold must be lower than maintenance_threshold")
    return errors


def _validate_schema(data: Any) -> list[str]:
    """Validate required fields and types without applying production policy."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["configuration must be a JSON object"]
    for field, expected in REQUIRED_FIELDS.items():
        if field not in data:
            errors.append(f"missing required field: {field}")
        elif type(data[field]) is not expected:
            errors.append(f"{field} must be {expected.__name__}")
    return errors


def load_settings(path: Path | str = CONFIG_PATH) -> Settings:
    with Path(path).open(encoding="utf-8") as config_file:
        data = json.load(config_file)
    if not isinstance(data, dict):
        raise ValueError("Invalid configuration: configuration must be a JSON object")
    return Settings.from_mapping(data)


settings = load_settings()
