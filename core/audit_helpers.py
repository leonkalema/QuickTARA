"""
Lightweight audit logging helpers for CRUD route handlers.
Wraps core.audit_service to provide a simple interface for route-level logging.
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Request

from core.audit_service import log_change


def get_user_from_request(request: Request) -> str:
    """Extract username from JWT auth header if present, else 'system'."""
    try:
        from api.auth.security import security_manager, extract_user_from_token
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = security_manager.verify_token(token)
            user_data = extract_user_from_token(payload)
            return user_data.get("email", user_data.get("user_id", "system"))
    except Exception:
        pass
    return "system"


def audit_create(
    db: Session,
    artifact_type: str,
    artifact_id: str,
    performed_by: str,
    scope_id: Optional[str] = None,
    summary: Optional[str] = None,
) -> None:
    """Log a create action. Safe to call — never raises."""
    try:
        log_change(
            db=db,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            action="create",
            performed_by=performed_by,
            scope_id=scope_id,
            change_summary=summary or f"{artifact_type} created",
        )
    except Exception:
        pass


def audit_update(
    db: Session,
    artifact_type: str,
    artifact_id: str,
    performed_by: str,
    scope_id: Optional[str] = None,
    field_changed: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    summary: Optional[str] = None,
) -> None:
    """Log an update action. Safe to call — never raises."""
    try:
        log_change(
            db=db,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            action="update",
            performed_by=performed_by,
            scope_id=scope_id,
            field_changed=field_changed,
            old_value=old_value,
            new_value=new_value,
            change_summary=summary or f"{artifact_type} updated",
        )
    except Exception:
        pass


def audit_delete(
    db: Session,
    artifact_type: str,
    artifact_id: str,
    performed_by: str,
    scope_id: Optional[str] = None,
    summary: Optional[str] = None,
) -> None:
    """Log a delete action. Safe to call — never raises."""
    try:
        log_change(
            db=db,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            action="delete",
            performed_by=performed_by,
            scope_id=scope_id,
            change_summary=summary or f"{artifact_type} deleted",
        )
    except Exception:
        pass


def audit_status_change(
    db: Session,
    artifact_type: str,
    artifact_id: str,
    performed_by: str,
    old_status: str,
    new_status: str,
    scope_id: Optional[str] = None,
) -> None:
    """Log a status change. Safe to call — never raises."""
    try:
        log_change(
            db=db,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            action="status_change",
            performed_by=performed_by,
            scope_id=scope_id,
            field_changed="status",
            old_value=old_status,
            new_value=new_status,
            change_summary=f"Status: {old_status} → {new_status}",
        )
    except Exception:
        pass
