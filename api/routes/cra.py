"""
CRA Compliance API Routes

Depends on: db.cra_models, api.models.cra, core.cra_classifier, core.cra_auto_mapper
Used by: api/app.py
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
import uuid
from datetime import datetime

from api.deps.db import get_db
from api.auth.dependencies import get_current_active_user
from api.models.user import User
from api.models.cra import (
    CraAssessmentCreate,
    CraAssessmentUpdate,
    CraAssessmentResponse,
    CraAssessmentListResponse,
    CraAssessmentListItem,
    ClassifyRequest,
    ClassificationResponse,
    ConformityModuleResponse,
    RequirementStatusUpdate,
    CraRequirementStatusResponse,
    CraRequirementDefinition,
    RequirementGuidanceResponse,
    SubRequirementResponse,
    RemediationActionResponse,
    DataProfileUpdate,
    DataProfileResponse,
    ApplicabilityResultResponse,
    CompensatingControlCreate,
    CompensatingControlUpdate,
    CompensatingControlResponse,
    MitigatedRequirementInfo,
    AutoMapResponse,
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    InventorySummary,
)
from db.cra_models import (
    CraAssessment,
    CraRequirementStatusRecord,
    CraCompensatingControl,
    CraControlRequirementLink,
)
from db.product_asset_models import ProductScope
from core.cra_classifier import classify_product, CRA_CLASSIFICATION_QUESTIONS
from core.cra_product_categories import get_all_categories as get_product_categories
from core.cra_auto_mapper import (
    auto_map_tara_to_cra,
    CRA_REQUIREMENTS,
    get_requirement_by_id,
    REQUIREMENT_TO_CONTROLS,
)
import core.cra_requirement_guidance_part2  # noqa: F401 — registers Part II guidance
from core.cra_requirement_guidance import get_guidance, get_all_guidance
from core.cra_data_classifier import (
    compute_applicability,
    get_questions as get_data_questions,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _generate_id() -> str:
    return str(uuid.uuid4())


def _enrich_requirement_status(
    record: CraRequirementStatusRecord,
) -> dict:
    """Add requirement definition fields to a status record."""
    data = {
        "id": record.id,
        "assessment_id": record.assessment_id,
        "requirement_id": record.requirement_id,
        "status": record.status,
        "auto_mapped": record.auto_mapped,
        "mapped_artifact_type": record.mapped_artifact_type,
        "mapped_artifact_count": record.mapped_artifact_count or 0,
        "owner": record.owner,
        "target_date": record.target_date,
        "evidence_notes": record.evidence_notes,
        "evidence_links": record.evidence_links or [],
        "gap_description": record.gap_description,
        "remediation_plan": record.remediation_plan,
        "gap_severity": getattr(record, 'gap_severity', 'none') or 'none',
        "residual_risk_level": getattr(record, 'residual_risk_level', 'none') or 'none',
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }
    req_def = get_requirement_by_id(record.requirement_id)
    if req_def:
        data["requirement_name"] = req_def["name"]
        data["requirement_article"] = req_def["article"]
        data["requirement_category"] = req_def["category"]
        data["annex_part"] = req_def.get("annex_part", "Part I")
        data["obligation_type"] = req_def.get("obligation_type", "risk_based")
    return data


def _build_control_response(control: CraCompensatingControl, db: Session) -> dict:
    """Build control response with mitigated requirements."""
    mitigated = []
    for link in control.mitigated_requirements:
        req_status = db.query(CraRequirementStatusRecord).filter(
            CraRequirementStatusRecord.id == link.requirement_status_id
        ).first()
        if req_status:
            req_def = get_requirement_by_id(req_status.requirement_id)
            mitigated.append(MitigatedRequirementInfo(
                requirement_status_id=req_status.id,
                requirement_id=req_status.requirement_id,
                requirement_name=req_def["name"] if req_def else None,
            ))
    return {
        "id": control.id,
        "assessment_id": control.assessment_id,
        "control_id": control.control_id,
        "name": control.name,
        "description": control.description,
        "implementation_status": control.implementation_status,
        "supplier_actions": control.supplier_actions,
        "oem_actions": control.oem_actions,
        "residual_risk": control.residual_risk,
        "mitigated_requirements": mitigated,
        "created_at": control.created_at,
        "updated_at": control.updated_at,
    }


def _compute_compliance_pct(assessment: CraAssessment) -> int:
    """Calculate overall compliance percentage from requirement statuses."""
    statuses = assessment.requirement_statuses
    if not statuses:
        return 0
    compliant = sum(
        1 for s in statuses
        if s.status in ("compliant", "not_applicable")
    )
    return int((compliant / len(statuses)) * 100)


def _build_assessment_response(
    assessment: CraAssessment,
    product_name: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    """Build a full assessment response dict."""
    enriched_reqs = [
        _enrich_requirement_status(rs)
        for rs in assessment.requirement_statuses
    ]
    # Build controls with mitigated requirements properly serialized
    controls = []
    for cc in assessment.compensating_controls:
        if db:
            controls.append(_build_control_response(cc, db))
        else:
            # Fallback without mitigated_requirements
            controls.append({
                "id": cc.id,
                "assessment_id": cc.assessment_id,
                "control_id": cc.control_id,
                "name": cc.name,
                "description": cc.description,
                "implementation_status": cc.implementation_status,
                "supplier_actions": cc.supplier_actions,
                "oem_actions": cc.oem_actions,
                "residual_risk": cc.residual_risk,
                "mitigated_requirements": [],
                "created_at": cc.created_at,
                "updated_at": cc.updated_at,
            })
    return {
        "id": assessment.id,
        "product_id": assessment.product_id,
        "product_name": product_name,
        "classification": assessment.classification,
        "classification_answers": assessment.classification_answers or {},
        "product_type": assessment.product_type,
        "compliance_path": getattr(assessment, 'compliance_path', 'direct_patch') or 'direct_patch',
        "compliance_deadline": assessment.compliance_deadline,
        "assessment_date": assessment.assessment_date,
        "assessor_id": assessment.assessor_id,
        "status": assessment.status,
        "overall_compliance_pct": assessment.overall_compliance_pct or 0,
        "support_period_years": getattr(assessment, 'support_period_years', None),
        "support_period_justification": getattr(assessment, 'support_period_justification', None),
        "support_period_end": assessment.support_period_end,
        "eoss_date": assessment.eoss_date,
        "notes": assessment.notes,
        "automotive_exception": bool(assessment.automotive_exception),
        "data_profile": assessment.data_profile or {},
        "created_at": assessment.created_at,
        "updated_at": assessment.updated_at,
        "requirement_statuses": enriched_reqs,
        "compensating_controls": controls,
    }


# ──────────────────────── Assessment CRUD ────────────────────────


@router.post(
    "/assessments",
    response_model=CraAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assessment(
    payload: CraAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a CRA assessment for a product and seed 18 requirement rows."""
    product = db.query(ProductScope).filter(
        ProductScope.scope_id == payload.product_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {payload.product_id} not found",
        )
    existing = db.query(CraAssessment).filter(
        CraAssessment.product_id == payload.product_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CRA assessment already exists for this product",
        )

    assessment = CraAssessment(
        id=_generate_id(),
        product_id=payload.product_id,
        product_type=payload.product_type.value,
        notes=payload.notes,
        assessor_id=current_user.user_id,
        status="draft",
    )
    db.add(assessment)

    for req in CRA_REQUIREMENTS:
        db.add(CraRequirementStatusRecord(
            id=_generate_id(),
            assessment_id=assessment.id,
            requirement_id=req["id"],
            status="not_started",
        ))

    db.commit()
    db.refresh(assessment)
    logger.info("Created CRA assessment %s for product %s", assessment.id, payload.product_id)
    return _build_assessment_response(assessment, product.name, db)


