import json
from pathlib import Path

import pytest

from app.config import Settings, load_settings, validate_config


CONFIG_PATH = Path(__file__).parents[1] / "config" / "production.json"


def test_loader_preserves_the_intended_incident_and_baseline_thresholds():
    settings = load_settings()
    assert settings.environment == "production"
    assert settings.debug is True
    assert settings.log_level == "DEBUG"
    assert settings.critical_health_threshold == 30
    assert settings.maintenance_threshold == 60


def test_canonical_thresholds_are_accepted_by_production_policy():
    baseline = {
        "environment": "production",
        "debug": False,
        "log_level": "INFO",
        "critical_health_threshold": 30,
        "maintenance_threshold": 60,
    }
    assert validate_config(baseline) == []
    settings = Settings.from_mapping(baseline)
    assert settings.critical_health_threshold == 30
    assert settings.maintenance_threshold == 60


def test_production_validation_reports_incident_and_no_threshold_drift():
    incident = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    errors = validate_config(incident)
    assert any("debug must be False" in error for error in errors)
    assert any("log_level must be 'INFO'" in error for error in errors)
    assert not any("critical_health_threshold" in error for error in errors)
    assert not any("maintenance_threshold" in error for error in errors)


def test_production_validation_fails_while_incident_is_active():
    incident = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    assert validate_config(incident)


@pytest.mark.parametrize("change,expected", [
    ({"debug": "true"}, "debug must be bool"),
    ({"critical_health_threshold": 31}, "critical_health_threshold must be 30"),
    ({"maintenance_threshold": 61}, "maintenance_threshold must be 60"),
])
def test_invalid_types_or_threshold_drift_are_rejected(change, expected):
    config = {
        "environment": "production",
        "debug": False,
        "log_level": "INFO",
        "critical_health_threshold": 30,
        "maintenance_threshold": 60,
    }
    config.update(change)
    assert any(expected in error for error in validate_config(config))


def test_missing_field_is_reported():
    assert "missing required field: debug" in validate_config({"environment": "production"})
