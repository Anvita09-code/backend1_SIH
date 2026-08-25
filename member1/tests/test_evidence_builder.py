from datetime import datetime, timezone
import pytest
from member1.evidence.builder import build_observation_evidence
from member1.evidence.contract import ObservationEvidence


def test_build_observation_evidence_basic():
    now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    obs = {
        "station_id": "STATION_001",
        "timestamp": now_str,
        "temperature_c": 22.5,
        "relative_humidity_pct": 55.0,
        "pressure_hpa": 1013.25,
    }

    ev = build_observation_evidence(obs)

    assert isinstance(ev, ObservationEvidence)
    assert ev.station_id == "STATION_001"
    assert ev.timestamp == now_str
    assert ev.validation.is_valid is True
    assert len(ev.temporal_features) == 1
    assert ev.cross_variable.station_id == "STATION_001"
    assert ev.schema_version == "1.0"


def test_build_observation_evidence_invalid_obs():
    now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    obs = {
        "station_id": "STATION_001",
        "timestamp": now_str,
        "temperature_c": -150.0,
        "relative_humidity_pct": 55.0,
        "pressure_hpa": 1013.25,
    }

    ev = build_observation_evidence(obs)

    assert isinstance(ev, ObservationEvidence)
    assert ev.validation.is_valid is False
    assert len(ev.validation.errors) > 0
