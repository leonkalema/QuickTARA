"""CRA-10 — SBOM upload, list, retrieve, delete.

Mounts under /api/cra. Each endpoint is thin: validate, call core parser,
persist, register CRA-10 evidence, return.

Article references:
  - CRA Art. 13(6) — SBOM obligation
  - Annex I, Part II §1 — manufacturers must identify components
"""
from __future__ import annotations

import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_active_user
from api.deps.db import get_db
from api.models.cra_sbom import (
    SbomComponentResponse,
    SbomDetailResponse,
    SbomListItem,
    SbomUploadResponse,
)
from api.models.user import User
from core.cra_sbom_parser import SbomDocument, parse_sbom
from db.cra_models import CraAssessment, CraRequirementStatusRecord
from db.cra_sbom_models import CraSbom, CraSbomComponent

logger = logging.getLogger(__name__)
router = APIRouter()

# Maximum accepted SBOM payload — guard against pathological uploads.
_MAX_SBOM_BYTES: int = 25 * 1024 * 1024  # 25 MiB
_CRA10_REQUIREMENT_ID: str = "CRA-10"


def _require_assessment(db: Session, assessment_id: str) -> CraAssessment:
    assessment = (
        db.query(CraAssessment).filter(CraAssessment.id == assessment_id).first()
    )
    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRA assessment not found",
        )
    return assessment


def _persist_sbom(
    db: Session,
    assessment: CraAssessment,
    document: SbomDocument,
    uploaded_by: str,
) -> CraSbom:
    sbom = CraSbom(
        id=str(uuid.uuid4()),
        assessment_id=assessment.id,
        sbom_format=document.sbom_format.value,
        spec_version=document.spec_version,
        serial_number=document.serial_number,
        document_name=document.document_name,
        primary_component_name=document.primary_component_name,
        primary_component_version=document.primary_component_version,
        component_count=len(document.components),
        raw_size_bytes=document.raw_size_bytes,
        uploaded_by=uploaded_by,
    )
    db.add(sbom)
    db.flush()  # populate sbom.id

    for comp in document.components:
        db.add(
            CraSbomComponent(
                sbom_id=sbom.id,
                bom_ref=comp.bom_ref,
                name=comp.name,
                version=comp.version,
                component_type=comp.component_type,
                purl=comp.purl,
                cpe=comp.cpe,
                supplier=comp.supplier,
                licenses=",".join(comp.licenses) if comp.licenses else None,
                hashes=";".join(f"{a}={v}" for a, v in comp.hashes) if comp.hashes else None,
            )
        )
    return sbom


def _register_cra10_evidence(
    db: Session, assessment_id: str, sbom_id: str, component_count: int
) -> str:
    """Mark CRA-10 (SBOM requirement) as 'partial' evidence on upload.

    Status is `partial`, not `compliant`: an uploaded SBOM proves the
    artifact exists, but full compliance requires a sign-off (completeness,
    accuracy, supplier disclosure) which only a human reviewer can grant.
    """
    record = (
        db.query(CraRequirementStatusRecord)
        .filter(
            CraRequirementStatusRecord.assessment_id == assessment_id,
            CraRequirementStatusRecord.requirement_id == _CRA10_REQUIREMENT_ID,
        )
        .first()
    )

    note = f"SBOM uploaded ({component_count} components). sbom_id={sbom_id}"

    if record is None:
        record = CraRequirementStatusRecord(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            requirement_id=_CRA10_REQUIREMENT_ID,
            status="partial",
            auto_mapped=True,
            mapped_artifact_type="sbom",
            mapped_artifact_count=1,
            evidence_notes=note,
        )
        db.add(record)
    else:
        if record.status == "not_started":
            record.status = "partial"
        record.auto_mapped = True
        record.mapped_artifact_type = "sbom"
        record.mapped_artifact_count = (record.mapped_artifact_count or 0) + 1
        record.evidence_notes = note
    return record.status


# ──────────────────────── Endpoints ────────────────────────


@router.post(
    "/assessments/{assessment_id}/sboms",
    response_model=SbomUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_sbom(
    assessment_id: str,
    file: UploadFile = File(..., description="CycloneDX 1.4+ or SPDX 2.3 JSON"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SbomUploadResponse:
    """CRA Art. 13(6) — upload an SBOM and auto-map to CRA-10."""
    assessment = _require_assessment(db, assessment_id)

    raw = await file.read()
    if len(raw) > _MAX_SBOM_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"SBOM exceeds maximum size of {_MAX_SBOM_BYTES} bytes",
        )

    result = parse_sbom(raw)
    if result.document is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": list(result.errors), "warnings": list(result.warnings)},
        )

    try:
        sbom = _persist_sbom(db, assessment, result.document, current_user.email)
        cra10_status = _register_cra10_evidence(
            db, assessment.id, sbom.id, len(result.document.components)
        )
        db.commit()
        db.refresh(sbom)
    except Exception:
        db.rollback()
        logger.exception("SBOM persistence failed for assessment %s", assessment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist SBOM",
        )

    return SbomUploadResponse(
        sbom=SbomListItem.model_validate(sbom),
        warnings=list(result.warnings),
        cra10_status=cra10_status,
    )


@router.get(
    "/assessments/{assessment_id}/sboms",
    response_model=List[SbomListItem],
)
async def list_sboms(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[SbomListItem]:
    """List all SBOMs uploaded against an assessment, newest first."""
    _require_assessment(db, assessment_id)
    rows = (
        db.query(CraSbom)
        .filter(CraSbom.assessment_id == assessment_id)
        .order_by(CraSbom.uploaded_at.desc())
        .all()
    )
    return [SbomListItem.model_validate(r) for r in rows]


@router.get(
    "/sboms/{sbom_id}",
    response_model=SbomDetailResponse,
)
async def get_sbom(
    sbom_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SbomDetailResponse:
    """Return one SBOM with its full component list."""
    sbom = db.query(CraSbom).filter(CraSbom.id == sbom_id).first()
    if sbom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SBOM not found",
        )
    payload = SbomDetailResponse.model_validate(sbom)
    payload.components = [
        SbomComponentResponse.model_validate(c) for c in sbom.components
    ]
    return payload


@router.delete(
    "/sboms/{sbom_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_sbom(
    sbom_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an SBOM and its components (cascades via FK)."""
    sbom = db.query(CraSbom).filter(CraSbom.id == sbom_id).first()
    if sbom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SBOM not found",
        )
    db.delete(sbom)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
