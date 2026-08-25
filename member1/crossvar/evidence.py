from dataclasses import dataclass, field

@dataclass(frozen=True)
class CrossVariableEvidence:
    station_id: str
    timestamp: str
    dewpoint_consistency_flag: bool
    pressure_temperature_flag: bool
    humidity_bounds_flag: bool
    notes: list[str] = field(default_factory=list)
