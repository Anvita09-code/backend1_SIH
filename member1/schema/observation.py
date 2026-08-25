from dataclasses import dataclass

@dataclass(frozen=True)
class Observation:
    """
    Canonical immutable observation representation for Member 1 OTE pipeline.
    
    LOCKED CONTRACT:
    Do not add, remove, or rename any public fields.
    """
    station_id: str
    timestamp: str
    temperature_c: float | None
    relative_humidity_pct: float | None
    pressure_hpa: float | None
    is_valid: bool | None = None
