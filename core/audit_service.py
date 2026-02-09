"""
Audit Trail service — records immutable change history for all TARA artifacts.

Usage:
    from core.audit_service import log_change
    log_change(db, artifact_type="damage_scenario", artifact_id="DS-001",
               action="update", performed_by="analyst@example.com",
               field_changed="severity", old_value="Medium", new_value="High")
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from db.audit_models import AuditLog


def log_change(
    db: Session,
    artifact_type: str,
    artifact_id: str,
    action: str,
    performed_by: str,
    scope_id: Optional[str] = None,
    field_changed: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    change_summary: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Append an immutable audit log entry."""
    entry = AuditLog(
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        scope_id=scope_id,
        action=action,
        performed_by=performed_by,
        performed_at=datetime.utcnow(),
        field_changed=field_changed,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        change_summary=change_summary,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(entry)
    db.flush()
    return entry


def log_bulk_changes(
    db: Session,
    artifact_type: str,
    artifact_id: str,
    action: str,
    performed_by: str,
    changes: Dict[str, tuple],
    scope_id: Optional[str] = None,
) -> List[AuditLog]:
    """Log multiple field changes in one call.

    Args:
        changes: dict of {field_name: (old_value, new_value)}
    """
    entries: List[AuditLog] = []
    for field, (old_val, new_val) in changes.items():
        if str(old_val) != str(new_val):
            entries.append(log_change(
                db, artifact_type, artifact_id, action, performed_by,
                scope_id=scope_id, field_changed=field,
                old_value=old_val, new_value=new_val,
            ))
    return entries


def get_audit_history(
    db: Session,
    artifact_type: Optional[str] = None,
    artifact_id: Optional[str] = None,
    scope_id: Optional[str] = None,
    performed_by: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[AuditLog]:
    """Query audit log with optional filters."""
    query = db.query(AuditLog)
    if artifact_type:
        query = query.filter(AuditLog.artifact_type == artifact_type)
    if artifact_id:
        query = query.filter(AuditLog.artifact_id == artifact_id)
    if scope_id:
        query = query.filter(AuditLog.scope_id == scope_id)
    if performed_by:
        query = query.filter(AuditLog.performed_by == performed_by)
    return (
        query.order_by(AuditLog.performed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def count_audit_entries(
    db: Session,
    artifact_type: Optional[str] = None,
    artifact_id: Optional[str] = None,
    scope_id: Optional[str] = None,
) -> int:
    """Count audit entries with optional filters."""
    query = db.query(AuditLog)
    if artifact_type:
        query = query.filter(AuditLog.artifact_type == artifact_type)
    if artifact_id:
        query = query.filter(AuditLog.artifact_id == artifact_id)
    if scope_id:
        query = query.filter(AuditLog.scope_id == scope_id)
    return query.count()
