"""
Approval Workflow service — state machine for TARA artifact approval.

States: draft → review → approved → released
Supports multi-level sign-off via ApprovalSignoff records.
"""
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from db.audit_models import (
    ApprovalWorkflow, ApprovalSignoff,
    VALID_TRANSITIONS, WORKFLOW_STATES,
)
from core.audit_service import log_change


class WorkflowError(Exception):
    """Raised on invalid workflow transitions."""
    pass


def get_or_create_workflow(
    db: Session,
    artifact_type: str,
    artifact_id: str,
    created_by: str,
    scope_id: Optional[str] = None,
) -> ApprovalWorkflow:
    """Get existing workflow for an artifact, or create a new one in draft."""
    wf = (
        db.query(ApprovalWorkflow)
        .filter(
            ApprovalWorkflow.artifact_type == artifact_type,
            ApprovalWorkflow.artifact_id == artifact_id,
        )
        .first()
    )
    if wf:
        return wf
    wf = ApprovalWorkflow(
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        scope_id=scope_id,
        current_state="draft",
        created_by=created_by,
    )
    db.add(wf)
    db.flush()
    log_change(
        db, artifact_type, artifact_id, "workflow_created",
        performed_by=created_by, scope_id=scope_id,
        new_value="draft", change_summary="Approval workflow created",
    )
    return wf


def transition_state(
    db: Session,
    artifact_type: str,
    artifact_id: str,
    target_state: str,
    performed_by: str,
    notes: Optional[str] = None,
) -> ApprovalWorkflow:
    """Move a workflow to a new state if the transition is valid."""
    if target_state not in WORKFLOW_STATES:
        raise WorkflowError(f"Invalid state: {target_state}")
    wf = (
        db.query(ApprovalWorkflow)
        .filter(
            ApprovalWorkflow.artifact_type == artifact_type,
            ApprovalWorkflow.artifact_id == artifact_id,
        )
        .first()
    )
    if not wf:
        raise WorkflowError("No workflow found for this artifact")
    allowed = VALID_TRANSITIONS.get(wf.current_state, [])
    if target_state not in allowed:
        raise WorkflowError(
            f"Cannot transition from '{wf.current_state}' to '{target_state}'. "
            f"Allowed: {allowed}"
        )
    old_state = wf.current_state
    now = datetime.utcnow()
    wf.current_state = target_state
    wf.updated_at = now
    if target_state == "review":
        wf.submitted_for_review_at = now
        wf.review_notes = notes
    elif target_state == "approved":
        wf.reviewed_at = now
        wf.approved_at = now
        wf.approved_by = performed_by
        wf.approval_notes = notes
    elif target_state == "released":
        wf.released_at = now
        wf.released_by = performed_by
    elif target_state == "draft":
        wf.rejection_reason = notes
    db.flush()
    log_change(
        db, artifact_type, artifact_id, "status_change",
        performed_by=performed_by, scope_id=wf.scope_id,
        field_changed="workflow_state", old_value=old_state,
        new_value=target_state,
        change_summary=f"Workflow: {old_state} → {target_state}",
    )
    return wf


def add_signoff(
    db: Session,
    workflow_id: int,
    signer: str,
    signer_role: str,
    action: str,
    comment: Optional[str] = None,
) -> ApprovalSignoff:
    """Record an individual sign-off on a workflow."""
    if action not in ("approve", "reject", "request_changes"):
        raise WorkflowError(f"Invalid signoff action: {action}")
    signoff = ApprovalSignoff(
        workflow_id=workflow_id,
        signer=signer,
        signer_role=signer_role,
        action=action,
        comment=comment,
    )
    db.add(signoff)
    db.flush()
    return signoff


def get_workflow(
    db: Session, artifact_type: str, artifact_id: str,
) -> Optional[ApprovalWorkflow]:
    """Get the workflow for an artifact."""
    return (
        db.query(ApprovalWorkflow)
        .filter(
            ApprovalWorkflow.artifact_type == artifact_type,
            ApprovalWorkflow.artifact_id == artifact_id,
        )
        .first()
    )


def get_signoffs(db: Session, workflow_id: int) -> List[ApprovalSignoff]:
    """Get all sign-offs for a workflow."""
    return (
        db.query(ApprovalSignoff)
        .filter(ApprovalSignoff.workflow_id == workflow_id)
        .order_by(ApprovalSignoff.signed_at.desc())
        .all()
    )


def list_workflows_by_scope(
    db: Session, scope_id: str, state: Optional[str] = None,
) -> List[ApprovalWorkflow]:
    """List all workflows for a product scope, optionally filtered by state."""
    query = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.scope_id == scope_id,
    )
    if state:
        query = query.filter(ApprovalWorkflow.current_state == state)
    return query.order_by(ApprovalWorkflow.updated_at.desc()).all()
