from datetime import datetime
from typing import List, Optional

from member1.schema.observation import Observation
from member1.temporal.history import StationHistory
from member1.temporal.features import TemporalFeatures, VariableTemporalFeatures
from member1.temporal.stats import (
    compute_rolling_mean,
    compute_rolling_std,
    compute_z_score,
    compute_rate_of_change,
    compute_persistence_and_flatline,
)

class TemporalAnalyticsEngine:
    """Computes deterministic temporal statistical features from station observation history."""

    def __init__(self, window_size: int = 12, min_history_required: int = 3, persistence_epsilon: float = 1e-4):
        self.window_size = window_size
        self.min_history_required = min_history_required
        self.persistence_epsilon = persistence_epsilon

    def _parse_iso(self, ts: str) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            return None

    def _compute_var_features(
        self,
        history_obs: List[Observation],
        current_obs: Observation,
        var_name: str
    ) -> VariableTemporalFeatures:
        current_val = getattr(current_obs, var_name, None)
        if current_val is None:
            return VariableTemporalFeatures()

        recent = history_obs[-self.window_size:]
        vals = [getattr(o, var_name) for o in recent if getattr(o, var_name, None) is not None]

        mean = compute_rolling_mean(vals)
        std = compute_rolling_std(vals) if len(vals) > 1 else 0.0
        z_score = compute_z_score(current_val, mean, std)

        roc = None
        if len(history_obs) >= 2:
            prev_obs = history_obs[-2]
            prev_val = getattr(prev_obs, var_name, None)
            if prev_val is not None:
                t_curr = self._parse_iso(current_obs.timestamp)
                t_prev = self._parse_iso(prev_obs.timestamp)
                if t_curr and t_prev:
                    dt = (t_curr - t_prev).total_seconds()
                    roc = compute_rate_of_change(current_val, prev_val, dt)

        pers_count, flatline_dur = compute_persistence_and_flatline(
            history_obs, var_name, self.persistence_epsilon
        )

        return VariableTemporalFeatures(
            rolling_mean=mean,
            rolling_std=std,
            rolling_z=z_score,
            rate_of_change=roc,
            persistence_count=pers_count,
            flatline_duration=flatline_dur,
            drift_slope=None,
            baseline_deviation=None,
        )

    def compute_features(self, history: StationHistory, current_obs: Observation) -> TemporalFeatures:
        """Computes TemporalFeatures contract including rolling stats and persistence."""
        history_obs = history.get_all()
        
        if not history.has_sufficient_history(self.min_history_required):
            empty_var = VariableTemporalFeatures()
            return TemporalFeatures(
                station_id=current_obs.station_id,
                timestamp=current_obs.timestamp,
                insufficient_history=True,
                temperature_c=empty_var,
                relative_humidity_pct=empty_var,
                pressure_hpa=empty_var,
            )

        temp_feat = self._compute_var_features(history_obs, current_obs, "temperature_c")
        rh_feat = self._compute_var_features(history_obs, current_obs, "relative_humidity_pct")
        press_feat = self._compute_var_features(history_obs, current_obs, "pressure_hpa")

        return TemporalFeatures(
            station_id=current_obs.station_id,
            timestamp=current_obs.timestamp,
            insufficient_history=False,
            temperature_c=temp_feat,
            relative_humidity_pct=rh_feat,
            pressure_hpa=press_feat,
        )
