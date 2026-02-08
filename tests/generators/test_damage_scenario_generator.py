"""
Tests for core/generators/damage_scenario_generator.py
"""
import pytest
from typing import Dict, Any

from core.generators.damage_scenario_generator import (
    generate_for_asset,
    load_templates,
    _get_active_cia_dimensions,
    _scale_impact,
)


SAMPLE_ASSET_HIGH_CIA: Dict[str, Any] = {
    "asset_id": "asset_001",
    "name": "Brake ECU Firmware",
    "asset_type": "Firmware",
    "scope_id": "scope_001",
    "confidentiality": "High",
    "integrity": "High",
    "availability": "High",
}

SAMPLE_ASSET_MIXED_CIA: Dict[str, Any] = {
    "asset_id": "asset_002",
    "name": "Infotainment Config",
    "asset_type": "Configuration",
    "scope_id": "scope_001",
    "confidentiality": "Low",
    "integrity": "Medium",
    "availability": "Low",
}

SAMPLE_ASSET_LOW_CIA: Dict[str, Any] = {
    "asset_id": "asset_003",
    "name": "Documentation",
    "asset_type": "Other",
    "scope_id": "scope_001",
    "confidentiality": "Low",
    "integrity": "Low",
    "availability": "Low",
}


class TestLoadTemplates:
    """Tests for template loading."""

    def test_loads_successfully(self) -> None:
        templates = load_templates()
        assert "templates" in templates
        assert "confidentiality" in templates["templates"]
        assert "integrity" in templates["templates"]
        assert "availability" in templates["templates"]

    def test_each_dimension_has_templates(self) -> None:
        templates = load_templates()
        for dim in ("confidentiality", "integrity", "availability"):
            assert len(templates["templates"][dim]) > 0


class TestGetActiveCiaDimensions:
    """Tests for CIA dimension filtering."""

    def test_all_high_returns_all_three(self) -> None:
        result = _get_active_cia_dimensions(SAMPLE_ASSET_HIGH_CIA)
        assert set(result.keys()) == {"confidentiality", "integrity", "availability"}

    def test_mixed_returns_only_medium_and_high(self) -> None:
        result = _get_active_cia_dimensions(SAMPLE_ASSET_MIXED_CIA)
        assert result == {"integrity": "Medium"}

    def test_all_low_returns_empty(self) -> None:
        result = _get_active_cia_dimensions(SAMPLE_ASSET_LOW_CIA)
        assert result == {}


class TestGenerateForAsset:
    """Tests for full damage scenario generation."""

    def test_high_cia_generates_six_scenarios(self) -> None:
        """All 3 CIA high → 2 templates each = 6 scenarios."""
        scenarios = generate_for_asset(SAMPLE_ASSET_HIGH_CIA, "TestProduct")
        assert len(scenarios) == 6

    def test_mixed_cia_generates_two_scenarios(self) -> None:
        """Only integrity Medium → 2 templates = 2 scenarios."""
        scenarios = generate_for_asset(SAMPLE_ASSET_MIXED_CIA, "TestProduct")
        assert len(scenarios) == 2

    def test_low_cia_generates_zero_scenarios(self) -> None:
        """All Low → nothing to generate."""
        scenarios = generate_for_asset(SAMPLE_ASSET_LOW_CIA, "TestProduct")
        assert len(scenarios) == 0

    def test_scenario_has_required_fields(self) -> None:
        scenarios = generate_for_asset(SAMPLE_ASSET_HIGH_CIA, "TestProduct")
        required_fields = {
            "scenario_id", "name", "description", "damage_category",
            "impact_type", "severity", "confidentiality_impact",
            "integrity_impact", "availability_impact", "scope_id",
        }
        for s in scenarios:
            assert required_fields.issubset(s.keys()), f"Missing fields: {required_fields - s.keys()}"

    def test_scenario_name_contains_asset_name(self) -> None:
        scenarios = generate_for_asset(SAMPLE_ASSET_HIGH_CIA, "TestProduct")
        for s in scenarios:
            assert "Brake ECU Firmware" in s["name"]

    def test_scenario_ids_are_unique(self) -> None:
        scenarios = generate_for_asset(SAMPLE_ASSET_HIGH_CIA, "TestProduct")
        ids = [s["scenario_id"] for s in scenarios]
        assert len(ids) == len(set(ids))

    def test_auto_generated_flag_is_set(self) -> None:
        scenarios = generate_for_asset(SAMPLE_ASSET_HIGH_CIA, "TestProduct")
        for s in scenarios:
            assert s["auto_generated"] is True


class TestScaleImpact:
    """Tests for SFOP impact scaling."""

    def test_severe_scaled_by_severe_stays_severe(self) -> None:
        assert _scale_impact("severe", "severe") == "severe"

    def test_severe_scaled_by_moderate_becomes_moderate(self) -> None:
        assert _scale_impact("severe", "moderate") == "moderate"

    def test_negligible_stays_negligible(self) -> None:
        assert _scale_impact("negligible", "severe") == "negligible"

    def test_major_scaled_by_major_stays_major(self) -> None:
        assert _scale_impact("major", "major") == "major"
