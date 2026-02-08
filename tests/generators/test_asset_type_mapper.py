"""
Tests for core/generators/asset_type_mapper.py
"""
import pytest
from core.generators.asset_type_mapper import (
    get_component_types,
    get_catalog_trust_zones,
    get_severity,
    get_impact_level,
)


class TestGetComponentTypes:
    """Tests for asset type → component type mapping."""

    def test_firmware_maps_to_controller_types(self) -> None:
        result = get_component_types("Firmware")
        assert "controller" in result
        assert "gateway" in result

    def test_communication_maps_to_communication_types(self) -> None:
        result = get_component_types("Communication")
        assert "communication" in result
        assert "gateway" in result

    def test_unknown_type_returns_other(self) -> None:
        result = get_component_types("NonExistent")
        assert result == ["other"]

    def test_all_known_types_have_mappings(self) -> None:
        known_types = [
            "Firmware", "Software", "Configuration", "Calibration",
            "Data", "Diagnostic", "Communication", "Hardware",
            "Interface", "Other",
        ]
        for asset_type in known_types:
            result = get_component_types(asset_type)
            assert len(result) > 0, f"No mapping for {asset_type}"


class TestGetCatalogTrustZones:
    """Tests for trust zone mapping."""

    def test_critical_maps_to_secure(self) -> None:
        result = get_catalog_trust_zones("Critical")
        assert "secure" in result

    def test_untrusted_maps_to_external(self) -> None:
        result = get_catalog_trust_zones("Untrusted")
        assert "external" in result

    def test_unknown_zone_defaults_to_untrusted(self) -> None:
        result = get_catalog_trust_zones("Unknown")
        assert result == ["untrusted"]


class TestGetSeverity:
    """Tests for CIA level → severity mapping."""

    def test_high_maps_to_critical(self) -> None:
        assert get_severity("High") == "Critical"

    def test_medium_maps_to_high(self) -> None:
        assert get_severity("Medium") == "High"

    def test_low_maps_to_medium(self) -> None:
        assert get_severity("Low") == "Medium"

    def test_na_maps_to_low(self) -> None:
        assert get_severity("N/A") == "Low"

    def test_unknown_defaults_to_medium(self) -> None:
        assert get_severity("Unknown") == "Medium"


class TestGetImpactLevel:
    """Tests for CIA level → SFOP impact level mapping."""

    def test_high_maps_to_severe(self) -> None:
        assert get_impact_level("High") == "severe"

    def test_medium_maps_to_major(self) -> None:
        assert get_impact_level("Medium") == "major"

    def test_low_maps_to_moderate(self) -> None:
        assert get_impact_level("Low") == "moderate"

    def test_unknown_defaults_to_negligible(self) -> None:
        assert get_impact_level("Unknown") == "negligible"
