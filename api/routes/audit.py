"""
Audit Trail, Approval Workflow, Evidence, and TARA Snapshot API routes.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging
import uuid
import os
import hashlib
from datetime import datetime

from api.deps.db import get_db
from api.auth.dependencies import get_current_user
from api.models.user import User
from core.audit_service import get_audit_history, count_audit_entries, log_change
from core.approval_service import (
    get_or_create_workflow, transition_state, add_signoff,
    get_workflow, get_signoffs, list_workflows_by_scope, WorkflowError,
)
from core.workflow_rbac import (
    assert_can_create_workflow, assert_can_transition,
    assert_can_signoff, get_allowed_transitions_for_user,
)
from core.snapshot_service import create_snapshot, get_snapshot, list_snapshots
from db.audit_models import EvidenceAttachment

router = APIRouter()
logger = logging.getLogger(__name__)

EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "evidence_uploads")


# ── Pydantic request/response models ─────────────────────────────────────

class AuditLogResponse(BaseModel):
    id: int
    artifact_type: str
    artifact_id: str
    scope_id: Optional[str] = None
    action: str
    performed_by: str
    performed_at: datetime
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_summary: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int


class WorkflowTransitionRequest(BaseModel):
    target_state: str = Field(..., description="Target state: review, approved, released, draft")
    performed_by: Optional[str] = Field(None, description="Deprecated — identity from JWT")
    notes: Optional[str] = Field(None, description="Transition notes")


class SignoffRequest(BaseModel):
    signer: Optional[str] = Field(None, description="Deprecated — identity from JWT")
    signer_role: str = Field(..., description="Role of the signer")
    action: str = Field(..., description="approve, reject, or request_changes")
    comment: Optional[str] = None


class WorkflowResponse(BaseModel):
    id: int
    artifact_type: str
    artifact_id: str
    scope_id: Optional[str] = None
    current_state: str
    created_by: str
    assigned_reviewer: Optional[str] = None
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    released_by: Optional[str] = None
    review_notes: Optional[str] = None
    approval_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SignoffResponse(BaseModel):
    id: int
    workflow_id: int
    signer: str
    signer_role: str
    action: str
    comment: Optional[str] = None
    signed_at: datetime

    class Config:
        from_attributes = True


class SnapshotCreateRequest(BaseModel):
    scope_id: str = Field(..., description="Product scope ID")
    created_by: str = Field(..., description="Username creating the snapshot")
    version_label: Optional[str] = Field(None, description="Version label e.g. v1.0")
    notes: Optional[str] = None


class SnapshotResponse(BaseModel):
    snapshot_id: str
    scope_id: str
    version: int
    version_label: Optional[str] = None
    asset_count: int
    damage_scenario_count: int
    threat_scenario_count: int
    attack_path_count: int
    risk_treatment_count: int
    workflow_state: Optional[str] = None
    created_by: str
    created_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class SnapshotDetailResponse(SnapshotResponse):
    snapshot_data: Dict[str, Any]


class EvidenceResponse(BaseModel):
    evidence_id: str
    artifact_type: str
    artifact_id: str
    scope_id: Optional[str] = None
    filename: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    evidence_type: str
    title: str
    description: Optional[str] = None
    uploaded_by: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ── Audit Log Endpoints ──────────────────────────────────────────────────

@router.get("/logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    artifact_type: Optional[str] = None,
    artifact_id: Optional[str] = None,
    scope_id: Optional[str] = None,
    performed_by: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List audit log entries with optional filters."""
    logs = get_audit_history(
        db, artifact_type=artifact_type, artifact_id=artifact_id,
        scope_id=scope_id, performed_by=performed_by,
        limit=limit, offset=offset,
    )
    total = count_audit_entries(
        db, artifact_type=artifact_type, artifact_id=artifact_id,
        scope_id=scope_id,
    )
    return AuditLogListResponse(logs=logs, total=total)


