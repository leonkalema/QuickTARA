"""
CRA (Cyber Resilience Act) Compliance Database Models

Tables:
  - cra_assessments: One per product, tracks classification and overall status
  - cra_requirement_statuses: 18 rows per assessment, one per CRA requirement
  - cra_compensating_controls: Legacy product compensating controls
"""
from sqlalchemy import (
    Column, String, ForeignKey, DateTime, Integer,
    Text, Boolean, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime
import enum

from db.product_asset_models import Base


class CraClassification(str, enum.Enum):
    """CRA product classification per Annex III"""
    DEFAULT = "default"
    CLASS_I = "class_i"
    CLASS_II = "class_ii"
    CRITICAL = "critical"


class CraProductType(str, enum.Enum):
    """Whether the product has existing TARA or is legacy"""
    CURRENT = "current"
    LEGACY_A = "legacy_a"
    LEGACY_B = "legacy_b"
    LEGACY_C = "legacy_c"


class CraAssessmentStatus(str, enum.Enum):
    """Assessment workflow status"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class CraRequirementStatus(str, enum.Enum):
    """Individual requirement compliance status"""
    NOT_STARTED = "not_started"
    PARTIAL = "partial"
    COMPLIANT = "compliant"
    NOT_APPLICABLE = "not_applicable"


class CompensatingControlStatus(str, enum.Enum):
    """Compensating control implementation status"""
    PLANNED = "planned"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"


class GapSeverity(str, enum.Enum):
    """Severity of gap for a CRA requirement"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CompliancePath(str, enum.Enum):
    """CRA compliance path per Art. 5(3)"""
    DIRECT_PATCH = "direct_patch"
    COMPENSATING_CONTROL = "compensating_control"
    HYBRID = "hybrid"


class CraAssessment(Base):
    """One CRA assessment per product"""
    __tablename__ = "cra_assessments"

    id = Column(String, primary_key=True, index=True)
    product_id = Column(
        String,
        ForeignKey("product_scopes.scope_id"),
        nullable=False,
        index=True,
        unique=True
    )
    classification = Column(String, nullable=True)
    classification_answers = Column(JSON, default=lambda: {})
    product_type = Column(String, default=CraProductType.CURRENT.value)
    compliance_path = Column(String, default=CompliancePath.DIRECT_PATCH.value)
    compliance_deadline = Column(String, nullable=True)
    assessment_date = Column(DateTime, default=datetime.now)
    assessor_id = Column(String, nullable=True)
    status = Column(
        String,
        default=CraAssessmentStatus.DRAFT.value,
        nullable=False
    )
    overall_compliance_pct = Column(Integer, default=0)
    support_period_end = Column(String, nullable=True)
    eoss_date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    automotive_exception = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    product = relationship("ProductScope", backref="cra_assessment")
    requirement_statuses = relationship(
        "CraRequirementStatusRecord",
        back_populates="assessment",
        cascade="all, delete-orphan"
    )
    compensating_controls = relationship(
        "CraCompensatingControl",
        back_populates="assessment",
        cascade="all, delete-orphan"
    )


class CraRequirementStatusRecord(Base):
    """Status of one CRA requirement within an assessment"""
    __tablename__ = "cra_requirement_statuses"

    id = Column(String, primary_key=True, index=True)
    assessment_id = Column(
        String,
        ForeignKey("cra_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    requirement_id = Column(String, nullable=False)
    status = Column(
        String,
        default=CraRequirementStatus.NOT_STARTED.value,
        nullable=False
    )
    auto_mapped = Column(Boolean, default=False)
    mapped_artifact_type = Column(String, nullable=True)
    mapped_artifact_count = Column(Integer, default=0)
    owner = Column(String, nullable=True)
    target_date = Column(String, nullable=True)
    evidence_notes = Column(Text, nullable=True)
    evidence_links = Column(JSON, default=lambda: [])
    gap_description = Column(Text, nullable=True)
    remediation_plan = Column(Text, nullable=True)
    gap_severity = Column(String, default=GapSeverity.NONE.value)
    residual_risk_level = Column(String, default=GapSeverity.NONE.value)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    assessment = relationship(
        "CraAssessment", back_populates="requirement_statuses"
    )


class CraCompensatingControl(Base):
    """Compensating controls for legacy products (Art. 5(3))"""
    __tablename__ = "cra_compensating_controls"

    id = Column(String, primary_key=True, index=True)
    assessment_id = Column(
        String,
        ForeignKey("cra_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    control_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    implementation_status = Column(
        String,
        default=CompensatingControlStatus.PLANNED.value,
        nullable=False
    )
    supplier_actions = Column(Text, nullable=True)
    oem_actions = Column(Text, nullable=True)
    residual_risk = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    # Relationships
    assessment = relationship(
        "CraAssessment", back_populates="compensating_controls"
    )
    mitigated_requirements = relationship(
        "CraControlRequirementLink",
        back_populates="control",
        cascade="all, delete-orphan"
    )


class CraInventoryItem(Base):
    """Inventory item for CRA assessment - tracks SKUs and field population"""
    __tablename__ = "cra_inventory_items"

    id = Column(String, primary_key=True, index=True)
    assessment_id = Column(
        String,
        ForeignKey("cra_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sku = Column(String, nullable=False)
    firmware_version = Column(String, nullable=True)
    units_in_stock = Column(Integer, default=0)
    units_in_field = Column(Integer, default=0)
    oem_customer = Column(String, nullable=True)
    target_market = Column(String, default="eu")  # eu, non_eu, global
    last_production_date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    assessment = relationship("CraAssessment", backref="inventory_items")


class CraControlRequirementLink(Base):
    """Junction table linking compensating controls to requirements they mitigate"""
    __tablename__ = "cra_control_requirement_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    control_id = Column(
        String,
        ForeignKey("cra_compensating_controls.id", ondelete="CASCADE"),
        nullable=False
    )
    requirement_status_id = Column(
        String,
        ForeignKey("cra_requirement_statuses.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    control = relationship(
        "CraCompensatingControl", back_populates="mitigated_requirements"
    )
    requirement_status = relationship("CraRequirementStatusRecord")
