import pytest
from member1.schema.observation import Observation
from member1.validation.validator import validate, ValidationResult
from member1.fixtures.loader import load_fixture

def test_validation_result_construction():
    obs = Observation("AWS_001", "2026-01-01T00:00:00Z", 20.0, 50.0, 1010.0, True)
    res = ValidationResult(True, [], [], obs)
    assert res.is_valid is True
    assert res.errors == []
    assert res.warnings == []
    assert res.normalized_observation == obs

def test_validate_non_dict_input():
    for malformed in [None, "string", 123, [1, 2, 3], (1, 2)]:
        res = validate(malformed)
        assert isinstance(res, ValidationResult)
        assert res.is_valid is False
        assert "malformed_input:input_must_be_dict" in res.errors
        assert res.normalized_observation is not None
        assert res.normalized_observation.is_valid is False

def test_validate_normal_observation_fixture():
    data = load_fixture("normal_observation")
    assert len(data) == 1
    res = validate(data[0])
    assert res.is_valid is True
    assert res.errors == []
    assert res.normalized_observation is not None
    assert res.normalized_observation.temperature_c == 24.5

def test_validate_invalid_observation_fixture():
    data = load_fixture("invalid_observation")
    assert len(data) == 1
    res = validate(data[0])
    assert res.is_valid is False
    assert "invalid_timestamp:format" in res.errors
    assert any(err.startswith("out_of_physical_range:temperature_c") for err in res.errors)
    assert any(err.startswith("out_of_physical_range:relative_humidity_pct") for err in res.errors)
    assert any(err.startswith("invalid_type:pressure_hpa") for err in res.errors)

def test_validate_missing_observation_fixture():
    data = load_fixture("missing_observation")
    assert len(data) == 1
    res = validate(data[0])
    assert res.is_valid is False
    assert any("missing_field:" in err for err in res.errors)
