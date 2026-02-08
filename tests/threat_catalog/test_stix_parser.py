"""
Tests for core/threat_catalog/stix_parser.py

Purpose: Verify STIX 2.1 bundle parsing, technique/mitigation extraction, and enrichment
Depends on: core/threat_catalog/stix_parser.py
"""
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from core.threat_catalog.stix_parser import (
    load_stix_bundle,
    extract_techniques,
    extract_mitigations,
    extract_tactics,
    build_technique_mitigation_map,
    parse_full_bundle,
    _clean_description,
    _get_external_id,
)


def _make_bundle(objects: list) -> Dict[str, Any]:
    """Helper: build a minimal STIX bundle dict."""
    return {"type": "bundle", "id": "bundle--test", "objects": objects}


def _make_technique(
    stix_id: str = "attack-pattern--abc",
    external_id: str = "T0800",
    name: str = "Test Technique",
    description: str = "A test technique.",
    tactic: str = "initial-access",
    revoked: bool = False,
) -> Dict[str, Any]:
    """Helper: build a minimal STIX attack-pattern."""
    return {
        "type": "attack-pattern",
        "id": stix_id,
        "name": name,
        "description": description,
        "revoked": revoked,
        "external_references": [
            {"source_name": "mitre-attack", "external_id": external_id}
        ],
        "kill_chain_phases": [
            {"kill_chain_name": "mitre-ics-attack", "phase_name": tactic}
        ],
    }


def _make_mitigation(
    stix_id: str = "course-of-action--xyz",
    external_id: str = "M0801",
    name: str = "Test Mitigation",
) -> Dict[str, Any]:
    """Helper: build a minimal STIX course-of-action."""
    return {
        "type": "course-of-action",
        "id": stix_id,
        "name": name,
        "description": "A test mitigation.",
        "external_references": [
            {"source_name": "mitre-attack", "external_id": external_id}
        ],
    }


def _make_relationship(source_ref: str, target_ref: str) -> Dict[str, Any]:
    """Helper: build a mitigates relationship."""
    return {
        "type": "relationship",
        "id": "relationship--rel1",
        "relationship_type": "mitigates",
        "source_ref": source_ref,
        "target_ref": target_ref,
    }


class TestExtractTechniques:
    def test_extracts_valid_technique(self) -> None:
        bundle = _make_bundle([_make_technique()])
        result = extract_techniques(bundle)
        assert len(result) == 1
        assert result[0]["mitre_technique_id"] == "T0800"
        assert result[0]["name"] == "Test Technique"

    def test_skips_revoked_technique(self) -> None:
        bundle = _make_bundle([_make_technique(revoked=True)])
        result = extract_techniques(bundle)
        assert len(result) == 0

    def test_skips_non_attack_pattern(self) -> None:
        mit = _make_mitigation()
        bundle = _make_bundle([mit])
        result = extract_techniques(bundle)
        assert len(result) == 0

    def test_handles_empty_bundle(self) -> None:
        result = extract_techniques({"objects": []})
        assert result == []


class TestExtractMitigations:
    def test_extracts_valid_mitigation(self) -> None:
        bundle = _make_bundle([_make_mitigation()])
        result = extract_mitigations(bundle)
        assert len(result) == 1
        key = "course-of-action--xyz"
        assert result[key]["mitre_id"] == "M0801"

    def test_skips_non_course_of_action(self) -> None:
        bundle = _make_bundle([_make_technique()])
        result = extract_mitigations(bundle)
        assert len(result) == 0


class TestBuildTechniqueMitigationMap:
    def test_maps_mitigation_to_technique(self) -> None:
        rel = _make_relationship("course-of-action--xyz", "attack-pattern--abc")
        bundle = _make_bundle([rel])
        result = build_technique_mitigation_map(bundle)
        assert "attack-pattern--abc" in result
        assert "course-of-action--xyz" in result["attack-pattern--abc"]


class TestParseFullBundle:
    def test_enriches_techniques_with_mitigations(self) -> None:
        tech = _make_technique()
        mit = _make_mitigation()
        rel = _make_relationship(mit["id"], tech["id"])
        bundle = _make_bundle([tech, mit, rel])

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as fh:
            json.dump(bundle, fh)
            tmp_path = Path(fh.name)

        result = parse_full_bundle(tmp_path)
        assert len(result) == 1
        assert len(result[0]["mitigations"]) == 1
        assert result[0]["mitigations"][0]["name"] == "Test Mitigation"
        assert result[0]["tactic_names"] == ["initial-access"]
        tmp_path.unlink()


class TestCleanDescription:
    def test_removes_citations(self) -> None:
        raw = "Some text (Citation: Example 2023) more text."
        result = _clean_description(raw)
        assert "(Citation:" not in result
        assert "Some text" in result

    def test_collapses_whitespace(self) -> None:
        raw = "Line one.\n  Line two.\n\nLine three."
        result = _clean_description(raw)
        assert "\n" not in result


class TestGetExternalId:
    def test_returns_id_for_mitre_attack(self) -> None:
        obj = {
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T0871"}
            ]
        }
        assert _get_external_id(obj) == "T0871"

    def test_returns_none_for_no_match(self) -> None:
        obj = {"external_references": [{"source_name": "other", "external_id": "X1"}]}
        assert _get_external_id(obj) is None
