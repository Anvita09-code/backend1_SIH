import pytest
from dataclasses import FrozenInstanceError, fields
from member1.schema.observation import Observation

def test_observation_construction():
    obs = Observation(
        station_id="AWS_001",
        timestamp="2026-08-25T12:00:00Z",
        temperature_c=25.5,
        relative_humidity_pct=65.0,
        pressure_hpa=1013.25
    )
    assert obs.station_id == "AWS_001"
    assert obs.timestamp == "2026-08-25T12:00:00Z"
    assert obs.temperature_c == 25.5
    assert obs.relative_humidity_pct == 65.0
    assert obs.pressure_hpa == 1013.25
    assert obs.is_valid is None

def test_observation_explicit_is_valid():
    obs_valid = Observation("AWS_001", "2026-08-25T12:00:00Z", 20.0, 50.0, 1000.0, is_valid=True)
    obs_invalid = Observation("AWS_001", "2026-08-25T12:00:00Z", 20.0, 50.0, 1000.0, is_valid=False)
    assert obs_valid.is_valid is True
    assert obs_invalid.is_valid is False

def test_observation_immutability():
    obs = Observation("AWS_001", "2026-08-25T12:00:00Z", 20.0, 50.0, 1000.0)
    with pytest.raises(FrozenInstanceError):
        obs.temperature_c = 30.0

def test_observation_exact_fields():
    expected_fields = [
        "station_id",
        "timestamp",
        "temperature_c",
        "relative_humidity_pct",
        "pressure_hpa",
        "is_valid"
    ]
    actual_fields = [f.name for f in fields(Observation)]
    assert actual_fields == expected_fields
