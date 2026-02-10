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
        """Automotive exception passes through."""
        result = classify_product({}, category_id="CI-01", automotive_exception=True)
        assert result.automotive_exception is True

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
