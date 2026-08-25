import pytest
from dataclasses import FrozenInstanceError
from member1.evidence.contract import ObservationEvidence
from member1.validation.validator import ValidationResult
from member1.temporal.features import TemporalFeatures, VariableTemporalFeatures
from member1.crossvar.evidence import CrossVariableEvidence


def test_observation_evidence_construction():
    val = ValidationResult(is_valid=True, errors=[], warnings=[])

    tf = [
        TemporalFeatures(
            station_id="STATION_001",
            timestamp="2026-08-25T14:30:00Z",
            insufficient_history=False,
            temperature_c=VariableTemporalFeatures(rolling_mean=20.5, rolling_std=0.5, rate_of_change=0.1),
            relative_humidity_pct=VariableTemporalFeatures(rolling_mean=65.0, rolling_std=1.2, rate_of_change=-0.2),
            pressure_hpa=VariableTemporalFeatures(rolling_mean=1013.25, rolling_std=0.1, rate_of_change=0.0),
        )
    ]

    cv = CrossVariableEvidence(
        station_id="STATION_001",
        timestamp="2026-08-25T14:30:00Z",
        dewpoint_consistency_flag=False,
        pressure_temperature_flag=False,
        humidity_bounds_flag=False,
        notes=[],
    )

    ev = ObservationEvidence(
        station_id="STATION_001",
        timestamp="2026-08-25T14:30:00Z",
        validation=val,
        temporal_features=tf,
        cross_variable=cv,
    )

    assert ev.station_id == "STATION_001"
    assert ev.timestamp == "2026-08-25T14:30:00Z"
    assert ev.validation == val
    assert len(ev.temporal_features) == 1
    assert ev.cross_variable == cv
    assert ev.schema_version == "1.0"


def test_observation_evidence_immutability():
    val = ValidationResult(is_valid=True, errors=[], warnings=[])
    tf = []
    cv = CrossVariableEvidence(
        station_id="STATION_001",
        timestamp="2026-08-25T14:30:00Z",
        dewpoint_consistency_flag=False,
        pressure_temperature_flag=False,
        humidity_bounds_flag=False,
        notes=[],
    )

    ev = ObservationEvidence(
        station_id="STATION_001",
        timestamp="2026-08-25T14:30:00Z",
        validation=val,
        temporal_features=tf,
        cross_variable=cv,
    )

    with pytest.raises(FrozenInstanceError):
        ev.station_id = "STATION_002"


def test_observation_evidence_exact_fields():
    expected_fields = {
        "station_id",
        "timestamp",
        "validation",
        "temporal_features",
        "cross_variable",
        "schema_version",
    }
    actual_fields = set(ObservationEvidence.__dataclass_fields__.keys())
    assert actual_fields == expected_fields


def test_observation_evidence_default_schema_version():
    val = ValidationResult(is_valid=True, errors=[], warnings=[])
    tf = []
    cv = CrossVariableEvidence(
        station_id="STATION_001",
        timestamp="2026-08-25T14:30:00Z",
        dewpoint_consistency_flag=False,
        pressure_temperature_flag=False,
        humidity_bounds_flag=False,
        notes=[],
    )

    ev = ObservationEvidence(
        station_id="STATION_001",
        timestamp="2026-08-25T14:30:00Z",
        validation=val,
        temporal_features=tf,
        cross_variable=cv,
    )

    assert ev.schema_version == "1.0"
