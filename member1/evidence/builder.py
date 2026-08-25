from typing import Any, Optional
from member1.evidence.contract import ObservationEvidence
from member1.validation.validator import validate
from member1.temporal.features import TemporalFeatures, VariableTemporalFeatures
from member1.temporal.analytics import TemporalAnalyticsEngine
from member1.temporal.history import StationHistory
from member1.crossvar.evidence import CrossVariableEvidence
from member1.crossvar.consistency import check_dewpoint_consistency


def build_observation_evidence(
    raw_obs: Any,
    history: Optional[StationHistory] = None,
) -> ObservationEvidence:
    """Build a complete, frozen ObservationEvidence object from raw observation data and history."""
    # 1. Phase 2 Validation
    val_result = validate(raw_obs)

    station_id = ""
    timestamp = ""
    if isinstance(raw_obs, dict):
        station_id = str(raw_obs.get("station_id", ""))
        timestamp = str(raw_obs.get("timestamp", ""))

    # 2. Phase 4 Temporal Features
    if val_result.is_valid and val_result.normalized_observation is not None:
        norm_obs = val_result.normalized_observation
        station_id = norm_obs.station_id
        timestamp = norm_obs.timestamp

        if history is None:
            history = StationHistory(station_id=station_id)
        tf_obj = TemporalAnalyticsEngine().compute_features(history, norm_obs)
    else:
        empty_var = VariableTemporalFeatures()
        tf_obj = TemporalFeatures(
            station_id=station_id,
            timestamp=timestamp,
            insufficient_history=True,
            temperature_c=empty_var,
            relative_humidity_pct=empty_var,
            pressure_hpa=empty_var,
        )

    # 3. Phase 5 Cross-Variable Evidence
    if val_result.is_valid and val_result.normalized_observation is not None:
        norm_obs = val_result.normalized_observation
        dewpoint_flag, note = check_dewpoint_consistency(norm_obs)
        notes = [note] if note else []
        cv_obj = CrossVariableEvidence(
            station_id=norm_obs.station_id,
            timestamp=norm_obs.timestamp,
            dewpoint_consistency_flag=dewpoint_flag,
            pressure_temperature_flag=False,
            humidity_bounds_flag=False,
            notes=notes,
        )
    else:
        cv_obj = CrossVariableEvidence(
            station_id=station_id,
            timestamp=timestamp,
            dewpoint_consistency_flag=False,
            pressure_temperature_flag=False,
            humidity_bounds_flag=False,
            notes=["invalid_observation"],
        )

    # 4. Phase 6 Observation Evidence Contract Construction
    return ObservationEvidence(
        station_id=station_id,
        timestamp=timestamp,
        validation=val_result,
        temporal_features=[tf_obj],
        cross_variable=cv_obj,
        schema_version="1.0",
    )
