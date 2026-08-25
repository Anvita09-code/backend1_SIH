import pytest
from member1.schema.observation import Observation
from member1.temporal.history import StationHistory
from member1.temporal.store import TemporalStore

def make_obs(station_id: str = "AWS_001", temp: float = 25.0, ts: str = "2026-08-25T12:00:00Z") -> Observation:
    return Observation(
        station_id=station_id,
        timestamp=ts,
        temperature_c=temp,
        relative_humidity_pct=50.0,
        pressure_hpa=1013.25,
        is_valid=True,
    )

def test_station_history_initialization():
    history = StationHistory(station_id="AWS_001")
    assert history.station_id == "AWS_001"
    assert len(history) == 0

def test_station_history_invalid_max_history():
    with pytest.raises(ValueError):
        StationHistory(station_id="AWS_001", max_history=0)

def test_add_observation():
    history = StationHistory(station_id="AWS_001")
    obs = make_obs()
    history.add_observation(obs)
    assert len(history) == 1

def test_station_mismatch_rejection():
    history = StationHistory(station_id="AWS_001")
    obs = make_obs(station_id="AWS_002")
    with pytest.raises(ValueError):
        history.add_observation(obs)

def test_has_sufficient_history_basic():
    history = StationHistory(station_id="AWS_001")
    assert history.has_sufficient_history(1) is False
    obs = make_obs()
    history.add_observation(obs)
    assert history.has_sufficient_history(1) is True
    assert history.has_sufficient_history(2) is False

def test_fifo_eviction():
    history = StationHistory(station_id="AWS_001", max_history=3)
    obs1 = make_obs(temp=10.0, ts="2026-08-25T12:00:00Z")
    obs2 = make_obs(temp=20.0, ts="2026-08-25T12:05:00Z")
    obs3 = make_obs(temp=30.0, ts="2026-08-25T12:10:00Z")
    obs4 = make_obs(temp=40.0, ts="2026-08-25T12:15:00Z")

    history.add_observation(obs1)
    history.add_observation(obs2)
    history.add_observation(obs3)
    assert len(history) == 3
    assert history.get_all()[0].temperature_c == 10.0

    history.add_observation(obs4)
    assert len(history) == 3
    all_obs = history.get_all()
    assert len(all_obs) == 3
    assert all_obs[0].temperature_c == 20.0
    assert all_obs[1].temperature_c == 30.0
    assert all_obs[2].temperature_c == 40.0

def test_get_recent():
    history = StationHistory(station_id="AWS_001", max_history=5)
    for i in range(5):
        history.add_observation(make_obs(temp=float(i)))
    
    recent_2 = history.get_recent(2)
    assert len(recent_2) == 2
    assert recent_2[0].temperature_c == 3.0
    assert recent_2[1].temperature_c == 4.0

    recent_10 = history.get_recent(10)
    assert len(recent_10) == 5

    assert history.get_recent(0) == []

def test_detect_gap_insufficient_history():
    history = StationHistory(station_id="AWS_001")
    assert history.detect_gap(300.0) is False
    history.add_observation(make_obs(ts="2026-08-25T12:00:00Z"))
    assert history.detect_gap(300.0) is False

def test_detect_gap_normal_interval():
    history = StationHistory(station_id="AWS_001")
    history.add_observation(make_obs(ts="2026-08-25T12:00:00Z"))
    history.add_observation(make_obs(ts="2026-08-25T12:05:00Z"))
    assert history.detect_gap(expected_interval=300.0) is False

def test_detect_gap_exceeded():
    history = StationHistory(station_id="AWS_001")
    history.add_observation(make_obs(ts="2026-08-25T12:00:00Z"))
    history.add_observation(make_obs(ts="2026-08-25T12:10:01Z"))
    assert history.detect_gap(expected_interval=600.0) is True

def test_detect_gap_invalid_timestamps():
    history = StationHistory(station_id="AWS_001")
    history.add_observation(make_obs(ts="invalid-date"))
    history.add_observation(make_obs(ts="2026-08-25T12:05:00Z"))
    assert history.detect_gap(300.0) is False

# TemporalStore Tests
def test_temporal_store_initialization():
    store = TemporalStore()
    assert len(store) == 0

def test_temporal_store_invalid_max_history():
    with pytest.raises(ValueError):
        TemporalStore(max_history_per_station=0)

def test_temporal_store_multi_station_isolation():
    store = TemporalStore(max_history_per_station=5)
    obs1 = make_obs(station_id="AWS_001", temp=20.0)
    obs2 = make_obs(station_id="AWS_002", temp=30.0)

    store.add_observation(obs1)
    store.add_observation(obs2)

    assert len(store) == 2
    
    hist1 = store.get_history("AWS_001")
    hist2 = store.get_history("AWS_002")

    assert hist1 is not None
    assert hist2 is not None
    assert len(hist1) == 1
    assert len(hist2) == 1
    assert hist1.get_all()[0].temperature_c == 20.0
    assert hist2.get_all()[0].temperature_c == 30.0

def test_temporal_store_get_unrecorded_station():
    store = TemporalStore()
    assert store.get_history("UNKNOWN") is None

def test_temporal_store_clear():
    store = TemporalStore()
    store.add_observation(make_obs(station_id="AWS_001"))
    store.add_observation(make_obs(station_id="AWS_002"))
    assert len(store) == 2
    store.clear()
    assert len(store) == 0
    assert store.get_history("AWS_001") is None
