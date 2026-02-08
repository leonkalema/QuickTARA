"""
Tests for core/threat_catalog/automotive_mapping.py

Purpose: Verify automotive mapping config loading, STRIDE mapping, and technique enrichment
Depends on: core/threat_catalog/automotive_mapping.py
"""
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from core.threat_catalog.automotive_mapping import (
    load_mapping_config,
    get_stride_for_tactic,
    enrich_technique,
    enrich_all_techniques,
    TACTIC_TO_STRIDE,
)


def _sample_mapping_config() -> Dict[str, Any]:
    """Helper: build a minimal mapping config dict."""
    return {
        "version": "1.0.0",
        "attack_version": "15.1",
        "mappings": {
            "T0800": {
                "automotive_relevance": 5,
                "automotive_context": "ECU firmware update exploitation",
                "component_types": ["controller", "gateway"],
                "trust_zones": ["trusted", "secure"],
                "attack_vectors": ["can_bus", "usb"],
                "typical_likelihood": 3,
                "typical_severity": 5,
                "cwe_ids": ["CWE-693"],
                "capec_ids": [],
                "examples": ["UDS firmware exploit"],
            }
        },
    }


def _sample_technique(technique_id: str = "T0800") -> Dict[str, Any]:
    """Helper: build a parsed STIX technique dict."""
    return {
        "stix_id": "attack-pattern--abc",
        "mitre_technique_id": technique_id,
        "name": "Activate Firmware Update Mode",
        "description": "Adversaries may activate firmware update mode.",
        "tactic_names": ["inhibit-response-function"],
        "mitigations": [
            {
                "stix_id": "course-of-action--xyz",
                "mitre_id": "M0801",
                "name": "Access Management",
                "description": "Restrict access to firmware update.",
            }
        ],
    }


class TestLoadMappingConfig:
    def test_loads_valid_config(self) -> None:
        config = _sample_mapping_config()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as fh:
            json.dump(config, fh)
            tmp_path = Path(fh.name)

        result = load_mapping_config(tmp_path)
        assert result["version"] == "1.0.0"
        assert "T0800" in result["mappings"]
        tmp_path.unlink()

    def test_returns_empty_for_missing_file(self) -> None:
        result = load_mapping_config(Path("/nonexistent/file.json"))
        assert result["mappings"] == {}


class TestGetStrideForTactic:
    def test_known_tactic_maps_correctly(self) -> None:
        assert get_stride_for_tactic("initial-access") == "spoofing"
        assert get_stride_for_tactic("inhibit-response-function") == "denial_of_service"
        assert get_stride_for_tactic("collection") == "info_disclosure"
        assert get_stride_for_tactic("impact") == "denial_of_service"

    def test_unknown_tactic_defaults_to_tampering(self) -> None:
        assert get_stride_for_tactic("unknown-tactic") == "tampering"

    def test_all_mapped_tactics_have_valid_stride(self) -> None:
        valid_stride = {
            "spoofing", "tampering", "repudiation",
            "info_disclosure", "denial_of_service", "elevation_of_privilege",
        }
        for stride_val in TACTIC_TO_STRIDE.values():
            assert stride_val in valid_stride


class TestEnrichTechnique:
    def test_enriches_mapped_technique(self) -> None:
        config = _sample_mapping_config()
        tech = _sample_technique("T0800")
        result = enrich_technique(tech, config)

        assert result is not None
        assert result["mitre_technique_id"] == "T0800"
        assert result["automotive_relevance"] == 5
        assert result["source"] == "mitre_attack_ics"
        assert result["stride_category"] == "denial_of_service"
        assert "controller" in result["applicable_component_types"]
        assert len(result["mitigation_strategies"]) == 1

    def test_returns_none_for_unmapped_technique(self) -> None:
        config = _sample_mapping_config()
        tech = _sample_technique("T9999")
        result = enrich_technique(tech, config)
        assert result is None


class TestEnrichAllTechniques:
    def test_filters_to_mapped_only(self) -> None:
        config = _sample_mapping_config()
        techniques = [
            _sample_technique("T0800"),
            _sample_technique("T9999"),
        ]
        result = enrich_all_techniques(techniques, config)
        assert len(result) == 1
        assert result[0]["mitre_technique_id"] == "T0800"

    def test_empty_input_returns_empty(self) -> None:
        config = _sample_mapping_config()
        result = enrich_all_techniques([], config)
        assert result == []
