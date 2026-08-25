import pytest
from dataclasses import is_dataclass, fields
from member1.crossvar.evidence import CrossVariableEvidence

def test_crossvariable_evidence_contract_fields():
    assert is_dataclass(CrossVariableEvidence)
    
    expected_fields = {
        "station_id": str,
        "timestamp": str,
        "dewpoint_consistency_flag": bool,
        "pressure_temperature_flag": bool,
        "humidity_bounds_flag": bool,
        "notes": list[str],
    }
    
    cls_fields = {f.name: f.type for f in fields(CrossVariableEvidence)}
    assert cls_fields == expected_fields, f"Fields mismatch! Got {cls_fields}"

def test_crossvariable_evidence_immutability():
    evidence = CrossVariableEvidence(
        station_id="ST_001",
        timestamp="2026-08-25T12:00:00Z",
        dewpoint_consistency_flag=True,
        pressure_temperature_flag=True,
        humidity_bounds_flag=True,
        notes=["Test note"]
    )
    with pytest.raises(Exception):
        evidence.dewpoint_consistency_flag = False
