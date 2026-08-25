import pytest
import math
from member1.schema.observation import Observation
from member1.temporal.history import StationHistory
from member1.temporal.stats import (
    compute_rolling_mean,
    compute_rolling_std,
    compute_z_score,
    compute_rate_of_change,
)
from member1.temporal.analytics import TemporalAnalyticsEngine

def test_compute_rolling_mean_basic():
    assert compute_rolling_mean([10.0, 20.0, 30.0]) == 20.0
    assert compute_rolling_mean([]) is None

def test_compute_rolling_std_basic():
    vals = [10.0, 12.0, 23.0, 23.0, 16.0, 23.0, 21.0, 16.0]
    std = compute_rolling_std(vals)
    assert std is not None
    assert math.isclose(std, 5.2372, abs_tol=1e-3)

def test_compute_rolling_std_zero_variance():
    vals = [15.0, 15.0, 15.0]
    assert compute_rolling_std(vals) == 0.0

def test_compute_z_score():
    assert compute_z_score(25.0, 20.0, 5.0) == 1.0
    assert compute_z_score(15.0, 20.0, 0.0) == 0.0
    assert compute_z_score(10.0, None, 5.0) is None

def test_compute_rate_of_change():
    assert compute_rate_of_change(25.0, 20.0, 300.0) == (5.0 / 300.0)
    assert compute_rate_of_change(25.0, 20.0, 0.0) is None

def test_analytics_engine_rolling_stats_integration():
    engine = TemporalAnalyticsEngine(window_size=3, min_history_required=3)
    history = StationHistory("AWS_001")
    
    timestamps = [
        "2026-08-25T12:00:00Z",
        "2026-08-25T12:05:00Z",
        "2026-08-25T12:10:00Z",
    ]
    temps = [20.0, 22.0, 24.0]

    for ts, temp in zip(timestamps, temps):
        obs = Observation(
            station_id="AWS_001",
            timestamp=ts,
            temperature_c=temp,
            relative_humidity_pct=50.0,
            pressure_hpa=1013.25,
            is_valid=True,
        )
        history.add_observation(obs)

    tf = engine.compute_features(history, obs)
    assert tf.insufficient_history is False
    assert tf.temperature_c.rolling_mean == 22.0
    assert math.isclose(tf.temperature_c.rolling_std, 2.0, abs_tol=1e-5)
    assert tf.temperature_c.rolling_z == 1.0
    assert math.isclose(tf.temperature_c.rate_of_change, 2.0 / 300.0, abs_tol=1e-7)
