"""CRA Art. 14 — incident reporting routes.

Mounts under /api/cra. Endpoints:

  POST   /incidents                          create draft
  GET    /incidents                          list (with computed deadlines)
  GET    /incidents/{id}                     get one
  PUT    /incidents/{id}                     update mutable fields
  POST   /incidents/{id}/submit              mark a phase submitted
  GET    /incidents/{id}/enisa-export        structured Art. 14 export
  DELETE /incidents/{id}                     delete (draft only)
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from api.auth.dependencies import get_current_active_user
from api.deps.db import get_db
from api.models.cra_incident import (
    DeadlineResponse,
    EnisaExportResponse,
    IncidentCreate,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
    SubmitPhaseRequest,
)
from api.models.user import User
from core.cra_incident_deadlines import (
    DeadlinePhase,
    IncidentDeadlines,
    compute_deadlines,
)
from db.cra_incident_models import CraIncident

logger = logging.getLogger(__name__)
router = APIRouter()


# ──────────────────────── helpers ────────────────────────


def _ensure_aware(dt: Optional[datetime]) -> Optional[datetime]:
    """Treat naive datetimes loaded from SQLite as UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _decode_member_states(raw: Optional[str]) -> Optional[List[str]]:
    if not raw:
        return None
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if isinstance(decoded, list):
        return [str(x) for x in decoded]
    return None


def _encode_member_states(values: Optional[List[str]]) -> Optional[str]:
    if values is None:
        return None
    return json.dumps(values)


def _compute(incident: CraIncident) -> IncidentDeadlines:
    return compute_deadlines(
        _ensure_aware(incident.discovered_at),  # type: ignore[arg-type]
        corrective_measure_available_at=_ensure_aware(incident.corrective_measure_available_at),
        early_warning_submitted_at=_ensure_aware(incident.early_warning_submitted_at),
        incident_report_submitted_at=_ensure_aware(incident.incident_report_submitted_at),
        final_report_submitted_at=_ensure_aware(incident.final_report_submitted_at),
    )


def _to_deadline_response_list(d: IncidentDeadlines) -> List[DeadlineResponse]:
    return [
        DeadlineResponse(
            phase=info.phase.value,  # type: ignore[arg-type]
            deadline_at=info.deadline_at,
            seconds_remaining=info.seconds_remaining,
            status=info.status.value,  # type: ignore[arg-type]
            submitted_at=info.submitted_at,
        )
        for info in (d.early_warning, d.incident_report, d.final_report)
    ]


def _build_response(incident: CraIncident) -> IncidentResponse:
    deadlines = _compute(incident)
    payload = IncidentResponse.model_validate(incident)
    payload.member_states_affected = _decode_member_states(incident.member_states_affected)  # type: ignore[arg-type]
    payload.deadlines = _to_deadline_response_list(deadlines)
    payload.overall_overdue = deadlines.overall_overdue
    return payload


def _require_incident(db: Session, incident_id: str) -> CraIncident:
    incident = (
        db.query(CraIncident).filter(CraIncident.id == incident_id).first()
    )
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found"
        )
    return incident


# ──────────────────────── endpoints ────────────────────────


