from typing import Dict, List, Optional
from member1.schema.observation import Observation
from member1.temporal.history import StationHistory

class TemporalStore:
    """
    Multi-station registry and temporal state manager.
    """
    def __init__(self, max_history_per_station: int = 100) -> None:
        if max_history_per_station <= 0:
            raise ValueError("max_history_per_station must be greater than 0")
        self._max_history: int = max_history_per_station
        self._stations: Dict[str, StationHistory] = {}

    def get_or_create_history(self, station_id: str) -> StationHistory:
        """
        Retrieves existing StationHistory for station_id or initializes a new one.
        """
        if station_id not in self._stations:
            self._stations[station_id] = StationHistory(station_id, max_history=self._max_history)
        return self._stations[station_id]

    def add_observation(self, obs: Observation) -> StationHistory:
        """
        Adds observation to corresponding station's history and returns updated StationHistory.
        """
        history = self.get_or_create_history(obs.station_id)
        history.add_observation(obs)
        return history

    def get_history(self, station_id: str) -> Optional[StationHistory]:
        """
        Returns StationHistory for station_id or None if unrecorded.
        """
        return self._stations.get(station_id)

    def clear(self) -> None:
        """
        Clears all station histories.
        """
        self._stations.clear()

    def __len__(self) -> int:
        return len(self._stations)
