import pytest
from member1.schema.observation import Observation
from member1.temporal.history import StationHistory
from member1.temporal.features import TemporalFeatures, VariableTemporalFeatures
from member1.temporal.analytics import TemporalAnalyticsEngine

def make_obs(station_id="AWS_001", temp=25.0, ts="2026-08-25T12:00:00Z") -> Observation:
    return Observation(
        station_id=station_id,
        timestamp=ts,
        temperature_c=temp,
        relative_humidity_pct=50.0,
        pressure_hpa=1013.25,
        is_valid=True,
    )

def test_variable_temporal_features_defaults():
    vf = VariableTemporalFeatures()
    assert vf.rolling_mean is None
    assert vf.rolling_std is None
    assert vf.rolling_z is None
    assert vf.rate_of_change is None
    assert vf.persistence_count is None
    assert vf.flatline_duration is None
    assert vf.drift_slope is None
    assert vf.baseline_deviation is None

def test_temporal_features_contract_immutability():
    vf = VariableTemporalFeatures(rolling_mean=20.0)
    tf = TemporalFeatures(
        station_id="AWS_001",
        timestamp="2026-08-25T12:00:00Z",
        insufficient_history=False,
        temperature_c=vf,
        relative_humidity_pct=vf,
        pressure_hpa=vf,
    )
    assert tf.station_id == "AWS_001"
    assert tf.insufficient_history is False
    with pytest.raises(AttributeError):
        tf.station_id = "AWS_002"

def test_analytics_engine_insufficient_history_branch():
    engine = TemporalAnalyticsEngine(min_history_required=3)
    history = StationHistory("AWS_001")
    obs = make_obs()
    history.add_observation(obs)

    tf = engine.compute_features(history, obs)
    assert tf.insufficient_history is True
    assert tf.temperature_c.rolling_mean is None

def test_analytics_engine_sufficient_history_branch():
    engine = TemporalAnalyticsEngine(min_history_required=2)
    history = StationHistory("AWS_001")
    obs1 = make_obs(ts="2026-08-25T12:00:00Z")
    obs2 = make_obs(ts="2026-08-25T12:05:00Z")
    history.add_observation(obs1)
    history.add_observation(obs2)

    tf = engine.compute_features(history, obs2)
    assert tf.insufficient_history is False
