from dataclasses import dataclass
from typing import List
from member1.validation.validator import ValidationResult
from member1.temporal.features import TemporalFeatures
from member1.crossvar.evidence import CrossVariableEvidence


@dataclass(frozen=True)
class ObservationEvidence:
    station_id: str
    timestamp: str
    validation: ValidationResult
    temporal_features: List[TemporalFeatures]
    cross_variable: CrossVariableEvidence
    schema_version: str = "1.0"
