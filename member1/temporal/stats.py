import math
from datetime import datetime
from typing import List, Tuple, Optional, Any

def compute_rolling_mean(values: List[float]) -> Optional[float]:
    """Computes arithmetic mean of non-None float values."""
    if not values:
        return None
    return sum(values) / len(values)

def compute_rolling_std(values: List[float], ddof: int = 1) -> Optional[float]:
    """
    Computes standard deviation of float values.
    Returns 0.0 if variance is below numerical epsilon (1e-7) or if sample size <= ddof.
    """
    if len(values) <= ddof:
        return None
    
    mean = compute_rolling_mean(values)
    if mean is None:
        return None
        
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - ddof)
    if variance < 1e-7:
        return 0.0
    return math.sqrt(variance)

def compute_z_score(val: float, mean: Optional[float], std: Optional[float]) -> Optional[float]:
    """
    Computes Z-Score: (val - mean) / std.
    Returns 0.0 if std is 0.0 or below numerical epsilon.
    """
    if mean is None or std is None:
        return None
    if std <= 1e-7:
        return 0.0
    return (val - mean) / std

def compute_rate_of_change(val_current: float, val_previous: float, dt_seconds: float) -> Optional[float]:
    """
    Computes rate of change per second: (val_current - val_previous) / dt_seconds.
    Returns None if dt_seconds is non-positive.
    """
    if dt_seconds <= 0:
        return None
    return (val_current - val_previous) / dt_seconds

def compute_persistence_and_flatline(
    history_obs: List[Any],
    var_name: str,
    epsilon: float = 1e-4
) -> Tuple[int, float]:
    """
    Computes (persistence_count, flatline_duration_seconds) for a target variable.
    Trailing consecutive observations within epsilon absolute difference are counted.
    """
    if not history_obs:
        return 0, 0.0

    current_obs = history_obs[-1]
    current_val = getattr(current_obs, var_name, None)
    if current_val is None:
        return 0, 0.0

    count = 1
    flatline_duration = 0.0
    
    def parse_iso(ts_str: str) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            return None

    end_time = parse_iso(current_obs.timestamp)
    start_time = end_time

    for i in range(len(history_obs) - 2, -1, -1):
        prev_obs = history_obs[i]
        prev_val = getattr(prev_obs, var_name, None)
        if prev_val is None:
            break

        if abs(current_val - prev_val) <= epsilon:
            count += 1
            t_prev = parse_iso(prev_obs.timestamp)
            if t_prev:
                start_time = t_prev
        else:
            break

    if start_time and end_time and count > 1:
        flatline_duration = max(0.0, (end_time - start_time).total_seconds())

    return count, flatline_duration
