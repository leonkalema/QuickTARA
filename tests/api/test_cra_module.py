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
        """0-1 yes answers -> Default category."""
        answers = {f"q{i}": False for i in range(1, 7)}
        result = classify_product(answers)
        assert result.classification == "default"
        assert result.compliance_deadline == "2027-12-11"
        assert result.cost_estimate_max <= 5000

    def test_class_i_classification(self) -> None:
        """2-3 yes answers -> Class I."""
        answers = {"q1": True, "q2": True, "q3": False, "q4": False, "q5": False, "q6": False}
        result = classify_product(answers)
        assert result.classification == "class_i"
        assert result.compliance_deadline == "2026-08-30"

    def test_class_ii_classification(self) -> None:
        """4+ yes answers -> Class II."""
        answers = {"q1": True, "q2": True, "q3": True, "q4": True, "q5": False, "q6": False}
        result = classify_product(answers)
        assert result.classification == "class_ii"
        assert result.compliance_deadline == "2026-10-30"

    def test_class_ii_with_tamper_resistance(self) -> None:
        """3 yes + tamper-resistant -> Class II."""
        answers = {"q1": True, "q2": True, "q3": True, "q4": False, "q5": False, "q6": False}
        result = classify_product(answers)
        assert result.classification == "class_ii"

    def test_critical_classification(self) -> None:
        """All 6 yes + HSM -> Critical."""
        answers = {f"q{i}": True for i in range(1, 7)}
        result = classify_product(answers)
        assert result.classification == "critical"
        assert result.compliance_deadline == "2026-10-30"
        assert result.cost_estimate_min >= 50000

    def test_automotive_exception_flag(self) -> None:
        """Automotive exception passes through."""
        answers = {"q1": True, "q2": True, "q3": False, "q4": False, "q5": False, "q6": False}
        result = classify_product(answers, automotive_exception=True)
        assert result.automotive_exception is True

    def test_result_is_frozen_dataclass(self) -> None:
        """ClassificationResult is immutable."""
        answers = {f"q{i}": False for i in range(1, 7)}
        result = classify_product(answers)
        assert isinstance(result, ClassificationResult)
        with pytest.raises(AttributeError):
            result.classification = "critical"  # type: ignore

    def test_missing_answers_default_to_false(self) -> None:
        """Missing question IDs default to False."""
        result = classify_product({})
        assert result.classification == "default"

    def test_questions_list_has_six_items(self) -> None:
        """Classification questionnaire has exactly 6 questions."""
        assert len(CRA_CLASSIFICATION_QUESTIONS) == 6
        ids = {q["id"] for q in CRA_CLASSIFICATION_QUESTIONS}
        assert ids == {"q1", "q2", "q3", "q4", "q5", "q6"}


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
            "conformity_assessment": "Internal assessment",
            "compliance_deadline": "2026-08-30",
            "cost_estimate_min": 5000,
            "cost_estimate_max": 20000,
            "automotive_exception": False,
            "rationale": "2/6 criteria met",
        }
        resp = ClassificationResponse(**data)
        assert resp.classification == "class_i"


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
