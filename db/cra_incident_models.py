"""CRA Art. 14 — incident reporting persistence model.

One row per incident or actively-exploited vulnerability that triggers
the 24h / 72h / 14d ENISA reporting obligation.

Optional FK to a CRA assessment (an incident may be reported even before
an assessment exists for the affected product).
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from db.product_asset_models import Base


class CraIncident(Base):
    """A reportable CRA Art. 14 incident or actively-exploited vulnerability."""

    __tablename__ = "cra_incidents"
    __table_args__ = (
        Index("ix_cra_incidents_status", "status"),
        Index("ix_cra_incidents_discovered_at", "discovered_at"),
        Index("ix_cra_incidents_assessment_id", "assessment_id"),
    )

    # Identity
    id = Column(String, primary_key=True, index=True)
    assessment_id = Column(
        String,
        ForeignKey("cra_assessments.id", ondelete="SET NULL"),
        nullable=True,
    )
    product_id = Column(String, nullable=True)

    # Classification (Art. 14(1) vs 14(4))
    incident_type = Column(String, nullable=False)
    # one of:
    #   "actively_exploited_vulnerability" (Art. 14(1))
    #   "severe_incident"                  (Art. 14(4))

    title = Column(String, nullable=False)
    severity = Column(String, nullable=True)  # critical/high/medium/low

    # Workflow
    status = Column(String, nullable=False, default="draft")
    # one of:
    #   "draft"
    #   "early_warning_submitted"
    #   "incident_report_submitted"
    #   "final_report_submitted"
    #   "closed"

    # ── Clock anchors ───────────────────────────────
    # When the manufacturer first became aware (Art. 14(1) — 24h clock starts).
    discovered_at = Column(DateTime(timezone=True), nullable=False)
    # When the corrective/mitigating measure becomes available (Art. 14(2)(c)
    # — 14d clock starts). Null until the fix lands.
    corrective_measure_available_at = Column(DateTime(timezone=True), nullable=True)

    # ── Submission timestamps (Art. 14(2)(a)/(b)/(c)) ───────────
    early_warning_submitted_at = Column(DateTime(timezone=True), nullable=True)
    incident_report_submitted_at = Column(DateTime(timezone=True), nullable=True)
    final_report_submitted_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # ── Art. 14(2)(a) — early warning content ────────────────
    actively_exploited = Column(Boolean, nullable=False, default=False)
    # JSON-encoded list of ISO-3166 alpha-2 codes of EU Member States where the
    # affected product has been made available, when known.
    member_states_affected = Column(Text, nullable=True)
    product_description = Column(Text, nullable=True)

    # ── Art. 14(2)(b) — incident-report addenda ──────────────
    vulnerability_nature = Column(Text, nullable=True)
    mitigations_taken = Column(Text, nullable=True)
    mitigations_recommended = Column(Text, nullable=True)

    # ── Art. 14(2)(c) — final report ──────────────────────────
    vulnerability_description = Column(Text, nullable=True)
    impact_description = Column(Text, nullable=True)
    malicious_actor_info = Column(Text, nullable=True)
    fixes_applied = Column(Text, nullable=True)

    # External identifiers
    cve_id = Column(String, nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    created_by = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    assessment = relationship("CraAssessment", backref="incidents")
