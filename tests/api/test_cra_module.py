"""
Tests for the CRA Compliance Module

Covers:
  - Classification logic (questionnaire scoring)
  - Auto-mapping logic (TARA artifact detection)
  - Pydantic model validation
  - API route import verification
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.cra_classifier import (
    classify_product,
    CRA_CLASSIFICATION_QUESTIONS,
    ClassificationResult,
)
from core.cra_annex_ii import evaluate_annex_ii, ANNEX_II_ITEMS
from core.cra_auto_mapper import (
    CRA_REQUIREMENTS,
    get_requirement_by_id,
)
from api.models.cra import (
    CraAssessmentCreate,
    CraAssessmentResponse,
    ClassifyRequest,
    ClassificationResponse,
    CraRequirementStatusResponse,
    CompensatingControlResponse,
    CraAssessmentListResponse,
    AutoMapResponse,
)


class TestClassificationLogic:
    """Test the CRA classification questionnaire scoring."""

    def test_default_classification(self) -> None:
        """No category_id -> Default category."""
        result = classify_product({})
        assert result.classification == "default"
        assert result.compliance_deadline == "2027-12-11"
        assert result.cost_estimate_max <= 5000

    def test_class_i_classification(self) -> None:
        """Class I category without harmonised standard -> Module B+C."""
        result = classify_product({}, category_id="CI-01")
        assert result.classification == "class_i"
        assert result.compliance_deadline == "2027-12-11"
        assert "B+C" in result.conformity_module.name or "Module B" in result.conformity_module.name

    def test_class_i_with_harmonised_standard(self) -> None:
        """Class I + harmonised standard -> Module A."""
        result = classify_product({}, category_id="CI-01", uses_harmonised_standard=True)
        assert result.classification == "class_i"
        assert "Module A" in result.conformity_module.name

    def test_class_ii_classification(self) -> None:
        """Class II category -> Module B+C mandatory."""
        result = classify_product({}, category_id="CII-01")
        assert result.classification == "class_ii"
        assert result.compliance_deadline == "2027-12-11"
        assert result.conformity_module.mandatory is True

    def test_critical_classification(self) -> None:
        """Critical category -> Module B+C mandatory."""
        result = classify_product({}, category_id="CR-01")
        assert result.classification == "critical"
        assert result.compliance_deadline == "2027-12-11"
        assert result.cost_estimate_min >= 50000

    def test_automotive_exception_flag(self) -> None:
        """Automotive exception sets scope_warning per Art. 2(2)(c) CRA."""
        result = classify_product({}, category_id="CI-01", automotive_exception=True)
        assert result.automotive_exception is True
        assert result.scope_warning != "", "scope_warning must be non-empty when automotive_exception=True"
        assert "Art. 2(2)(c)" in result.scope_warning
        assert "PROVISIONAL" in result.scope_warning

    def test_no_automotive_exception_has_no_scope_warning(self) -> None:
        """Normal products have no scope_warning."""
        result = classify_product({}, category_id="CI-01", automotive_exception=False)
        assert result.scope_warning == ""

    def test_steward_path_classification(self) -> None:
        """Art. 24 steward path produces 'steward' classification and security attestation."""
        result = classify_product({}, is_open_source_steward=True)
        assert result.classification == "steward"
        assert result.conformity_module.module_id == "security_attestation"
        assert result.conformity_module.mandatory is True
        assert result.conformity_module.alternatives == []
        assert "Art. 24" in result.rationale or "Art. 24" in result.conformity_module.rationale

    def test_steward_path_scope_warning_is_provisional(self) -> None:
        """Steward path sets a scope_warning flagging the provisional nature."""
        result = classify_product({}, is_open_source_steward=True)
        assert "PROVISIONAL" in result.scope_warning
        assert "Art. 24" in result.scope_warning

    def test_steward_path_cost_is_low(self) -> None:
        """Steward cost estimate reflects attestation-only effort."""
        result = classify_product({}, is_open_source_steward=True)
        assert result.cost_estimate_max <= 2_000

    def test_steward_reporting_deadline_still_applies(self) -> None:
        """Art. 14 reporting deadline (Sep 2026) still applies to stewards."""
        result = classify_product({}, is_open_source_steward=True)
        assert result.reporting_deadline == "2026-09-11"

    def test_steward_overrides_category(self) -> None:
        """Steward flag takes precedence over category_id selection."""
        result = classify_product({}, category_id="CII-01", is_open_source_steward=True)
        assert result.classification == "steward"

    def test_result_is_frozen_dataclass(self) -> None:
        """ClassificationResult is immutable."""
        result = classify_product({})
        assert isinstance(result, ClassificationResult)
        with pytest.raises(AttributeError):
            result.classification = "critical"  # type: ignore

    def test_missing_category_defaults_to_default(self) -> None:
        """No category_id -> Default."""
        result = classify_product({})
        assert result.classification == "default"

    def test_questions_list_has_three_items(self) -> None:
        """Classification questionnaire has exactly 3 questions."""
        assert len(CRA_CLASSIFICATION_QUESTIONS) == 3
        ids = {q["id"] for q in CRA_CLASSIFICATION_QUESTIONS}
        assert ids == {"q_category", "q_harmonised_standard", "q_open_source"}

    def test_open_source_class_ii_gets_module_a(self) -> None:
        """Open-source Class II with public docs -> Module A."""
        result = classify_product({}, category_id="CII-01", is_open_source_public=True)
        assert result.classification == "class_ii"
        assert "Module A" in result.conformity_module.name

    def test_reporting_deadline(self) -> None:
        """All products have 11 Sep 2026 reporting deadline."""
        result = classify_product({})
        assert result.reporting_deadline == "2026-09-11"


class TestAnnexII:
    """Test the Annex II user information checklist."""

    def test_nine_annex_ii_items(self) -> None:
        """Annex II has exactly 9 mandatory user-information items."""
        assert len(ANNEX_II_ITEMS) == 9

    def test_all_items_have_article_ref(self) -> None:
        """Every Annex II item references a specific article."""
        for item in ANNEX_II_ITEMS:
            assert item.article_ref.startswith("Annex II"), (
                f"{item.key} missing Annex II reference"
            )

    def test_support_period_auto_derived_when_eoss_present(self) -> None:
        """support_period item is marked 'done' when eoss_date is populated."""
        results = evaluate_annex_ii({"eoss_date": "2032-12-31"})
        sp = next(r for r in results if r.key == "support_period")
        assert sp.status == "done"
        assert sp.auto_derived is True
        assert sp.derived_value == "2032-12-31"

    def test_support_period_action_required_when_eoss_missing(self) -> None:
        """support_period item is 'action_required' when eoss_date is absent."""
        results = evaluate_annex_ii({})
        sp = next(r for r in results if r.key == "support_period")
        assert sp.status == "action_required"
        assert sp.auto_derived is True

    def test_non_auto_items_are_not_checked(self) -> None:
        """Items that cannot be auto-derived are returned as 'not_checked'."""
        results = evaluate_annex_ii({})
        non_auto = [r for r in results if not r.auto_derived]
        for r in non_auto:
            assert r.status == "not_checked"

    def test_evaluate_returns_all_nine(self) -> None:
        """evaluate_annex_ii returns exactly 9 results."""
        results = evaluate_annex_ii({})
        assert len(results) == 9


class TestCraRequirements:
    """Test the CRA requirements master list."""

    def test_eighteen_requirements(self) -> None:
        """Must have exactly 18 CRA requirements."""
        assert len(CRA_REQUIREMENTS) == 18

    def test_requirement_ids_sequential(self) -> None:
        """Requirement IDs are CRA-01 through CRA-18."""
        expected = {f"CRA-{i:02d}" for i in range(1, 19)}
        actual = {r["id"] for r in CRA_REQUIREMENTS}
        assert actual == expected

    def test_requirement_categories(self) -> None:
        """All requirements belong to valid categories."""
        valid_categories = {"technical", "process", "documentation"}
        for req in CRA_REQUIREMENTS:
            assert req["category"] in valid_categories, f"{req['id']} has invalid category"

    def test_cra14_annex_part_is_art14_obligation(self) -> None:
        """CRA-14 (24h reporting) is an Art. 14 obligation, not Annex I Part II."""
        req = get_requirement_by_id("CRA-14")
        assert req is not None
        assert req["annex_part"] == "Art. 14 Obligation", (
            "CRA-14 must be labelled 'Art. 14 Obligation' — it is not an Annex I item"
        )

    def test_cra09_covers_part_i_para1_and_para10(self) -> None:
        """CRA-09 article reference covers both §1 (no known exploitable) and §10 (updates)."""
        req = get_requirement_by_id("CRA-09")
        assert req is not None
        assert "§1" in req["article"] and "§10" in req["article"]

    def test_cra13_covers_part_ii_para4_to_6(self) -> None:
        """CRA-13 covers Annex I Part II §4 (disclosure), §5 (CVD policy), §6 (contact)."""
        req = get_requirement_by_id("CRA-13")
        assert req is not None
        # Article string is "Annex I Part II §4-6" — range notation covers §4, §5, §6
        assert "§4-6" in req["article"] or ("§4" in req["article"] and "§6" in req["article"])

    def test_get_requirement_by_id_found(self) -> None:
        """Look up existing requirement."""
        result = get_requirement_by_id("CRA-01")
        assert result is not None
        assert result["name"] == "Secure by default configuration"

    def test_get_requirement_by_id_not_found(self) -> None:
        """Look up non-existent requirement returns None."""
        assert get_requirement_by_id("CRA-99") is None

    def test_each_requirement_has_article(self) -> None:
        """Every requirement references a CRA article."""
        for req in CRA_REQUIREMENTS:
            assert req["article"], f"{req['id']} missing article"


class TestPydanticModels:
    """Test Pydantic model validation."""

    def test_assessment_create_valid(self) -> None:
        """Valid assessment creation payload."""
        payload = CraAssessmentCreate(
            product_id="test-product-001",
            product_type="current",
        )
        assert payload.product_id == "test-product-001"
        assert payload.product_type.value == "current"

    def test_assessment_create_legacy(self) -> None:
        """Legacy product type accepted."""
        payload = CraAssessmentCreate(
            product_id="legacy-ecu",
            product_type="legacy_c",
        )
        assert payload.product_type.value == "legacy_c"

    def test_classify_request_validation(self) -> None:
        """Classify request with answers dict."""
        req = ClassifyRequest(
            answers={"q1": True, "q2": False},
            automotive_exception=False,
        )
        assert req.answers["q1"] is True

    def test_requirement_status_response_from_attributes(self) -> None:
        """CraRequirementStatusResponse can construct from dict."""
        data = {
            "id": "rs-001",
            "assessment_id": "a-001",
            "requirement_id": "CRA-01",
            "status": "partial",
            "auto_mapped": True,
            "mapped_artifact_count": 3,
            "evidence_links": [],
        }
        resp = CraRequirementStatusResponse(**data)
        assert resp.auto_mapped is True
        assert resp.mapped_artifact_count == 3

    def test_compensating_control_response(self) -> None:
        """CompensatingControlResponse validation."""
        data = {
            "id": "cc-001",
            "assessment_id": "a-001",
            "control_id": "CC-DIAG-001",
            "name": "Diagnostic Interface Restriction",
            "implementation_status": "planned",
        }
        resp = CompensatingControlResponse(**data)
        assert resp.control_id == "CC-DIAG-001"

    def test_classification_response(self) -> None:
        """ClassificationResponse validation."""
        data = {
            "classification": "class_i",
            "category_name": "Identity management systems",
            "conformity_assessment": "Module B+C",
            "conformity_module": {
                "module_id": "module_bc",
                "name": "Module B+C",
                "description": "EU-type examination",
                "mandatory": True,
                "alternatives": ["Module H"],
                "rationale": "Class I without harmonised standard",
            },
            "compliance_deadline": "2027-12-11",
            "reporting_deadline": "2026-09-11",
            "cost_estimate_min": 5000,
            "cost_estimate_max": 20000,
            "automotive_exception": False,
            "rationale": "Category CI-01 matched",
        }
        resp = ClassificationResponse(**data)
        assert resp.classification == "class_i"
        assert resp.conformity_module.mandatory is True
        assert resp.reporting_deadline == "2026-09-11"


class TestRouteImports:
    """Verify all CRA route modules import without errors."""

    def test_cra_routes_import(self) -> None:
        """CRA API routes module loads."""
        from api.routes.cra import router
        assert router is not None

    def test_cra_models_import(self) -> None:
        """CRA DB models module loads."""
        from db.cra_models import (
            CraAssessment,
            CraRequirementStatusRecord,
            CraCompensatingControl,
        )
        assert CraAssessment.__tablename__ == "cra_assessments"
        assert CraRequirementStatusRecord.__tablename__ == "cra_requirement_statuses"
        assert CraCompensatingControl.__tablename__ == "cra_compensating_controls"

    def test_report_section_import(self) -> None:
        """CRA report section module loads."""
        from api.services.reporting.sections.cra_compliance_section import (
            build_cra_compliance_section,
        )
        assert callable(build_cra_compliance_section)

    def test_app_includes_cra_routes(self) -> None:
        """FastAPI app has CRA routes registered."""
        from api.app import app
        paths = [r.path for r in app.routes if hasattr(r, "path")]
        cra_paths = [p for p in paths if "/cra" in p]
        assert len(cra_paths) >= 12


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
