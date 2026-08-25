import pytest
from member1.schema.observation import Observation
from member1.temporal.history import StationHistory
from member1.temporal.stats import compute_persistence_and_flatline
from member1.temporal.analytics import TemporalAnalyticsEngine

def test_compute_persistence_and_flatline_single_obs():
    obs = Observation("AWS_001", "2026-08-25T12:00:00Z", 20.0, 50.0, 1013.25)
    count, dur = compute_persistence_and_flatline([obs], "temperature_c")
    assert count == 1
    assert dur == 0.0

def test_compute_persistence_and_flatline_consecutive_identical():
    obs1 = Observation("AWS_001", "2026-08-25T12:00:00Z", 20.0, 50.0, 1013.25)
    obs2 = Observation("AWS_001", "2026-08-25T12:05:00Z", 20.0, 50.0, 1013.25)
    obs3 = Observation("AWS_001", "2026-08-25T12:10:00Z", 20.0, 50.0, 1013.25)

    count, dur = compute_persistence_and_flatline([obs1, obs2, obs3], "temperature_c")
    assert count == 3
    assert dur == 600.0  # 10 minutes = 600s

def test_compute_persistence_break():
    obs1 = Observation("AWS_001", "2026-08-25T12:00:00Z", 20.0, 50.0, 1013.25)
    obs2 = Observation("AWS_001", "2026-08-25T12:05:00Z", 25.0, 50.0, 1013.25)
    obs3 = Observation("AWS_001", "2026-08-25T12:10:00Z", 25.0, 50.0, 1013.25)

    count, dur = compute_persistence_and_flatline([obs1, obs2, obs3], "temperature_c")
    assert count == 2
    assert dur == 300.0  # 5 minutes = 300s

def test_analytics_engine_flatline_fixture():
    engine = TemporalAnalyticsEngine(min_history_required=3)
    history = StationHistory("AWS_001")
    
    timestamps = [
        "2026-08-25T12:00:00Z",
        "2026-08-25T12:05:00Z",
        "2026-08-25T12:10:00Z",
    ]
    for ts in timestamps:
        obs = Observation("AWS_001", ts, 22.5, 50.0, 1013.25)
        history.add_observation(obs)

    tf = engine.compute_features(history, obs)
    assert tf.temperature_c.persistence_count == 3
    assert tf.temperature_c.flatline_duration == 600.0
