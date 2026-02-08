"""
Tests for core/threat_catalog/catalog_seeder.py

Purpose: Verify DB seeding logic — create, update, skip behaviors
Depends on: core/threat_catalog/catalog_seeder.py, db/threat_catalog.py
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from core.threat_catalog.catalog_seeder import (
    seed_from_enriched,
    get_catalog_stats,
    _create_threat,
    _update_threat,
)
from db.threat_catalog import ThreatCatalog


def _sample_enriched_threat(technique_id: str = "T0800") -> Dict[str, Any]:
    """Helper: build an enriched threat dict ready for seeding."""
    return {
        "mitre_technique_id": technique_id,
        "title": f"Test Threat {technique_id}",
        "description": f"Description for {technique_id}",
        "stride_category": "denial_of_service",
        "mitre_tactic": "inhibit-response-function",
        "source": "mitre_attack_ics",
        "source_version": "15.1",
        "automotive_relevance": 5,
        "automotive_context": "ECU firmware exploitation",
        "applicable_component_types": ["controller", "gateway"],
        "applicable_trust_zones": ["trusted"],
        "attack_vectors": ["can_bus"],
        "typical_likelihood": 3,
        "typical_severity": 5,
        "mitigation_strategies": [],
        "cwe_ids": ["CWE-693"],
        "capec_ids": [],
        "examples": ["Example attack"],
    }


def _mock_db_threat(
    technique_id: str = "T0800",
    is_user_modified: bool = False,
) -> ThreatCatalog:
    """Helper: build a mock ThreatCatalog row."""
    threat = ThreatCatalog()
    threat.id = f"MITRE-{technique_id}"
    threat.mitre_technique_id = technique_id
    threat.title = f"Old Title {technique_id}"
    threat.is_user_modified = is_user_modified
    threat.updated_at = datetime.now()
    return threat


class TestSeedFromEnriched:
    def test_creates_new_threats(self) -> None:
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        threats = [_sample_enriched_threat("T0800"), _sample_enriched_threat("T0814")]

        result = seed_from_enriched(db, threats)

        assert result["created"] == 2
        assert result["updated"] == 0
        assert result["skipped"] == 0
        assert db.add.call_count == 2
        db.commit.assert_called_once()

    def test_updates_existing_unmodified_threat(self) -> None:
        existing = _mock_db_threat("T0800", is_user_modified=False)
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = existing
        threats = [_sample_enriched_threat("T0800")]

        result = seed_from_enriched(db, threats)

        assert result["created"] == 0
        assert result["updated"] == 1
        assert result["skipped"] == 0

    def test_skips_user_modified_threat(self) -> None:
        existing = _mock_db_threat("T0800", is_user_modified=True)
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = existing
        threats = [_sample_enriched_threat("T0800")]

        result = seed_from_enriched(db, threats, force_update=False)

        assert result["created"] == 0
        assert result["updated"] == 0
        assert result["skipped"] == 1

    def test_force_update_overrides_user_modified(self) -> None:
        existing = _mock_db_threat("T0800", is_user_modified=True)
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = existing
        threats = [_sample_enriched_threat("T0800")]

        result = seed_from_enriched(db, threats, force_update=True)

        assert result["updated"] == 1
        assert result["skipped"] == 0

    def test_skips_threats_without_technique_id(self) -> None:
        db = MagicMock()
        threat = _sample_enriched_threat("T0800")
        threat["mitre_technique_id"] = ""

        result = seed_from_enriched(db, [threat])

        assert result["skipped"] == 1
        assert result["created"] == 0

    def test_empty_list_returns_zeros(self) -> None:
        db = MagicMock()
        result = seed_from_enriched(db, [])
        assert result == {"created": 0, "updated": 0, "skipped": 0}


class TestGetCatalogStats:
    def test_returns_correct_stats(self) -> None:
        db = MagicMock()
        db.query.return_value.count.return_value = 30
        db.query.return_value.filter.return_value.count.side_effect = [25, 5, 3]

        result = get_catalog_stats(db)

        assert result["total"] == 30
        assert result["mitre_attack_ics"] == 25
        assert result["custom"] == 5
        assert result["user_modified"] == 3
