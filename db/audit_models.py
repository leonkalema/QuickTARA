"""
Audit Trail, Approval Workflow, Evidence Attachment, and TARA Snapshot models.

Implements:
- AuditLog: immutable change history on all artifacts
- ApprovalWorkflow: state machine Draft → Review → Approved → Released
- EvidenceAttachment: file references linked to any artifact
- TaraSnapshot: versioned point-in-time snapshots of the complete TARA
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, Boolean, ForeignKey,
)
from sqlalchemy.types import JSON
from db.base import Base


# ── Audit Log ─────────────────────────────────────────────────────────────

class AuditLog(Base):
    """Immutable change-history record for any TARA artifact."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # What changed
    artifact_type = Column(String(50), nullable=False, index=True)
    artifact_id = Column(String(100), nullable=False, index=True)
    scope_id = Column(String(100), nullable=True, index=True)
    # Action performed
    action = Column(String(30), nullable=False)  # create, update, delete, status_change, approve, reject
    # Who & when
    performed_by = Column(String(100), nullable=False)
    performed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # Change details
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    change_summary = Column(Text, nullable=True)
    # Optional metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)


# ── Approval Workflow ─────────────────────────────────────────────────────

WORKFLOW_STATES = ("draft", "review", "approved", "released")
VALID_TRANSITIONS = {
    "draft": ["review"],
    "review": ["draft", "approved"],
    "approved": ["review", "released"],
    "released": [],  # terminal
}


class ApprovalWorkflow(Base):
    """Tracks the approval state of a TARA artifact through a state machine.

    States: draft → review → approved → released
    """
    __tablename__ = "approval_workflows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Target artifact
    artifact_type = Column(String(50), nullable=False, index=True)
    artifact_id = Column(String(100), nullable=False, index=True)
    scope_id = Column(String(100), nullable=True, index=True)
    # Current state
    current_state = Column(String(20), default="draft", nullable=False)
    # Ownership
    created_by = Column(String(100), nullable=False)
    assigned_reviewer = Column(String(100), nullable=True)
    # Timestamps per state
    submitted_for_review_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    released_at = Column(DateTime, nullable=True)
    # Sign-off tracking
    reviewed_by = Column(String(100), nullable=True)
    approved_by = Column(String(100), nullable=True)
    released_by = Column(String(100), nullable=True)
    # Notes
    review_notes = Column(Text, nullable=True)
    approval_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# ── Approval Sign-off History ─────────────────────────────────────────────

class ApprovalSignoff(Base):
    """Individual sign-off record for multi-level approval chains."""
    __tablename__ = "approval_signoffs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("approval_workflows.id"), nullable=False, index=True)
    # Sign-off details
    signer = Column(String(100), nullable=False)
    signer_role = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)  # approve, reject, request_changes
    comment = Column(Text, nullable=True)
    signed_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# ── Evidence Attachments ──────────────────────────────────────────────────

class EvidenceAttachment(Base):
    """Evidence file reference linked to any TARA artifact.

    Stores metadata only; actual files live on the filesystem or object store.
    """
    __tablename__ = "evidence_attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String(100), unique=True, nullable=False, index=True)
    # Link to artifact
    artifact_type = Column(String(50), nullable=False, index=True)
    artifact_id = Column(String(100), nullable=False, index=True)
    scope_id = Column(String(100), nullable=True, index=True)
    # File metadata
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_hash = Column(String(128), nullable=True)  # SHA-256 for integrity
    # Evidence metadata
    evidence_type = Column(String(50), nullable=False)  # test_report, pen_test, scan_result, design_doc, approval_record
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # Audit
    uploaded_by = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


# ── TARA Snapshots ────────────────────────────────────────────────────────

class TaraSnapshot(Base):
    """Point-in-time versioned snapshot of a complete TARA for a product.

    Captures counts and full JSON export of all artifacts at snapshot time.
    Used for audit, comparison, and regulatory submissions.
    """
    __tablename__ = "tara_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(String(100), unique=True, nullable=False, index=True)
    scope_id = Column(String(100), nullable=False, index=True)
    # Version info
    version = Column(Integer, nullable=False)
    version_label = Column(String(50), nullable=True)  # e.g. "v1.0", "RC-2"
    # Counts at snapshot time
    asset_count = Column(Integer, default=0, nullable=False)
    damage_scenario_count = Column(Integer, default=0, nullable=False)
    threat_scenario_count = Column(Integer, default=0, nullable=False)
    attack_path_count = Column(Integer, default=0, nullable=False)
    risk_treatment_count = Column(Integer, default=0, nullable=False)
    # Full artifact data (JSON blob)
    snapshot_data = Column(JSON, nullable=False)
    # Workflow state at snapshot time
    workflow_state = Column(String(20), nullable=True)
    # Audit
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)
