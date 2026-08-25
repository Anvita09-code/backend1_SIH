import pytest
from member1.config.calibration import CalibrationRegistry
from member1.fixtures.loader import load_fixture

def test_all_modules_import():
    """Verify foundation modules import and instantiate cleanly."""
    registry = CalibrationRegistry()
    assert registry is not None

@pytest.mark.parametrize("fixture_name", [
    "normal_observation",
    "spike",
    "flatline",
    "drift",
    "bias",
    "noise",
    "missing_observation",
    "invalid_observation",
    "insufficient_history",
    "timestamp_gap",
])
def test_load_fixture_for_each_case(fixture_name):
    """Verify each required fixture loads without error and returns a list."""
    data = load_fixture(fixture_name)
    assert isinstance(data, list)