@router.get("/logs/{artifact_type}/{artifact_id}", response_model=AuditLogListResponse)
async def get_artifact_audit_log(
    artifact_type: str,
    artifact_id: str,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get audit log for a specific artifact."""
    logs = get_audit_history(
        db, artifact_type=artifact_type, artifact_id=artifact_id, limit=limit,
    )
    total = count_audit_entries(db, artifact_type=artifact_type, artifact_id=artifact_id)
    return AuditLogListResponse(logs=logs, total=total)


# ── Approval Workflow Endpoints ───────────────────────────────────────────

@router.get("/workflows/scope/{scope_id}", response_model=List[WorkflowResponse])
async def list_scope_workflows(
    scope_id: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all workflows for a product scope. Requires authentication."""
    return list_workflows_by_scope(db, scope_id, state)


@router.post("/workflows/{artifact_type}/{artifact_id}", response_model=WorkflowResponse)
async def create_or_get_workflow(
    artifact_type: str,
    artifact_id: str,
    scope_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or retrieve the approval workflow for an artifact. Requires workflows:create."""
    assert_can_create_workflow(current_user)
    wf = get_or_create_workflow(db, artifact_type, artifact_id, current_user.email, scope_id)
    db.commit()
    return wf


@router.get("/workflows/{artifact_type}/{artifact_id}", response_model=WorkflowResponse)
async def get_artifact_workflow(
    artifact_type: str,
    artifact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current workflow state for an artifact. Requires authentication."""
    wf = get_workflow(db, artifact_type, artifact_id)
    if not wf:
        raise HTTPException(status_code=404, detail="No workflow found for this artifact")
    return wf


@router.post("/workflows/{artifact_type}/{artifact_id}/transition", response_model=WorkflowResponse)
async def transition_workflow(
    artifact_type: str,
    artifact_id: str,
    request: WorkflowTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Transition workflow state. Enforces RBAC + separation of duties."""
    wf = get_workflow(db, artifact_type, artifact_id)
    if not wf:
        raise HTTPException(status_code=404, detail="No workflow found for this artifact")
    assert_can_transition(current_user, request.target_state, wf.created_by)
    try:
        wf = transition_state(
            db, artifact_type, artifact_id,
            request.target_state, current_user.email, request.notes,
        )
        db.commit()
        return wf
    except WorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signoffs/{workflow_id}", response_model=SignoffResponse)
async def add_workflow_signoff(
    workflow_id: int,
    request: SignoffRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a sign-off. Requires workflows:signoff permission."""
    assert_can_signoff(current_user)
    try:
        signoff = add_signoff(
            db, workflow_id, current_user.email, request.signer_role,
            request.action, request.comment,
        )
        db.commit()
        return signoff
    except WorkflowError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/signoffs/{workflow_id}", response_model=List[SignoffResponse])
async def list_workflow_signoffs(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all sign-offs for a workflow. Requires authentication."""
    return get_signoffs(db, workflow_id)


# ── TARA Snapshot Endpoints ───────────────────────────────────────────────

@router.post("/snapshots", response_model=SnapshotResponse)
async def create_tara_snapshot(
    request: SnapshotCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a versioned snapshot of the complete TARA for a product."""
    snapshot = create_snapshot(
        db, request.scope_id, request.created_by,
        request.version_label, request.notes,
    )
    db.commit()
    return snapshot


@router.get("/snapshots/{snapshot_id}", response_model=SnapshotDetailResponse)
async def get_tara_snapshot(
    snapshot_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific TARA snapshot with full artifact data."""
    snapshot = get_snapshot(db, snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


@router.get("/snapshots/scope/{scope_id}", response_model=List[SnapshotResponse])
async def list_tara_snapshots(
    scope_id: str,
    db: Session = Depends(get_db),
):
    """List all TARA snapshots for a product scope."""
    return list_snapshots(db, scope_id)


# ── Evidence Attachment Endpoints ─────────────────────────────────────────

@router.post("/evidence", response_model=EvidenceResponse)
async def upload_evidence(
    artifact_type: str = Form(...),
    artifact_id: str = Form(...),
    evidence_type: str = Form(...),
    title: str = Form(...),
    uploaded_by: str = Form(...),
    scope_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload an evidence attachment linked to a TARA artifact."""
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    evidence_id = f"ev_{uuid.uuid4().hex[:8]}"
    safe_filename = f"{evidence_id}_{file.filename}"
    file_path = os.path.join(EVIDENCE_DIR, safe_filename)
    # Read and save file
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    with open(file_path, "wb") as f:
        f.write(content)
    attachment = EvidenceAttachment(
        evidence_id=evidence_id,
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        scope_id=scope_id,
        filename=file.filename,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        file_hash=file_hash,
        evidence_type=evidence_type,
        title=title,
        description=description,
        uploaded_by=uploaded_by,
    )
    db.add(attachment)
    db.flush()
    log_change(
        db, artifact_type, artifact_id, "evidence_attached",
        performed_by=uploaded_by, scope_id=scope_id,
        change_summary=f"Evidence '{title}' attached ({file.filename})",
    )
    db.commit()
    return attachment


@router.get("/evidence/{artifact_type}/{artifact_id}", response_model=List[EvidenceResponse])
async def list_evidence(
    artifact_type: str,
    artifact_id: str,
    db: Session = Depends(get_db),
):
    """List all evidence attachments for an artifact."""
    return (
        db.query(EvidenceAttachment)
        .filter(
            EvidenceAttachment.artifact_type == artifact_type,
            EvidenceAttachment.artifact_id == artifact_id,
            EvidenceAttachment.is_deleted == False,
        )
        .order_by(EvidenceAttachment.uploaded_at.desc())
        .all()
    )


@router.delete("/evidence/{evidence_id}")
async def delete_evidence(
    evidence_id: str,
    deleted_by: str = Query(..., description="Username"),
    db: Session = Depends(get_db),
):
    """Soft-delete an evidence attachment."""
    att = db.query(EvidenceAttachment).filter(
        EvidenceAttachment.evidence_id == evidence_id,
    ).first()
    if not att:
        raise HTTPException(status_code=404, detail="Evidence not found")
    att.is_deleted = True
    log_change(
        db, att.artifact_type, att.artifact_id, "evidence_removed",
        performed_by=deleted_by, scope_id=att.scope_id,
        change_summary=f"Evidence '{att.title}' removed",
    )
    db.commit()
    return {"detail": "Evidence deleted"}
