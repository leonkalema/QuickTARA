"""
Tests for impact rating model fixes.

Covers:
  - ImpactRatingUpdate accepts ImpactRatingLevel values (not SeverityLevel)
  - DamageScenarioUpdate accepts ImpactRatingLevel for SFOP fields
  - End-to-end: ImpactRatingUpdate → DamageScenarioUpdate pipeline validates cleanly
  - ImpactRatingSuggestion returns ImpactRatingLevel values
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError


# ── ImpactRatingUpdate ────────────────────────────────────────────────────────

class TestImpactRatingUpdate:
    def test_accepts_valid_impact_rating_level_values(self) -> None:
        from api.models.impact_rating import ImpactRatingUpdate
        obj = ImpactRatingUpdate(
            safety_impact="severe",
            financial_impact="major",
            operational_impact="moderate",
            privacy_impact="negligible",
        )
        assert obj.safety_impact.value == "severe"
        assert obj.financial_impact.value == "major"
        assert obj.operational_impact.value == "moderate"
        assert obj.privacy_impact.value == "negligible"

    def test_rejects_severity_level_values(self) -> None:
        """SeverityLevel values (Low/High/Critical) must NOT be accepted."""
        from api.models.impact_rating import ImpactRatingUpdate
        with pytest.raises(ValidationError):
            ImpactRatingUpdate(safety_impact="High")

    def test_all_fields_optional(self) -> None:
        from api.models.impact_rating import ImpactRatingUpdate
        obj = ImpactRatingUpdate()
        assert obj.safety_impact is None
        assert obj.financial_impact is None

    def test_partial_update_accepted(self) -> None:
        from api.models.impact_rating import ImpactRatingUpdate
        obj = ImpactRatingUpdate(safety_impact="major")
        assert obj.safety_impact.value == "major"
        assert obj.financial_impact is None

    def test_override_reason_accepted(self) -> None:
        from api.models.impact_rating import ImpactRatingUpdate
        obj = ImpactRatingUpdate(
            safety_impact="severe",
            sfop_rating_override_reason="Manually updated by user",
        )
        assert obj.sfop_rating_override_reason == "Manually updated by user"


# ── DamageScenarioUpdate ──────────────────────────────────────────────────────

class TestDamageScenarioUpdate:
    def test_sfop_fields_accept_impact_rating_level(self) -> None:
        from api.models.damage_scenario import DamageScenarioUpdate
        obj = DamageScenarioUpdate(
            safety_impact="negligible",
            financial_impact="moderate",
            operational_impact="major",
            privacy_impact="severe",
        )
        assert obj.safety_impact.value == "negligible"
        assert obj.financial_impact.value == "moderate"
        assert obj.operational_impact.value == "major"
        assert obj.privacy_impact.value == "severe"

    def test_sfop_fields_reject_severity_level(self) -> None:
        """Old bug: SeverityLevel values (Low/High) must NOT pass validation."""
        from api.models.damage_scenario import DamageScenarioUpdate
        with pytest.raises(ValidationError):
            DamageScenarioUpdate(safety_impact="High")

    def test_non_sfop_fields_unaffected(self) -> None:
        from api.models.damage_scenario import DamageScenarioUpdate
        obj = DamageScenarioUpdate(name="Updated name", safety_impact="major")
        assert obj.name == "Updated name"
        assert obj.safety_impact.value == "major"

    def test_all_sfop_fields_optional(self) -> None:
        from api.models.damage_scenario import DamageScenarioUpdate
        obj = DamageScenarioUpdate(name="Only name")
        assert obj.safety_impact is None
        assert obj.financial_impact is None
        assert obj.operational_impact is None
        assert obj.privacy_impact is None


# ── End-to-end: ImpactRatingUpdate → DamageScenarioUpdate pipeline ───────────

class TestImpactRatingPipeline:
    def test_pipeline_validates_cleanly(self) -> None:
        """
        Simulates what update_impact_ratings() does:
        ImpactRatingUpdate.model_dump() → DamageScenarioUpdate(**data)
        Must not raise. This was the 500 bug.
        """
        from api.models.impact_rating import ImpactRatingUpdate
        from api.models.damage_scenario import DamageScenarioUpdate
        from datetime import datetime

        ratings = ImpactRatingUpdate(
            safety_impact="major",
            financial_impact="negligible",
            operational_impact="moderate",
            privacy_impact="negligible",
            sfop_rating_override_reason="Manually updated by user",
        )
        update_data = ratings.model_dump(exclude_unset=True)
        update_data["sfop_rating_auto_generated"] = False
        update_data["sfop_rating_last_edited_by"] = "system"
        update_data["sfop_rating_last_edited_at"] = datetime.now()

        update_obj = DamageScenarioUpdate(**update_data)
        assert update_obj.safety_impact.value == "major"
        assert update_obj.sfop_rating_auto_generated is False

    def test_pipeline_rejects_invalid_values(self) -> None:
        """Garbage values must fail at ImpactRatingUpdate, not silently pass."""
        from api.models.impact_rating import ImpactRatingUpdate
        with pytest.raises(ValidationError):
            ImpactRatingUpdate(safety_impact="not_a_real_level")


# ── ImpactRatingSuggestion ────────────────────────────────────────────────────

class TestImpactRatingSuggestion:
    def test_accepts_impact_rating_level(self) -> None:
        from api.models.impact_rating import ImpactRatingSuggestion, ImpactRatingExplanation
        from api.models.damage_scenario import ImpactRatingLevel
        obj = ImpactRatingSuggestion(
            safety_impact=ImpactRatingLevel.SEVERE,
            financial_impact=ImpactRatingLevel.MAJOR,
            operational_impact=ImpactRatingLevel.MODERATE,
            privacy_impact=ImpactRatingLevel.NEGLIGIBLE,
            explanations=ImpactRatingExplanation(
                safety_impact="test",
                financial_impact="test",
                operational_impact="test",
                privacy_impact="test",
            ),
        )
        assert obj.safety_impact == ImpactRatingLevel.SEVERE


# ── Service write→read round-trip (DB level) ──────────────────────────────────

class TestSfopServiceRoundTrip:
    """
    Tests the write path (update_damage_scenario) and read path (get_damage_scenario)
    share consistent column handling. These operate on an in-memory SQLite DB.
    """

    @pytest.fixture
    def db(self, tmp_path):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from db.product_asset_models import Base
        engine = create_engine(f"sqlite:///{tmp_path}/test.db", connect_args={"check_same_thread": False})
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        session = Session()
        try:
            yield session
        finally:
            session.close()
            engine.dispose()

    def _make_scenario(self, db, scenario_id: str = "DS-AUTO-test1"):
        from db.product_asset_models import DamageScenario as DBDamageScenario, ProductScope
        from datetime import datetime
        product = ProductScope(
            scope_id="scope-sfop",
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
        ds = DBDamageScenario(
            scenario_id=scenario_id,
            name="Test scenario",
            description="",
            damage_category="Safety",
            impact_type="Direct",
            severity="High",
            confidentiality_impact=False,
            integrity_impact=True,
            availability_impact=False,
            safety_impact="negligible",
            financial_impact="negligible",
            operational_impact="negligible",
            privacy_impact="negligible",
            scope_id="scope-sfop",
            status="draft",
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(ds)
        db.commit()
        return ds

    def test_sfop_write_stores_string_not_boolean(self, db) -> None:
        """
        update_damage_scenario must write 'major' to safety_impact column,
        not True/False (the old boolean-conversion bug).
        """
        from api.services.damage_scenario_service import update_damage_scenario
        from api.models.damage_scenario import DamageScenarioUpdate
        from db.product_asset_models import DamageScenario as DBDamageScenario

        self._make_scenario(db, "DS-AUTO-test2")
        update = DamageScenarioUpdate(
            safety_impact="major",
            financial_impact="moderate",
            operational_impact="severe",
            privacy_impact="negligible",
            sfop_rating_override_reason="Manually updated by user",
        )
        update_damage_scenario(db, "DS-AUTO-test2", update)

        row = db.query(DBDamageScenario).filter_by(scenario_id="DS-AUTO-test2").first()
        assert row.safety_impact == "major", f"Expected 'major', got {row.safety_impact!r}"
        assert row.financial_impact == "moderate"
        assert row.operational_impact == "severe"
        assert row.privacy_impact == "negligible"

    def test_sfop_read_populates_impact_rating(self, db) -> None:
        """
        get_damage_scenario must return impact_rating with values read from
        the direct DB columns, not None.
        """
        from api.services.damage_scenario_service import get_damage_scenario, update_damage_scenario
        from api.models.damage_scenario import DamageScenarioUpdate

        self._make_scenario(db, "DS-AUTO-test3")
        update_damage_scenario(db, "DS-AUTO-test3", DamageScenarioUpdate(
            safety_impact="severe",
            financial_impact="major",
            operational_impact="moderate",
            privacy_impact="negligible",
            sfop_rating_override_reason="test",
        ))

        result = get_damage_scenario(db, "DS-AUTO-test3")
        assert result is not None
        assert result.impact_rating is not None, "impact_rating must not be None after update"
        assert result.impact_rating.safety.value == "severe"
        assert result.impact_rating.financial.value == "major"
        assert result.impact_rating.operational.value == "moderate"
        assert result.impact_rating.privacy.value == "negligible"