@router.get(
    "/assessments/{assessment_id}",
    response_model=CraAssessmentResponse,
)
async def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a CRA assessment by ID."""
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    product = db.query(ProductScope).filter(
        ProductScope.scope_id == assessment.product_id
    ).first()
    product_name = product.name if product else None
    return _build_assessment_response(assessment, product_name, db)


@router.get(
    "/assessments/product/{product_id}",
    response_model=CraAssessmentResponse,
)
async def get_assessment_by_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a CRA assessment by product ID."""
    assessment = db.query(CraAssessment).filter(
        CraAssessment.product_id == product_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="No CRA assessment for this product")
    product = db.query(ProductScope).filter(
        ProductScope.scope_id == product_id
    ).first()
    product_name = product.name if product else None
    return _build_assessment_response(assessment, product_name, db)


@router.get(
    "/assessments",
    response_model=CraAssessmentListResponse,
)
async def list_assessments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all CRA assessments."""
    query = db.query(CraAssessment)
    total = query.count()
    assessments = query.offset(skip).limit(limit).all()
    items = []
    for a in assessments:
        product = db.query(ProductScope).filter(
            ProductScope.scope_id == a.product_id
        ).first()
        items.append(CraAssessmentListItem(
            id=a.id,
            product_id=a.product_id,
            product_name=product.name if product else None,
            classification=a.classification,
            product_type=a.product_type,
            status=a.status,
            overall_compliance_pct=a.overall_compliance_pct or 0,
            compliance_deadline=a.compliance_deadline,
            updated_at=a.updated_at,
        ))
    return {"assessments": items, "total": total}


@router.put(
    "/assessments/{assessment_id}",
    response_model=CraAssessmentResponse,
)
async def update_assessment(
    assessment_id: str,
    payload: CraAssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a CRA assessment."""
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    update_data = payload.model_dump(exclude_unset=True)
    sp_years = update_data.get("support_period_years")
    if sp_years is not None and sp_years < 5:
        justification = update_data.get("support_period_justification", "")
        if not justification or len(justification.strip()) < 10:
            raise HTTPException(
                status_code=422,
                detail=(
                    "CRA requires a minimum 5-year support period. "
                    "A support period shorter than 5 years requires a "
                    "documented justification (e.g. product expected to "
                    "be in use less than 5 years)."
                ),
            )
    for key, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(assessment, key, value)
    assessment.updated_at = datetime.now()
    db.commit()
    db.refresh(assessment)
    product = db.query(ProductScope).filter(
        ProductScope.scope_id == assessment.product_id
    ).first()
    return _build_assessment_response(assessment, product.name if product else None, db)


