from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationConfig:
    min_temp_c: float = -80.0
    max_temp_c: float = 60.0
    min_rh_pct: float = 0.0
    max_rh_pct: float = 100.0
    min_pressure_hpa: float = 800.0
    max_pressure_hpa: float = 1100.0

@dataclass(frozen=True)
class CalibrationRegistry:
    validation: ValidationConfig = ValidationConfig()

# Dewpoint Magnus Approximation & Consistency Parameters (Phase 5C)
MAGNUS_A = 17.625
MAGNUS_B = 243.04
DEWPOINT_TOLERANCE_C = 0.5
