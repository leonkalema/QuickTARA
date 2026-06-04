"""
Tests for core/generators/scenario_orchestrator.py

Covers:
  - Asset deduplication (duplicate rows don't produce duplicate scenarios)
  - Manual scenario overlap skipping (_get_manual_scenario_keys)
  - has_auto_damage_drafts / has_auto_threat_drafts helpers
  - generate_damage_scenarios_for_product end-to-end with a real SQLite DB
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Warm ORM metadata
from db.product_asset_models import Base, Asset as DBAsset, ProductScope as DBProductScope, DamageScenario as DBDamageScenario  # noqa: E402


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db(tmp_path: Path) -> Generator[Session, None, None]:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _make_product(db: Session, scope_id: str = "scope-test") -> DBProductScope:
    product = DBProductScope(
        scope_id=scope_id,
        name="Test ECU",
        product_type="ECU",
        safety_level="ASIL-B",
        location="On-Board",
        trust_zone="Critical",
        version="1.0",
        is_current=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(product)
    db.commit()
    return product


def _make_asset(
    db: Session,
    asset_id: str,
    scope_id: str = "scope-test",
    asset_type: str = "Firmware",
    confidentiality: str = "High",
    integrity: str = "High",
    availability: str = "High",
) -> DBAsset:
    asset = DBAsset(
        asset_id=asset_id,
        name=f"Asset-{asset_id}",
        asset_type=asset_type,
        scope_id=scope_id,
        confidentiality=confidentiality,
        integrity=integrity,
        availability=availability,
        is_current=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(asset)
    db.commit()
    return asset


def _make_manual_damage_scenario(
    db: Session,
    scenario_id: str,
    scope_id: str,
    asset_id: str,
    damage_category: str = "Safety",
    confidentiality_impact: bool = False,
    integrity_impact: bool = True,
    availability_impact: bool = False,
) -> DBDamageScenario:
    ds = DBDamageScenario(
        scenario_id=scenario_id,
        name=f"Manual scenario {scenario_id}",
        description="Expert-written scenario",
        damage_category=damage_category,
        impact_type="Direct",
        severity="Critical",
        confidentiality_impact=confidentiality_impact,
        integrity_impact=integrity_impact,
        availability_impact=availability_impact,
        safety_impact="severe",
        financial_impact="major",
        operational_impact="major",
        privacy_impact="negligible",
        scope_id=scope_id,
        primary_component_id=asset_id,
        status="accepted",
        version=1,
        is_current=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(ds)
    db.commit()
    return ds


# ── has_auto_damage_drafts ────────────────────────────────────────────────────

class TestHasAutoDamageDrafts:
    def test_returns_false_when_no_drafts(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import has_auto_damage_drafts
        _make_product(db)
        assert has_auto_damage_drafts(db, "scope-test") is False

    def test_returns_true_after_auto_draft_inserted(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import has_auto_damage_drafts
        _make_product(db)
        ds = DBDamageScenario(
            scenario_id="DS-AUTO-abc123",
            name="Auto draft",
            description="",
            damage_category="Safety",
            impact_type="Direct",
            severity="High",
            confidentiality_impact=False,
            integrity_impact=True,
            availability_impact=False,
            safety_impact="major",
            financial_impact="negligible",
            operational_impact="negligible",
            privacy_impact="negligible",
            scope_id="scope-test",
            status="draft",
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(ds)
        db.commit()
        assert has_auto_damage_drafts(db, "scope-test") is True

    def test_returns_true_when_auto_draft_accepted(self, db: Session) -> None:
        """Accepted auto scenarios still count — prevents duplicate generation after accept-all."""
        from core.generators.scenario_orchestrator import has_auto_damage_drafts
        _make_product(db)
        ds = DBDamageScenario(
            scenario_id="DS-AUTO-accepted1",
            name="Accepted auto",
            description="",
            damage_category="Safety",
            impact_type="Direct",
            severity="High",
            confidentiality_impact=False,
            integrity_impact=True,
            availability_impact=False,
            safety_impact="major",
            financial_impact="negligible",
            operational_impact="negligible",
            privacy_impact="negligible",
            scope_id="scope-test",
            status="accepted",   # accepted — still blocks re-generation
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(ds)
        db.commit()
        assert has_auto_damage_drafts(db, "scope-test") is True

    def test_scoped_to_product(self, db: Session) -> None:
        """Drafts from a different scope don't affect the query."""
        from core.generators.scenario_orchestrator import has_auto_damage_drafts
        ds = DBDamageScenario(
            scenario_id="DS-AUTO-other",
            name="Other product draft",
            description="",
            damage_category="Safety",
            impact_type="Direct",
            severity="High",
            confidentiality_impact=False,
            integrity_impact=True,
            availability_impact=False,
            safety_impact="major",
            financial_impact="negligible",
            operational_impact="negligible",
            privacy_impact="negligible",
            scope_id="scope-OTHER",
            status="draft",
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(ds)
        db.commit()
        assert has_auto_damage_drafts(db, "scope-test") is False


# ── _get_manual_scenario_keys ─────────────────────────────────────────────────

class TestGetManualScenarioKeys:
    def test_returns_empty_when_no_manual_scenarios(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import _get_manual_scenario_keys
        assert _get_manual_scenario_keys(db, "scope-test") == set()

    def test_ignores_auto_scenarios(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import _get_manual_scenario_keys
        _make_product(db)
        _make_asset(db, "asset-1")
        # Insert an AUTO scenario — should NOT appear in keys
        ds = DBDamageScenario(
            scenario_id="DS-AUTO-111",
            name="Auto",
            description="",
            damage_category="Safety",
            impact_type="Direct",
            severity="High",
            confidentiality_impact=False,
            integrity_impact=True,
            availability_impact=False,
            safety_impact="severe",
            financial_impact="negligible",
            operational_impact="negligible",
            privacy_impact="negligible",
            scope_id="scope-test",
            primary_component_id="asset-1",
            status="draft",
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(ds)
        db.commit()
        assert _get_manual_scenario_keys(db, "scope-test") == set()

    def test_returns_key_for_manual_integrity_scenario(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import _get_manual_scenario_keys
        _make_product(db)
        _make_asset(db, "asset-1")
        _make_manual_damage_scenario(
            db, "DS-MANUAL-001", "scope-test", "asset-1",
            damage_category="Safety",
            integrity_impact=True,
        )
        keys = _get_manual_scenario_keys(db, "scope-test")
        assert ("asset-1", "Safety", "integrity") in keys

    def test_returns_key_for_manual_confidentiality_scenario(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import _get_manual_scenario_keys
        _make_product(db)
        _make_asset(db, "asset-2")
        _make_manual_damage_scenario(
            db, "DS-MANUAL-002", "scope-test", "asset-2",
            damage_category="Privacy",
            confidentiality_impact=True,
            integrity_impact=False,
        )
        keys = _get_manual_scenario_keys(db, "scope-test")
        assert ("asset-2", "Privacy", "confidentiality") in keys

    def test_scoped_correctly(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import _get_manual_scenario_keys
        # Manual scenario in a different scope
        _make_manual_damage_scenario(
            db, "DS-MANUAL-003", "scope-OTHER", "asset-x",
            damage_category="Safety",
            integrity_impact=True,
        )
        keys = _get_manual_scenario_keys(db, "scope-test")
        assert len(keys) == 0


# ── duplicate asset deduplication ────────────────────────────────────────────

class TestAssetDeduplication:
    def test_single_asset_produces_correct_scenario_count(self, db: Session) -> None:
        """
        A Firmware asset with High confidentiality should produce exactly 2
        damage scenarios (the 2 confidentiality templates). The deduplication
        guard in the orchestrator must not drop or double-count them.
        """
        from core.generators.scenario_orchestrator import generate_damage_scenarios_for_product

        _make_product(db)
        _make_asset(db, "asset-fw-c", asset_type="Firmware", confidentiality="High",
                    integrity="Low", availability="Low")

        result = generate_damage_scenarios_for_product(db, "scope-test")
        assert "error" not in result
        # High confidentiality → 2 templates; dedup leaves exactly 2
        assert result["damage_scenarios_created"] == 2

    def test_no_duplicate_scenario_names(self, db: Session) -> None:
        """
        Running generation produces unique scenario names — no two rows share
        the same name for the same product.
        """
        from core.generators.scenario_orchestrator import generate_damage_scenarios_for_product

        _make_product(db)
        _make_asset(db, "asset-fw-i", asset_type="Firmware", confidentiality="Low",
                    integrity="High", availability="Low")

        generate_damage_scenarios_for_product(db, "scope-test")

        rows = db.query(DBDamageScenario).filter(
            DBDamageScenario.scope_id == "scope-test",
            DBDamageScenario.scenario_id.like("DS-AUTO-%"),
        ).all()
        names = [r.name for r in rows]
        assert len(names) == len(set(names)), f"Duplicate names: {names}"

    def test_second_run_replaces_drafts_not_doubles(self, db: Session) -> None:
        """
        Running generation a second time must replace old auto-drafts, not
        accumulate them — the count after two runs equals the count after one.
        """
        from core.generators.scenario_orchestrator import generate_damage_scenarios_for_product

        _make_product(db)
        _make_asset(db, "asset-fw-r", asset_type="Firmware", confidentiality="High",
                    integrity="Low", availability="Low")

        result1 = generate_damage_scenarios_for_product(db, "scope-test")
        result2 = generate_damage_scenarios_for_product(db, "scope-test")
        assert result1["damage_scenarios_created"] == result2["damage_scenarios_created"]

        rows = db.query(DBDamageScenario).filter(
            DBDamageScenario.scope_id == "scope-test",
            DBDamageScenario.scenario_id.like("DS-AUTO-%"),
        ).count()
        assert rows == result2["damage_scenarios_created"]


# ── manual overlap skipping ───────────────────────────────────────────────────

class TestManualOverlapSkipping:
    def test_auto_skips_scenario_covered_by_manual(self, db: Session) -> None:
        """
        If a manual scenario already covers (asset, Safety, integrity),
        the auto-generator must not produce another Safety+integrity scenario
        for the same asset.
        """
        from core.generators.scenario_orchestrator import generate_damage_scenarios_for_product

        _make_product(db)
        _make_asset(db, "asset-fw", integrity="High", confidentiality="Low", availability="Low")

        # Manual scenario covers Safety + integrity for this asset
        _make_manual_damage_scenario(
            db, "DS-MANUAL-FW", "scope-test", "asset-fw",
            damage_category="Safety",
            integrity_impact=True,
        )

        result = generate_damage_scenarios_for_product(db, "scope-test")
        assert "error" not in result

        auto_rows = db.query(DBDamageScenario).filter(
            DBDamageScenario.scope_id == "scope-test",
            DBDamageScenario.scenario_id.like("DS-AUTO-%"),
        ).all()

        # Both integrity templates produce Safety category — both should be skipped
        for row in auto_rows:
            assert not (row.integrity_impact and row.damage_category == "Safety"), (
                f"Auto-generated a duplicate of the manual Safety+integrity scenario: {row.name}"
            )

    def test_auto_generates_uncovered_dimensions(self, db: Session) -> None:
        """
        Manual covers integrity. Auto should still generate confidentiality
        and availability scenarios for the same asset.
        """
        from core.generators.scenario_orchestrator import generate_damage_scenarios_for_product

        _make_product(db)
        _make_asset(db, "asset-all", confidentiality="High", integrity="High", availability="High")

        # Manual covers one integrity scenario
        _make_manual_damage_scenario(
            db, "DS-MANUAL-ALL", "scope-test", "asset-all",
            damage_category="Safety",
            integrity_impact=True,
        )

        result = generate_damage_scenarios_for_product(db, "scope-test")
        assert result["duplicates_skipped"] >= 1
        # Confidentiality (2) + availability (2) + possibly remaining integrity (1, Operational)
        # should still be generated
        assert result["damage_scenarios_created"] >= 2


# ── has_auto_threat_drafts ────────────────────────────────────────────────────

class TestHasAutoThreatDrafts:
    def test_returns_false_when_no_threat_drafts(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import has_auto_threat_drafts
        assert has_auto_threat_drafts(db, "scope-test") is False

    def test_returns_true_when_ts_auto_draft_exists(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import has_auto_threat_drafts
        from db.threat_scenario import ThreatScenario as DBThreatScenario
        ts = DBThreatScenario(
            threat_scenario_id="TS-AUTO-abc",
            name="Auto threat",
            description="",
            attack_vector="network",
            scope_id="scope-test",
            scope_version=1,
            status="draft",
        )
        db.add(ts)
        db.commit()
        assert has_auto_threat_drafts(db, "scope-test") is True

    def test_returns_false_when_only_manual_threats(self, db: Session) -> None:
        from core.generators.scenario_orchestrator import has_auto_threat_drafts
        from db.threat_scenario import ThreatScenario as DBThreatScenario
        ts = DBThreatScenario(
            threat_scenario_id="TS-MANUAL-001",  # no AUTO prefix
            name="Manual threat",
            description="",
            attack_vector="physical",
            scope_id="scope-test",
            scope_version=1,
            status="draft",
        )
        db.add(ts)
        db.commit()
        assert has_auto_threat_drafts(db, "scope-test") is False

    def test_accepted_auto_threats_do_count(self, db: Session) -> None:
        """Accepted auto scenarios keep the button disabled — prevents duplicate generation."""
        from core.generators.scenario_orchestrator import has_auto_threat_drafts
        from db.threat_scenario import ThreatScenario as DBThreatScenario
        ts = DBThreatScenario(
            threat_scenario_id="TS-AUTO-accepted",
            name="Accepted auto threat",
            description="",
            attack_vector="network",
            scope_id="scope-test",
            scope_version=1,
            status="accepted",
        )
        db.add(ts)
        db.commit()
        assert has_auto_threat_drafts(db, "scope-test") is True
