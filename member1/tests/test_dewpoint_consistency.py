import pytest
from member1.schema.observation import Observation
from member1.crossvar.consistency import compute_dewpoint, check_dewpoint_consistency

def test_compute_dewpoint_numerical_accuracy():
    # Benchmark check with MAGNUS_A=17.625, MAGNUS_B=243.04: T=20°C, RH=50% -> Dewpoint ≈ 9.26°C
    dp = compute_dewpoint(20.0, 50.0)
    assert round(dp, 2) == 9.26

def test_dewpoint_consistency_valid_normal():
    obs = Observation(
        station_id="ST_001",
        timestamp="2026-08-25T12:00:00Z",
        temperature_c=25.0,
        relative_humidity_pct=60.0,
        pressure_hpa=1013.25,
        is_valid=True
    )
    flagged, note = check_dewpoint_consistency(obs)
    assert not flagged
    assert note is None

def test_dewpoint_consistency_saturation_boundary():
    # At RH=100%, Dewpoint == Temp (10°C == 10°C), which is <= 10.5°C threshold
    obs = Observation(
        station_id="ST_001",
        timestamp="2026-08-25T12:00:00Z",
        temperature_c=10.0,
        relative_humidity_pct=100.0,
        pressure_hpa=1013.25,
        is_valid=True
    )
    flagged, note = check_dewpoint_consistency(obs)
    assert not flagged
    assert note is None

def test_dewpoint_invalid_rh_handling():
    # Negative/out of bound RH must raise ValueError without returning magic numbers (-999.0)
    with pytest.raises(ValueError):
        compute_dewpoint(20.0, -5.0)

    # Observations marked invalid by Phase 2 should skip consistency check safely
    obs_invalid = Observation(
        station_id="ST_001",
        timestamp="2026-08-25T12:00:00Z",
        temperature_c=20.0,
        relative_humidity_pct=-5.0,
        pressure_hpa=1013.25,
        is_valid=False
    )
    flagged, note = check_dewpoint_consistency(obs_invalid)
    assert not flagged
    assert "Skipped dewpoint check" in note

def test_dewpoint_determinism():
    obs = Observation(
        station_id="ST_001",
        timestamp="2026-08-25T12:00:00Z",
        temperature_c=22.5,
        relative_humidity_pct=55.0,
        pressure_hpa=1008.0,
        is_valid=True
    )
    res1 = check_dewpoint_consistency(obs)
    res2 = check_dewpoint_consistency(obs)
    assert res1 == res2
