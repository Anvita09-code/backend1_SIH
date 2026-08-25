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

def test_subsecond_gap_detection():
    history = StationHistory(station_id="AWS_001")
    history.add_observation(make_obs(ts="2026-08-25T12:00:00.000Z"))
    history.add_observation(make_obs(ts="2026-08-25T12:00:00.500Z"))
    # Interval is 0.5s; expected threshold is 0.4s -> should detect gap
    assert history.detect_gap(expected_interval=0.4) is True
    # Expected threshold is 1.0s -> no gap
    assert history.detect_gap(expected_interval=1.0) is False

def test_negative_time_delta_gap_detection():
    history = StationHistory(station_id="AWS_001")
    history.add_observation(make_obs(ts="2026-08-25T12:05:00Z"))
    history.add_observation(make_obs(ts="2026-08-25T12:00:00Z"))
    # Delta is negative (-300s), which does not strictly exceed expected positive interval
    assert history.detect_gap(expected_interval=300.0) is False

def test_capacity_boundary_eviction_order():
    history = StationHistory(station_id="AWS_001", max_history=1)
    history.add_observation(make_obs(temp=10.0))
    assert len(history) == 1
    assert history.get_all()[0].temperature_c == 10.0

    history.add_observation(make_obs(temp=20.0))
    assert len(history) == 1
    assert history.get_all()[0].temperature_c == 20.0

def test_temporal_store_reinitialization_after_clear():
    store = TemporalStore(max_history_per_station=10)
    store.add_observation(make_obs(station_id="AWS_001", temp=15.0))
    assert len(store) == 1
    
    store.clear()
    assert len(store) == 0

    # Ensure store can re-register station cleanly after clear
    h = store.get_or_create_history("AWS_001")
    assert len(h) == 0
    store.add_observation(make_obs(station_id="AWS_001", temp=25.0))
    assert len(store.get_history("AWS_001")) == 1

def test_high_volume_stream_simulation():
    store = TemporalStore(max_history_per_station=50)
    num_stations = 5
    obs_per_station = 100

    for i in range(obs_per_station):
        for s in range(num_stations):
            st_id = f"STATION_{s:02d}"
            obs = make_obs(station_id=st_id, temp=float(i))
            store.add_observation(obs)

    assert len(store) == num_stations
    for s in range(num_stations):
        st_id = f"STATION_{s:02d}"
        hist = store.get_history(st_id)
        assert len(hist) == 50
        # Check FIFO maintained last 50 elements (50..99)
        assert hist.get_all()[0].temperature_c == 50.0
        assert hist.get_all()[-1].temperature_c == 99.0
