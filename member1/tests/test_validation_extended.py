import pytest
from member1.schema.observation import Observation
from member1.validation.validator import validate, ValidationResult
from member1.fixtures.loader import load_fixture

# -------------------------------------------------------------------
# 1. Missing Field Validation (missing_field:<field_name>)
# -------------------------------------------------------------------
@pytest.mark.parametrize("missing_field", [
    "station_id",
    "timestamp",
    "temperature_c",
    "relative_humidity_pct",
    "pressure_hpa"
])
def test_validate_missing_required_fields(missing_field):
    payload = {
        "station_id": "AWS_001",
        "timestamp": "2026-01-01T00:00:00Z",
        "temperature_c": 20.0,
        "relative_humidity_pct": 50.0,
        "pressure_hpa": 1010.0
    }
    del payload[missing_field]
    res = validate(payload)
    assert res.is_valid is False
    assert any(f"missing_field:{missing_field}" in err for err in res.errors)

# -------------------------------------------------------------------
# 2. Both-Boundary Physical Range Tests
# -------------------------------------------------------------------
def test_validate_temperature_below_min():
    payload = {"station_id": "AWS_001", "timestamp": "2026-01-01T00:00:00Z", "temperature_c": -95.0, "relative_humidity_pct": 50.0, "pressure_hpa": 1010.0}
    res = validate(payload)
    assert res.is_valid is False

def test_validate_temperature_above_max():
    payload = {"station_id": "AWS_001", "timestamp": "2026-01-01T00:00:00Z", "temperature_c": 65.0, "relative_humidity_pct": 50.0, "pressure_hpa": 1010.0}
    res = validate(payload)
    assert res.is_valid is False

def test_validate_humidity_below_min():
    payload = {"station_id": "AWS_001", "timestamp": "2026-01-01T00:00:00Z", "temperature_c": 20.0, "relative_humidity_pct": -5.0, "pressure_hpa": 1010.0}
    res = validate(payload)
    assert res.is_valid is False

def test_validate_humidity_above_max():
    payload = {"station_id": "AWS_001", "timestamp": "2026-01-01T00:00:00Z", "temperature_c": 20.0, "relative_humidity_pct": 105.0, "pressure_hpa": 1010.0}
    res = validate(payload)
    assert res.is_valid is False

def test_validate_pressure_below_min():
    payload = {"station_id": "AWS_001", "timestamp": "2026-01-01T00:00:00Z", "temperature_c": 20.0, "relative_humidity_pct": 50.0, "pressure_hpa": 250.0}
    res = validate(payload)
    assert res.is_valid is False

def test_validate_pressure_above_max():
    payload = {"station_id": "AWS_001", "timestamp": "2026-01-01T00:00:00Z", "temperature_c": 20.0, "relative_humidity_pct": 50.0, "pressure_hpa": 1200.0}
    res = validate(payload)
    assert res.is_valid is False

# -------------------------------------------------------------------
# 3. Timestamps: Malformed & Future Boundaries
# -------------------------------------------------------------------
def test_validate_malformed_timestamp():
    payload = {"station_id": "AWS_001", "timestamp": "invalid-iso-date", "temperature_c": 20.0, "relative_humidity_pct": 50.0, "pressure_hpa": 1010.0}
    res = validate(payload)
    assert res.is_valid is False

def test_validate_far_future_timestamp():
    payload = {"station_id": "AWS_001", "timestamp": "2099-01-01T00:00:00Z", "temperature_c": 20.0, "relative_humidity_pct": 50.0, "pressure_hpa": 1010.0}
    res = validate(payload)
    assert res.is_valid is False

# -------------------------------------------------------------------
# 4. Top-Level Malformed Inputs (Non-Dict)
# -------------------------------------------------------------------
@pytest.mark.parametrize("bad_input", [
    None,
    "invalid string",
    12345,
    [{"station_id": "AWS_001"}],
    ("tuple", "data")
])
def test_validate_malformed_top_level_inputs(bad_input):
    res = validate(bad_input)
    assert isinstance(res, ValidationResult)
    assert res.is_valid is False
    assert len(res.errors) > 0

# -------------------------------------------------------------------
# 5. Determinism & Full Fixture Audit across all 10 files
# -------------------------------------------------------------------
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
    "timestamp_gap"
])
def test_validate_all_fixtures_without_exceptions(fixture_name):
    data = load_fixture(fixture_name)
    assert isinstance(data, list)
    for sample in data:
        res = validate(sample)
        assert isinstance(res, ValidationResult)

def test_validate_determinism():
    payload = {
        "station_id": "AWS_001",
        "timestamp": "2026-01-01T00:00:00Z",
        "temperature_c": 24.5,
        "relative_humidity_pct": 55.0,
        "pressure_hpa": 1013.25
    }
    res1 = validate(payload)
    res2 = validate(payload)
    assert res1.is_valid == res2.is_valid
    assert res1.errors == res2.errors
    assert res1.warnings == res2.warnings
    assert res1.normalized_observation == res2.normalized_observation
