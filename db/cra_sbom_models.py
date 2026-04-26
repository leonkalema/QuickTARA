"""CRA-10 — SBOM persistence models.

CRA Art. 13(6) / Annex I, Part II §1: manufacturers must identify and
document components in the product, including by drawing up an SBOM in
a commonly used and machine-readable format.

Tables:
  - cra_sboms              : one row per uploaded SBOM document
  - cra_sbom_components    : flattened component entries from each SBOM

A `CraAssessment` may have multiple SBOMs over time (one per release).
The most-recent SBOM is the source of evidence for CRA-10 auto-mapping.
"""
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from db.product_asset_models import Base


class CraSbom(Base):
    """One uploaded SBOM document attached to a CRA assessment."""

    __tablename__ = "cra_sboms"

    id = Column(String, primary_key=True, index=True)
    assessment_id = Column(
        String,
        ForeignKey("cra_assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sbom_format = Column(String, nullable=False)  # "cyclonedx" | "spdx"
    spec_version = Column(String, nullable=False)
    serial_number = Column(String, nullable=True)
    document_name = Column(String, nullable=True)
    primary_component_name = Column(String, nullable=True)
    primary_component_version = Column(String, nullable=True)
    component_count = Column(Integer, nullable=False, default=0)
    raw_size_bytes = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    uploaded_by = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    assessment = relationship("CraAssessment", backref="sboms")
    components = relationship(
        "CraSbomComponent",
        back_populates="sbom",
        cascade="all, delete-orphan",
    )


class CraSbomComponent(Base):
    """One component entry parsed from an SBOM document."""

    __tablename__ = "cra_sbom_components"
    __table_args__ = (
        Index("ix_cra_sbom_components_purl", "purl"),
        Index("ix_cra_sbom_components_name_version", "name", "version"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    sbom_id = Column(
        String,
        ForeignKey("cra_sboms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    bom_ref = Column(String, nullable=False)
    name = Column(String, nullable=False)
    version = Column(String, nullable=True)
    component_type = Column(String, nullable=True)
    purl = Column(String, nullable=True)
    cpe = Column(String, nullable=True)
    supplier = Column(String, nullable=True)
    licenses = Column(Text, nullable=True)  # comma-separated SPDX IDs
    hashes = Column(Text, nullable=True)    # "alg=value;alg=value"

    sbom = relationship("CraSbom", back_populates="components")