@router.post(
    "/incidents",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> IncidentResponse:
    """CRA Art. 14(1) — open a draft for a reportable event."""
    if payload.discovered_at.tzinfo is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="discovered_at must be timezone-aware (ISO 8601 with offset)",
        )

    now = datetime.now(timezone.utc)
    incident = CraIncident(
        id=str(uuid.uuid4()),
        assessment_id=payload.assessment_id,
        product_id=payload.product_id,
        incident_type=payload.incident_type,
        title=payload.title,
        severity=payload.severity,
        status="draft",
        discovered_at=payload.discovered_at,
        actively_exploited=payload.actively_exploited,
        member_states_affected=_encode_member_states(payload.member_states_affected),
        product_description=payload.product_description,
        cve_id=payload.cve_id,
        notes=payload.notes,
        created_at=now,
        updated_at=now,
        created_by=current_user.email,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return _build_response(incident)


@router.get("/incidents", response_model=IncidentListResponse)
async def list_incidents(
    assessment_id: Optional[str] = None,
    incident_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> IncidentListResponse:
    """List incidents, optionally filtered by assessment or workflow status."""
    query = db.query(CraIncident)
    if assessment_id is not None:
        query = query.filter(CraIncident.assessment_id == assessment_id)
    if incident_status is not None:
        query = query.filter(CraIncident.status == incident_status)
    total = query.count()
    rows = (
        query.order_by(CraIncident.discovered_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return IncidentListResponse(
        incidents=[_build_response(r) for r in rows],
        total=total,
    )


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> IncidentResponse:
    return _build_response(_require_incident(db, incident_id))


@router.put("/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> IncidentResponse:
    incident = _require_incident(db, incident_id)

    update_data = payload.model_dump(exclude_unset=True)

    if "member_states_affected" in update_data:
        incident.member_states_affected = _encode_member_states(
            update_data.pop("member_states_affected")
        )

    for key, value in update_data.items():
        if key == "corrective_measure_available_at" and value is not None:
            if value.tzinfo is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="corrective_measure_available_at must be timezone-aware",
                )
        setattr(incident, key, value)

    incident.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(incident)
    return _build_response(incident)


@router.post("/incidents/{incident_id}/submit", response_model=IncidentResponse)
async def submit_phase(
    incident_id: str,
    payload: SubmitPhaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> IncidentResponse:
    """Mark an Art. 14(2)(a/b/c) phase as submitted to ENISA."""
    incident = _require_incident(db, incident_id)
    now = datetime.now(timezone.utc)

    if payload.phase == "early_warning":
        incident.early_warning_submitted_at = now
        incident.status = "early_warning_submitted"
    elif payload.phase == "incident_report":
        incident.incident_report_submitted_at = now
        if incident.early_warning_submitted_at is None:
            incident.early_warning_submitted_at = now
        incident.status = "incident_report_submitted"
    elif payload.phase == "final_report":
        incident.final_report_submitted_at = now
        if incident.early_warning_submitted_at is None:
            incident.early_warning_submitted_at = now
        if incident.incident_report_submitted_at is None:
            incident.incident_report_submitted_at = now
        incident.status = "final_report_submitted"
        incident.closed_at = now
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unknown phase '{payload.phase}'",
        )

    incident.updated_at = now
    db.commit()
    db.refresh(incident)
    return _build_response(incident)


@router.get(
    "/incidents/{incident_id}/enisa-export",
    response_model=EnisaExportResponse,
)
async def enisa_export(
    incident_id: str,
    phase: str = "early_warning",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> EnisaExportResponse:
    """Structured payload shaped to CRA Art. 14 fields for the chosen phase.

    Until the Commission publishes the Single Reporting Platform schema,
    this is the portable representation of the data the manufacturer would
    submit.
    """
    incident = _require_incident(db, incident_id)
    if phase not in {"early_warning", "incident_report", "final_report"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"unknown phase '{phase}'",
        )

    payload: dict = {
        "regulation": "EU 2024/2847",
        "article": "14",
        "phase": phase,
        "incident": {
            "id": incident.id,
            "title": incident.title,
            "incident_type": incident.incident_type,
            "severity": incident.severity,
            "discovered_at": _ensure_aware(incident.discovered_at).isoformat()  # type: ignore[union-attr]
            if incident.discovered_at
            else None,
            "cve_id": incident.cve_id,
            "product_id": incident.product_id,
        },
        "art_14_2_a": {
            "actively_exploited": bool(incident.actively_exploited),
            "member_states_affected": _decode_member_states(incident.member_states_affected) or [],
            "product_description": incident.product_description,
        },
    }

    if phase in {"incident_report", "final_report"}:
        payload["art_14_2_b"] = {
            "vulnerability_nature": incident.vulnerability_nature,
            "mitigations_taken": incident.mitigations_taken,
            "mitigations_recommended": incident.mitigations_recommended,
        }

    if phase == "final_report":
        payload["art_14_2_c"] = {
            "vulnerability_description": incident.vulnerability_description,
            "impact_description": incident.impact_description,
            "malicious_actor_info": incident.malicious_actor_info,
            "fixes_applied": incident.fixes_applied,
            "corrective_measure_available_at": _ensure_aware(
                incident.corrective_measure_available_at
            ).isoformat()
            if incident.corrective_measure_available_at
            else None,
        }

    return EnisaExportResponse(
        incident_id=incident.id,
        phase=phase,  # type: ignore[arg-type]
        generated_at=datetime.now(timezone.utc),
        payload=payload,
    )


@router.delete(
    "/incidents/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a draft incident. Submitted incidents are not deletable."""
    incident = _require_incident(db, incident_id)
    if incident.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft incidents can be deleted",
        )
    db.delete(incident)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