@router.delete(
    "/assessments/{assessment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a CRA assessment and all related records."""
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    db.delete(assessment)
    db.commit()
    logger.info("Deleted CRA assessment %s", assessment_id)


# ──────────────────────── Product Categories ────────────────────────


@router.get("/product-categories")
async def list_product_categories():
    """Return all CRA product categories from Annexes III/IV for classification UI."""
    categories = get_product_categories()
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "classification": cat.classification,
            "description": cat.description,
            "examples": cat.examples,
            "annex_ref": cat.annex_ref,
        }
        for cat in categories
    ]


# ──────────────────────── Classification ────────────────────────


@router.post(
    "/assessments/{assessment_id}/classify",
    response_model=ClassificationResponse,
)
async def classify_assessment(
    assessment_id: str,
    payload: ClassifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Classify product by core functionality category per EU 2025/2392."""
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    result = classify_product(
        answers=payload.answers,
        automotive_exception=payload.automotive_exception,
        category_id=payload.category_id,
        uses_harmonised_standard=payload.uses_harmonised_standard,
        is_open_source_public=payload.is_open_source_public,
    )
    classification_data = {
        "category_id": payload.category_id,
        "uses_harmonised_standard": payload.uses_harmonised_standard,
        "is_open_source_public": payload.is_open_source_public,
        **payload.answers,
    }
    assessment.classification = result.classification
    assessment.classification_answers = classification_data
    assessment.compliance_deadline = result.compliance_deadline
    assessment.automotive_exception = result.automotive_exception
    assessment.status = "in_progress"
    assessment.updated_at = datetime.now()
    db.commit()
    logger.info(
        "Classified assessment %s as %s (category: %s)",
        assessment_id, result.classification, result.category_name,
    )
    cm = result.conformity_module
    return ClassificationResponse(
        classification=result.classification,
        category_id=result.category_id,
        category_name=result.category_name,
        conformity_assessment=result.conformity_assessment,
        conformity_module=ConformityModuleResponse(
            module_id=cm.module_id,
            name=cm.name,
            description=cm.description,
            mandatory=cm.mandatory,
            alternatives=list(cm.alternatives),
            rationale=cm.rationale,
        ),
        compliance_deadline=result.compliance_deadline,
        reporting_deadline=result.reporting_deadline,
        cost_estimate_min=result.cost_estimate_min,
        cost_estimate_max=result.cost_estimate_max,
        automotive_exception=result.automotive_exception,
        rationale=result.rationale,
    )


# ──────────────────────── Auto-Mapping ────────────────────────


@router.post(
    "/assessments/{assessment_id}/auto-map",
    response_model=AutoMapResponse,
)
async def auto_map_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Auto-map existing TARA artifacts to CRA requirements."""
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    mappings = auto_map_tara_to_cra(db, assessment.product_id)
    mapping_dicts = []

    for mapping in mappings:
        req_status = db.query(CraRequirementStatusRecord).filter(
            CraRequirementStatusRecord.assessment_id == assessment_id,
            CraRequirementStatusRecord.requirement_id == mapping.requirement_id,
        ).first()
        if req_status:
            req_status.status = mapping.status
            req_status.auto_mapped = True
            req_status.mapped_artifact_type = mapping.artifact_type
            req_status.mapped_artifact_count = mapping.artifact_count
            req_status.evidence_notes = mapping.evidence_notes
            req_status.updated_at = datetime.now()

        mapping_dicts.append({
            "requirement_id": mapping.requirement_id,
            "status": mapping.status,
            "artifact_type": mapping.artifact_type,
            "artifact_count": mapping.artifact_count,
            "evidence_notes": mapping.evidence_notes,
        })

    assessment.overall_compliance_pct = _compute_compliance_pct(assessment)
    assessment.updated_at = datetime.now()
    db.commit()

    logger.info(
        "Auto-mapped %d requirements for assessment %s",
        len(mappings), assessment_id,
    )
    return {"mapped_count": len(mappings), "mappings": mapping_dicts}


# ──────────────────────── Data Classification ────────────────────────


@router.get("/data-classification-questions")
async def get_data_classification_questions():
    """Return the list of data profile questions for the UI."""
    return get_data_questions()


@router.get(
    "/assessments/{assessment_id}/data-profile",
    response_model=DataProfileResponse,
)
async def get_data_profile(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get the current data profile and computed applicability."""
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    profile = assessment.data_profile or {}
    results = compute_applicability(profile)
    na_count = sum(1 for r in results if not r.applicable)
    return DataProfileResponse(
        profile=profile,
        applicability=[
            ApplicabilityResultResponse(
                requirement_id=r.requirement_id,
                applicable=r.applicable,
                justification=r.justification,
            )
            for r in results
        ],
        auto_resolved_count=na_count,
    )


@router.put(
    "/assessments/{assessment_id}/data-profile",
    response_model=DataProfileResponse,
)
async def update_data_profile(
    assessment_id: str,
    payload: DataProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Save data profile and auto-resolve non-applicable requirements."""
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    profile = payload.model_dump(exclude_unset=False)
    profile = {k: bool(v) for k, v in profile.items() if v is not None}
    assessment.data_profile = profile
    assessment.updated_at = datetime.now()
    results = compute_applicability(profile)
    na_count = 0
    for r in results:
        if not r.applicable:
            req_status = db.query(CraRequirementStatusRecord).filter(
                CraRequirementStatusRecord.assessment_id == assessment_id,
                CraRequirementStatusRecord.requirement_id == r.requirement_id,
            ).first()
            if req_status and req_status.status != "not_applicable":
                req_status.status = "not_applicable"
                req_status.evidence_notes = r.justification
                req_status.updated_at = datetime.now()
            na_count += 1
    db.flush()
    db.expire(assessment, ["requirement_statuses"])
    assessment.overall_compliance_pct = _compute_compliance_pct(assessment)
    db.commit()
    logger.info(
        "Data profile saved for %s — %d requirements auto-resolved as N/A",
        assessment_id, na_count,
    )
    return DataProfileResponse(
        profile=profile,
        applicability=[
            ApplicabilityResultResponse(
                requirement_id=r.requirement_id,
                applicable=r.applicable,
                justification=r.justification,
            )
            for r in results
        ],
        auto_resolved_count=na_count,
    )


# ──────────────────────── Requirement Statuses ────────────────────────


@router.get("/requirements")
async def get_requirements():
    """Get the master list of 18 CRA requirements."""
    return [
        CraRequirementDefinition(**req)
        for req in CRA_REQUIREMENTS
    ]


def _serialize_guidance(g) -> RequirementGuidanceResponse:
    """Convert a RequirementGuidance dataclass to Pydantic response."""
    return RequirementGuidanceResponse(
        requirement_id=g.requirement_id,
        annex_section=g.annex_section,
        cra_article=g.cra_article,
        priority=g.priority,
        deadline_note=g.deadline_note,
        explanation=g.explanation,
        regulatory_text=g.regulatory_text,
        sub_requirements=[
            SubRequirementResponse(
                description=s.description,
                check_evidence=s.check_evidence,
                typical_gap=s.typical_gap,
            )
            for s in g.sub_requirements
        ],
        evidence_checklist=list(g.evidence_checklist),
        investigation_prompts=list(g.investigation_prompts),
        common_gaps=list(g.common_gaps),
        remediation_actions=[
            RemediationActionResponse(
                action=a.action,
                owner_hint=a.owner_hint,
                effort_days=a.effort_days,
            )
            for a in g.remediation_actions
        ],
        effort_estimate=g.effort_estimate,
        mapped_controls=list(g.mapped_controls),
        mapped_standards=list(g.mapped_standards),
        tara_link=g.tara_link,
    )


@router.get(
    "/guidance",
    response_model=List[RequirementGuidanceResponse],
)
async def get_all_requirement_guidance():
    """Return coaching guidance for all 18 CRA requirements."""
    all_guidance = get_all_guidance()
    return [_serialize_guidance(g) for g in all_guidance.values()]


@router.get(
    "/guidance/{requirement_id}",
    response_model=RequirementGuidanceResponse,
)
async def get_requirement_guidance(requirement_id: str):
    """Return coaching guidance for a single CRA requirement."""
    g = get_guidance(requirement_id)
    if not g:
        raise HTTPException(status_code=404, detail=f"No guidance for {requirement_id}")
    return _serialize_guidance(g)


@router.put(
    "/requirements/{status_id}",
    response_model=CraRequirementStatusResponse,
)
async def update_requirement_status(
    status_id: str,
    payload: RequirementStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a single requirement status."""
    record = db.query(CraRequirementStatusRecord).filter(
        CraRequirementStatusRecord.id == status_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Requirement status not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(record, key, value)
    record.updated_at = datetime.now()

    # Flush so the updated record is visible through relationships
    db.flush()
    # Recalculate overall compliance
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == record.assessment_id
    ).first()
    if assessment:
        db.expire(assessment, ["requirement_statuses"])
        assessment.overall_compliance_pct = _compute_compliance_pct(assessment)
        assessment.updated_at = datetime.now()

    db.commit()
    db.refresh(record)
    return _enrich_requirement_status(record)


# ──────────────────────── Compensating Controls ────────────────────────


@router.get(
    "/compensating-controls/{assessment_id}",
    response_model=List[CompensatingControlResponse],
)
async def get_compensating_controls(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get compensating controls for a legacy product assessment."""
    controls = db.query(CraCompensatingControl).filter(
        CraCompensatingControl.assessment_id == assessment_id
    ).all()
    return [_build_control_response(c, db) for c in controls]


@router.post(
    "/compensating-controls",
    response_model=CompensatingControlResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_compensating_control(
    payload: CompensatingControlCreate,
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a compensating control to an assessment."""
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    control = CraCompensatingControl(
        id=_generate_id(),
        assessment_id=assessment_id,
        control_id=payload.control_id,
        name=payload.name,
        description=payload.description,
        implementation_status=payload.implementation_status.value,
        supplier_actions=payload.supplier_actions,
        oem_actions=payload.oem_actions,
        residual_risk=payload.residual_risk,
    )
    db.add(control)
    db.flush()

    # Add mitigated requirement links
    if payload.mitigated_requirement_ids:
        for req_id in payload.mitigated_requirement_ids:
            link = CraControlRequirementLink(
                control_id=control.id,
                requirement_status_id=req_id,
            )
            db.add(link)

    db.commit()
    db.refresh(control)
    logger.info("Created compensating control %s for assessment %s", control.id, assessment_id)
    return _build_control_response(control, db)


@router.put(
    "/compensating-controls/{control_id}",
    response_model=CompensatingControlResponse,
)
async def update_compensating_control(
    control_id: str,
    payload: CompensatingControlUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a compensating control."""
    control = db.query(CraCompensatingControl).filter(
        CraCompensatingControl.id == control_id
    ).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")

    update_data = payload.model_dump(exclude_unset=True)
    mitigated_req_ids = update_data.pop("mitigated_requirement_ids", None)

    for key, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(control, key, value)
    control.updated_at = datetime.now()

    # Update mitigated requirements if provided
    if mitigated_req_ids is not None:
        # Remove existing links
        db.query(CraControlRequirementLink).filter(
            CraControlRequirementLink.control_id == control_id
        ).delete()
        # Add new links
        for req_id in mitigated_req_ids:
            link = CraControlRequirementLink(
                control_id=control_id,
                requirement_status_id=req_id,
            )
            db.add(link)

    db.commit()
    db.refresh(control)
    return _build_control_response(control, db)


@router.delete("/compensating-controls/{control_id}")
async def delete_compensating_control(
    control_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a compensating control."""
    control = db.query(CraCompensatingControl).filter(
        CraCompensatingControl.id == control_id
    ).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")

    db.delete(control)
    db.commit()
    return {"deleted": True, "id": control_id}


@router.get("/classification-questions")
async def get_classification_questions():
    """Get the 6 classification questions + automotive exception question."""
    return {
        "questions": CRA_CLASSIFICATION_QUESTIONS,
        "automotive_exception_question": {
            "id": "auto_exception",
            "text": "Is this product sold exclusively to one OEM for vehicle type-approval under UN R155?",
            "hint": "If yes, CRA may not apply (lex specialis). Compliance still recommended.",
        },
    }


@router.get("/compensating-controls-catalog")
async def get_compensating_controls_catalog():
    """Get the pre-approved compensating controls catalog for legacy products."""
    from core.cra_compensating_controls_catalog import get_catalog
    return get_catalog()


# ──────────────────────── Automated Gap Analysis ────────────────────────


@router.get("/assessments/{assessment_id}/gap-analysis")
async def get_gap_analysis(
    assessment_id: str,
    db: Session = Depends(get_db),
):
    """
    Gap analysis based on the assessment's requirement statuses.

    Source of truth: requirement_statuses set by the user.
    - Compliant / N/A → covered
    - Not Started / Partial → gap
    - For legacy products: suggests compensating controls
    - For TARA products: shows linked TARA artifacts
    """
    assessment = db.query(CraAssessment).filter(
        CraAssessment.id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    is_legacy = assessment.product_type in ("legacy_b", "legacy_c")
    classification = assessment.classification or "default"
    classification_risk = {
        "critical": "critical", "class_ii": "high",
        "class_i": "medium", "default": "low",
    }
    base_risk = classification_risk.get(classification, "medium")
    existing_controls = db.query(CraCompensatingControl).filter(
        CraCompensatingControl.assessment_id == assessment_id
    ).all()
    control_links = db.query(CraControlRequirementLink).filter(
        CraControlRequirementLink.control_id.in_(
            [c.id for c in existing_controls]
        )
    ).all() if existing_controls else []
    req_to_controls = {}
    for link in control_links:
        ctrl = next((c for c in existing_controls if c.id == link.control_id), None)
        if ctrl:
            req_to_controls.setdefault(link.requirement_status_id, []).append({
                "control_id": ctrl.control_id,
                "name": ctrl.name,
                "status": ctrl.implementation_status,
            })
    gaps = []
    for req_status in assessment.requirement_statuses:
        is_compliant = req_status.status in ("compliant", "not_applicable")
        req_def = get_requirement_by_id(req_status.requirement_id) or {}
        applied_controls = req_to_controls.get(req_status.id, [])
        has_verified_control = any(
            c["status"] == "verified" for c in applied_controls
        )
        has_implemented_control = any(
            c["status"] == "implemented" for c in applied_controls
        )
        if is_compliant:
            risk_level = "none"
        elif has_verified_control:
            risk_level = "low"
        elif has_implemented_control:
            risk_level = "medium" if base_risk in ("high", "critical") else "low"
        else:
            risk_level = base_risk
        suggested = []
        if not is_compliant and is_legacy:
            suggested = REQUIREMENT_TO_CONTROLS.get(
                req_status.requirement_id, []
            )
        tara_evidence = []
        if req_status.auto_mapped and req_status.mapped_artifact_type:
            tara_evidence.append({
                "type": req_status.mapped_artifact_type,
                "count": req_status.mapped_artifact_count or 0,
                "notes": req_status.evidence_notes or "",
            })
        guidance = get_guidance(req_status.requirement_id)
        annex_part = req_def.get("annex_part", "Part I")
        obligation_type = req_def.get("obligation_type", "risk_based")
        gap_item: dict = {
            "requirement_status_id": req_status.id,
            "requirement_id": req_status.requirement_id,
            "requirement_name": req_def.get("name", req_status.requirement_id),
            "category": req_def.get("category", "technical"),
            "article": req_def.get("article", ""),
            "annex_part": annex_part,
            "obligation_type": obligation_type,
            "status": req_status.status,
            "is_gap": not is_compliant,
            "risk_level": risk_level,
            "suggested_controls": suggested,
            "applied_controls": applied_controls,
            "tara_evidence": tara_evidence,
            "owner": req_status.owner,
            "target_date": req_status.target_date,
            "evidence_notes": req_status.evidence_notes or "",
        }
        if guidance:
            gap_item["guidance"] = {
                "priority": guidance.priority,
                "deadline_note": guidance.deadline_note,
                "effort_estimate": guidance.effort_estimate,
                "cra_article": guidance.cra_article,
                "explanation": guidance.explanation,
                "common_gaps": list(guidance.common_gaps),
                "sub_requirements": [
                    {
                        "description": s.description,
                        "check_evidence": s.check_evidence,
                        "typical_gap": s.typical_gap,
                    }
                    for s in guidance.sub_requirements
                ],
                "remediation_actions": [
                    {
                        "action": a.action,
                        "owner_hint": a.owner_hint,
                        "effort_days": a.effort_days,
                    }
                    for a in guidance.remediation_actions
                ],
                "mapped_standards": list(guidance.mapped_standards),
            }
        gaps.append(gap_item)
    gap_items = [g for g in gaps if g["is_gap"]]
    mitigated = sum(
        1 for g in gap_items
        if g["applied_controls"] and g["risk_level"] in ("low", "none")
    )
    unmitigated = sum(
        1 for g in gap_items
        if g["risk_level"] in ("high", "critical") and not g["applied_controls"]
    )
    total_effort = sum(
        a["effort_days"]
        for g in gap_items
        if g.get("guidance")
        for a in g["guidance"].get("remediation_actions", [])
    )
    risk_reduction_pct = (
        int((mitigated / len(gap_items)) * 100) if gap_items else 0
    )
    return {
        "assessment_id": assessment_id,
        "product_id": assessment.product_id,
        "product_type": assessment.product_type,
        "classification": classification,
        "is_legacy": is_legacy,
        "requirements": gaps,
        "summary": {
            "total": len(gaps),
            "compliant": sum(1 for g in gaps if not g["is_gap"]),
            "gaps": len(gap_items),
            "critical_risk": sum(1 for g in gap_items if g["risk_level"] == "critical"),
            "high_risk": sum(1 for g in gap_items if g["risk_level"] == "high"),
            "with_controls": sum(1 for g in gap_items if g["applied_controls"]),
            "mitigated": mitigated,
            "unmitigated": unmitigated,
            "total_remediation_effort_days": total_effort,
            "risk_reduction_pct": risk_reduction_pct,
        },
    }


# ──────────────────────── Inventory CRUD ────────────────────────


@router.get("/inventory/{assessment_id}")
async def get_inventory(
    assessment_id: str,
    db: Session = Depends(get_db),
):
    """Get all inventory items for an assessment."""
    from db.cra_models import CraInventoryItem
    items = db.query(CraInventoryItem).filter(
        CraInventoryItem.assessment_id == assessment_id
    ).all()
    return [InventoryItemResponse.model_validate(item) for item in items]


@router.get("/inventory/{assessment_id}/summary")
async def get_inventory_summary(
    assessment_id: str,
    db: Session = Depends(get_db),
):
    """Get inventory summary for an assessment."""
    from db.cra_models import CraInventoryItem
    items = db.query(CraInventoryItem).filter(
        CraInventoryItem.assessment_id == assessment_id
    ).all()
    
    eu_units = sum(i.units_in_stock + i.units_in_field for i in items if i.target_market == 'eu')
    non_eu_units = sum(i.units_in_stock + i.units_in_field for i in items if i.target_market != 'eu')
    oems = list(set(i.oem_customer for i in items if i.oem_customer))
    
    return InventorySummary(
        total_skus=len(items),
        total_units_in_stock=sum(i.units_in_stock for i in items),
        total_units_in_field=sum(i.units_in_field for i in items),
        eu_units=eu_units,
        non_eu_units=non_eu_units,
        oems=oems,
    )


@router.post("/inventory", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    payload: InventoryItemCreate,
    db: Session = Depends(get_db),
):
    """Create a new inventory item."""
    from db.cra_models import CraInventoryItem
    import uuid
    
    item = CraInventoryItem(
        id=str(uuid.uuid4()),
        assessment_id=payload.assessment_id,
        sku=payload.sku,
        firmware_version=payload.firmware_version,
        units_in_stock=payload.units_in_stock,
        units_in_field=payload.units_in_field,
        oem_customer=payload.oem_customer,
        target_market=payload.target_market.value if payload.target_market else 'eu',
        last_production_date=payload.last_production_date,
        notes=payload.notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return InventoryItemResponse.model_validate(item)


@router.put("/inventory/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: str,
    payload: InventoryItemUpdate,
    db: Session = Depends(get_db),
):
    """Update an inventory item."""
    from db.cra_models import CraInventoryItem
    
    item = db.query(CraInventoryItem).filter(CraInventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    if 'target_market' in update_data and update_data['target_market']:
        update_data['target_market'] = update_data['target_market'].value
    
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return InventoryItemResponse.model_validate(item)


@router.delete("/inventory/{item_id}")
async def delete_inventory_item(
    item_id: str,
    db: Session = Depends(get_db),
):
    """Delete an inventory item."""
    from db.cra_models import CraInventoryItem
    
    item = db.query(CraInventoryItem).filter(CraInventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    db.delete(item)
    db.commit()
    return {"deleted": True, "id": item_id}
