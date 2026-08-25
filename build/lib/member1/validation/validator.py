from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from member1.schema.observation import Observation

PHYSICAL_LIMITS = {
    "temperature_c": (-90.0, 60.0),
    "relative_humidity_pct": (0.0, 100.0),
    "pressure_hpa": (300.0, 1100.0)
}

REQUIRED_FIELDS = ["station_id", "timestamp", "temperature_c", "relative_humidity_pct", "pressure_hpa"]

class ValidationResult:
    def __init__(
        self,
        is_valid: bool,
        errors: List[str],
        warnings: List[str],
        normalized_observation: Optional[Observation] = None
    ):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings
        self.normalized_observation = normalized_observation

    def __repr__(self) -> str:
        return (
            f"ValidationResult(is_valid={self.is_valid}, errors={self.errors}, "
            f"warnings={self.warnings}, normalized_observation={self.normalized_observation})"
        )


def validate(payload: Any, future_tolerance_seconds: float = 300.0) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(payload, dict):
        fallback_obs = Observation(
            station_id="",
            timestamp="",
            temperature_c=None,
            relative_humidity_pct=None,
            pressure_hpa=None,
            is_valid=False
        )
        return ValidationResult(
            is_valid=False,
            errors=["malformed_input:input_must_be_dict"],
            warnings=[],
            normalized_observation=fallback_obs
        )

    # Check missing required fields
    for field in REQUIRED_FIELDS:
        if field not in payload or payload[field] is None:
            errors.append(f"missing_field:{field}")

    # Station ID check
    station_id = payload.get("station_id")
    if station_id is not None and not isinstance(station_id, str):
        errors.append("invalid_type:station_id must be string")

    # Timestamp check
    timestamp_str = payload.get("timestamp")
    parsed_dt: Optional[datetime] = None
    if timestamp_str is not None:
        if not isinstance(timestamp_str, str):
            errors.append("invalid_type:timestamp must be ISO string")
        else:
            try:
                # Handle Z suffix for UTC ISO parsing
                clean_ts = timestamp_str.replace("Z", "+00:00")
                parsed_dt = datetime.fromisoformat(clean_ts)
                
                # Enforce timezone awareness
                if parsed_dt.tzinfo is None:
                    parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
                
                # Check future timestamp tolerance
                now = datetime.now(timezone.utc)
                if parsed_dt > now + timedelta(seconds=future_tolerance_seconds):
                    errors.append(f"invalid_timestamp:future timestamp {timestamp_str} exceeds tolerance")
            except Exception:
                errors.append("invalid_timestamp:format")

    # Numeric & range checks
    num_values = {}
    for param, (min_val, max_val) in PHYSICAL_LIMITS.items():
        val = payload.get(param)
        if val is not None:
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                errors.append(f"invalid_type:{param} must be numeric")
            else:
                float_val = float(val)
                num_values[param] = float_val
                if float_val < min_val or float_val > max_val:
                    errors.append(f"out_of_physical_range:{param} ({float_val}) outside [{min_val}, {max_val}]")

    is_valid = len(errors) == 0

    normalized_obs: Optional[Observation] = None
    if is_valid:
        normalized_obs = Observation(
            station_id=str(station_id),
            timestamp=str(timestamp_str),
            temperature_c=num_values["temperature_c"],
            relative_humidity_pct=num_values["relative_humidity_pct"],
            pressure_hpa=num_values["pressure_hpa"],
            is_valid=True
        )

    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        normalized_observation=normalized_obs
    )
