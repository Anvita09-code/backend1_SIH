from typing import List, Optional
from datetime import datetime, timezone
from member1.schema.observation import Observation

def _parse_iso_timestamp(ts: str) -> Optional[datetime]:
    """
    Parses ISO 8601 string to datetime object. Handles optional trailing 'Z'.
    """
    try:
        ts_clean = ts.rstrip("Z")
        dt = datetime.fromisoformat(ts_clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None

class StationHistory:
    """
    Per-station bounded temporal history layer.
    """
    def __init__(self, station_id: str, max_history: int = 100) -> None:
        if max_history <= 0:
            raise ValueError("max_history must be greater than 0")
        self.station_id: str = station_id
        self._max_history: int = max_history
        self._observations: List[Observation] = []

    def add_observation(self, obs: Observation) -> None:
        """
        Appends an observation to the station history, enforcing FIFO eviction if max_history is reached.
        """
        if obs.station_id != self.station_id:
            raise ValueError(f"Station ID mismatch: history belongs to '{self.station_id}', got '{obs.station_id}'")
        
        if len(self._observations) >= self._max_history:
            self._observations.pop(0)
            
        self._observations.append(obs)

    def has_sufficient_history(self, min_samples: int) -> bool:
        """
        Returns True if the stored history count meets or exceeds min_samples.
        """
        return len(self._observations) >= min_samples

    def get_recent(self, count: int) -> List[Observation]:
        """
        Returns the N most recent observations in chronological order.
        """
        if count <= 0:
            return []
        return list(self._observations[-count:])

    def get_all(self) -> List[Observation]:
        """
        Returns all stored observations in chronological order.
        """
        return list(self._observations)

    def detect_gap(self, expected_interval: float = 300.0) -> bool:
        """
        Returns True if the time elapsed between the last two observations strictly exceeds expected_interval seconds.
        Returns False if history has fewer than 2 observations or timestamps are invalid.
        """
        if len(self._observations) < 2:
            return False

        t_prev = _parse_iso_timestamp(self._observations[-2].timestamp)
        t_curr = _parse_iso_timestamp(self._observations[-1].timestamp)

        if t_prev is None or t_curr is None:
            return False

        delta_sec = (t_curr - t_prev).total_seconds()
        return delta_sec > expected_interval

    def __len__(self) -> int:
        return len(self._observations)
