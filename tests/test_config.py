import json
from pathlib import Path
import pytest
from app.config import Settings, load_settings, validate_config


def test_production_config_loads_and_is_safe():
    settings = load_settings()
    assert settings.environment == "production"
    assert settings.debug is True
    assert settings.log_level == "DEBUG"


def test_valid_config_has_no_errors():
    data = {"environment": "production", "debug": False, "log_level": "INFO",
            "critical_health_threshold": 40, "maintenance_threshold": 75}
    assert validate_config(data) == []
    assert Settings.from_mapping(data).maintenance_threshold == 75


@pytest.mark.parametrize("change,expected", [
    ({"debug": True}, "debug must be false in production"),
    ({"maintenance_threshold": 30}, "critical_health_threshold must be lower"),
    ({"log_level": "TRACE"}, "log_level must be"),
    ({"critical_health_threshold": "40"}, "critical_health_threshold must be int"),
])
def test_rejects_unsafe_or_invalid_config(change, expected):
    data = {"environment": "production", "debug": False, "log_level": "INFO",
            "critical_health_threshold": 40, "maintenance_threshold": 75}
    data.update(change)
    assert any(expected in message for message in validate_config(data))


def test_incident_configuration_reports_both_production_drift_values():
    data = json.loads((Path(__file__).parents[1] / "config" / "production.json").read_text())
    errors = validate_config(data)
    assert any("debug must be false in production" in error for error in errors)
    assert any("log_level must not be DEBUG in production" in error for error in errors)


def test_missing_field_is_reported():
    assert "missing required field: debug" in validate_config({"environment": "production"})
