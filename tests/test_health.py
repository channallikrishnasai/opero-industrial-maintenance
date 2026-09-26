from app.models import HealthClassification, Machine, MachineStatus
from app.services.health_service import classify_health


def machine(score):
    return Machine("TEST", "Test machine", "Test bay", 60.0, 1.0, score, MachineStatus.RUNNING)


def test_health_classification_boundaries():
    assert classify_health(machine(61)) == HealthClassification.HEALTHY
    assert classify_health(machine(60)) == HealthClassification.MAINTENANCE_REQUIRED
    assert classify_health(machine(30)) == HealthClassification.CRITICAL
