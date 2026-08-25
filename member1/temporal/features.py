from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class VariableTemporalFeatures:
    """Temporal statistical features for a single weather observation variable."""
    rolling_mean: Optional[float] = None
    rolling_std: Optional[float] = None
    rolling_z: Optional[float] = None
    rate_of_change: Optional[float] = None
    persistence_count: Optional[int] = None
    flatline_duration: Optional[float] = None
    drift_slope: Optional[float] = None
    baseline_deviation: Optional[float] = None

@dataclass(frozen=True)
class TemporalFeatures:
    """Temporal statistical features across all target observation variables."""
    station_id: str
    timestamp: str
    insufficient_history: bool
    temperature_c: VariableTemporalFeatures
    relative_humidity_pct: VariableTemporalFeatures
    pressure_hpa: VariableTemporalFeatures
