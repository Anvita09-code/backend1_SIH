import math
from typing import Optional, Tuple
from member1.schema.observation import Observation
from member1.config.calibration import MAGNUS_A, MAGNUS_B, DEWPOINT_TOLERANCE_C

def compute_dewpoint(temperature_c: float, relative_humidity_pct: float) -> float:
    """
    Compute approximate dewpoint in Celsius using the Magnus approximation.
    Raises ValueError if relative_humidity_pct <= 0 or > 100 to respect Phase-2 validation boundaries.
    """
    if relative_humidity_pct <= 0 or relative_humidity_pct > 100:
        raise ValueError(f"Relative humidity out of valid physical range (0, 100]: {relative_humidity_pct}")
    
    rh_ratio = relative_humidity_pct / 100.0
    gamma = (MAGNUS_A * temperature_c) / (MAGNUS_B + temperature_c) + math.log(rh_ratio)
    dewpoint = (MAGNUS_B * gamma) / (MAGNUS_A - gamma)
    return dewpoint

def check_dewpoint_consistency(obs: Observation) -> Tuple[bool, Optional[str]]:
    """
    Check if dewpoint exceeds temperature by more than configured tolerance.
    Returns (True, note) if inconsistent, (False, None) otherwise.
    """
    if not obs.is_valid:
        return False, "Skipped dewpoint check: Observation flagged invalid by Phase 2 schema validation."

    try:
        dewpoint = compute_dewpoint(obs.temperature_c, obs.relative_humidity_pct)
    except ValueError as e:
        return True, f"Dewpoint calculation failed: {str(e)}"

    threshold = obs.temperature_c + DEWPOINT_TOLERANCE_C
    if dewpoint > threshold:
        note = (
            f"Dewpoint inconsistency detected: computed dewpoint ({dewpoint:.2f}°C) "
            f"> temperature ({obs.temperature_c:.2f}°C) + tolerance ({DEWPOINT_TOLERANCE_C}°C)"
        )
        return True, note

    return False, None
