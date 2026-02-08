"""
SQLAlchemy models for the threat catalog
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Table, JSON, Enum, Boolean
# Remove the declarative_base import as we're using Base from db.base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from db.base import Base

# Association tables for many-to-many relationships
# These association tables would be used for a more complex DB implementation
# For the simpler version, we'll store these as JSON arrays in the main table

# threat_component_types = Table(
#     'threat_component_types',
#     Base.metadata,
#     Column('threat_id', String, ForeignKey('threat_catalog.id'), primary_key=True),
#     Column('component_type', String, primary_key=True)
# )
#
# threat_trust_zones = Table(
#     'threat_trust_zones',
#     Base.metadata,
#     Column('threat_id', String, ForeignKey('threat_catalog.id'), primary_key=True),
#     Column('trust_zone', String, primary_key=True)
# )
#
# threat_attack_vectors = Table(
#     'threat_attack_vectors',
#     Base.metadata,
#     Column('threat_id', String, ForeignKey('threat_catalog.id'), primary_key=True),
#     Column('attack_vector', String, primary_key=True)
# )


class StrideCategoryEnum(str, enum.Enum):
    """STRIDE category enum for SQLAlchemy"""
    SPOOFING = "spoofing"
    TAMPERING = "tampering"
    REPUDIATION = "repudiation"
    INFO_DISCLOSURE = "info_disclosure"
    DENIAL_OF_SERVICE = "denial_of_service"
    ELEVATION = "elevation_of_privilege"


class ThreatCatalog(Base):
    """SQLAlchemy model for the threat catalog"""
    __tablename__ = "threat_catalog"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    stride_category = Column(String, nullable=False)  # Use string instead of Enum for simplicity
    applicable_component_types = Column(JSON, nullable=True)  # Store as JSON array
    applicable_trust_zones = Column(JSON, nullable=True)  # Store as JSON array
    attack_vectors = Column(JSON, nullable=True)  # Store as JSON array
    prerequisites = Column(JSON, nullable=True)
    typical_likelihood = Column(Integer, nullable=False)
    typical_severity = Column(Integer, nullable=False)
    mitigation_strategies = Column(JSON, nullable=True)
    cwe_ids = Column(JSON, nullable=True)
    capec_ids = Column(JSON, nullable=True)
    examples = Column(JSON, nullable=True)
    
    # MITRE ATT&CK provenance fields
    source = Column(String, nullable=False, default="custom")  # mitre_attack_ics | capec | custom
    source_version = Column(String, nullable=True)  # e.g. "15.1" for ATT&CK v15.1
    mitre_technique_id = Column(String, nullable=True, index=True)  # e.g. "T0800"
    mitre_tactic = Column(String, nullable=True)  # original ATT&CK tactic name
    automotive_relevance = Column(Integer, nullable=False, default=3)  # 1-5 relevance to automotive
    automotive_context = Column(String, nullable=True)  # automotive-specific description
    is_user_modified = Column(Boolean, nullable=False, default=False)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ThreatAnalysisResult(Base):
    """SQLAlchemy model for storing threat analysis results"""
    __tablename__ = "threat_analysis_results"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), index=True)
    component_id = Column(String, ForeignKey("components.component_id"), index=True)
    threat_id = Column(String, ForeignKey("threat_catalog.id"), index=True)
    match_confidence = Column(Integer, nullable=False)
    calculated_likelihood = Column(Integer, nullable=False)
    calculated_severity = Column(Integer, nullable=False)
    calculated_risk_score = Column(Integer, nullable=False)
    applicable_mitigations = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    analysis = relationship("Analysis", backref="threat_results")
    component = relationship("Component", backref="threat_results")
    threat = relationship("ThreatCatalog", backref="analysis_results")
