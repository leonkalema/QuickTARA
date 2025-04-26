"""
SQLAlchemy models definitions
"""
from sqlalchemy import Column, String, Enum, ForeignKey, Table, DateTime, Integer, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON, ARRAY
from datetime import datetime

Base = declarative_base()

# Association tables for many-to-many relationships
component_connections = Table(
    'component_connections',
    Base.metadata,
    Column('component_id', String, ForeignKey('components.component_id'), primary_key=True),
    Column('connected_to_id', String, ForeignKey('components.component_id'), primary_key=True)
)


class Component(Base):
    """SQLAlchemy model for components"""
    __tablename__ = "components"
    
    component_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    safety_level = Column(String, nullable=False)
    interfaces = Column(JSON)
    access_points = Column(JSON)
    data_types = Column(JSON)
    location = Column(String, nullable=False)
    trust_zone = Column(String, nullable=False)
    
    # Relationships
    connected_to = relationship(
        "Component",
        secondary=component_connections,
        primaryjoin=component_id==component_connections.c.component_id,
        secondaryjoin=component_id==component_connections.c.connected_to_id,
        backref="connected_from"
    )
    
    # Analysis results relationship
    analyses = relationship("ComponentAnalysis", back_populates="component")
    
    # Scope relationship
    scope_id = Column(String, ForeignKey("system_scopes.scope_id"), nullable=True)
    scope = relationship("SystemScope", back_populates="components")


class Analysis(Base):
    """SQLAlchemy model for analysis results"""
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Summary metrics
    total_components = Column(Integer, default=0)
    total_threats = Column(Integer, default=0)
    critical_components = Column(Integer, default=0)
    high_risk_threats = Column(Integer, default=0)
    
    # Relationships
    component_analyses = relationship("ComponentAnalysis", back_populates="analysis")


class ComponentAnalysis(Base):
    """SQLAlchemy model for component-specific analysis results"""
    __tablename__ = "component_analyses"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), index=True)
    component_id = Column(String, ForeignKey("components.component_id"), index=True)
    
    # Analysis results (stored as JSON)
    threats = Column(JSON)
    stride_analysis = Column(JSON)
    compliance = Column(JSON)
    feasibility_assessments = Column(JSON)
    risk_acceptance = Column(JSON)
    attack_paths = Column(JSON)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="component_analyses")
    component = relationship("Component", back_populates="analyses")


class Report(Base):
    """SQLAlchemy model for reports"""
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), index=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    format = Column(String, nullable=False)  # Report format (txt, json, xlsx, pdf)
    report_type = Column(String, nullable=False)  # Report type (preliminary, final)
    status = Column(String, nullable=False)  # Report status (pending, generating, completed, failed)
    file_path = Column(String, nullable=True)  # Path to the generated file
    file_size = Column(Integer, nullable=True)  # Size of the generated file in bytes
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    
    # Configuration options (stored as JSON)
    configuration = Column(JSON)
    
    # Error information for failed reports (stored as JSON)
    error_info = Column(JSON, nullable=True)
    
    # Relationships
    analysis = relationship("Analysis", backref="reports")


class ReviewDecision(Base):
    """SQLAlchemy model for review decisions"""
    __tablename__ = "review_decisions"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), index=True)
    component_id = Column(String, ForeignKey("components.component_id"), index=True)
    threat_id = Column(String, nullable=False)  # Not a foreign key as threats are stored as JSON
    
    original_decision = Column(String, nullable=False)
    final_decision = Column(String, nullable=False)
    reviewer = Column(String, nullable=False)
    justification = Column(Text, nullable=False)
    additional_notes = Column(Text, nullable=True)
    review_date = Column(String, nullable=False)  # Format: YYYY-MM-DD
    evidence_references = Column(JSON, nullable=True)  # List of evidence references
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    status = Column(String, nullable=False)  # Review status (pending, in_progress, completed)
    
    # Relationships
    analysis = relationship("Analysis", backref="review_decisions")
    component = relationship("Component", backref="review_decisions")


class SystemScope(Base):
    """SQLAlchemy model for system scope definition"""
    __tablename__ = "system_scopes"
    
    id = Column(Integer, primary_key=True, index=True)
    scope_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    system_type = Column(String, nullable=False)  # subsystem, API, backend, etc.
    description = Column(Text, nullable=True)
    boundaries = Column(JSON, nullable=True)  # Using JSON for array storage as PostgreSQL ARRAY not supported in SQLite
    objectives = Column(JSON, nullable=True)  # Using JSON for array storage
    stakeholders = Column(JSON, nullable=True)  # Using JSON for array storage
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    components = relationship("Component", back_populates="scope")


class RiskFramework(Base):
    """SQLAlchemy model for risk calculation framework"""
    __tablename__ = "risk_frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String, nullable=False)
    impact_definitions = Column(JSON, nullable=False)  # Dict[str, List[ImpactDefinition]]
    likelihood_definitions = Column(JSON, nullable=False)  # List[LikelihoodDefinition]
    risk_matrix = Column(JSON, nullable=False)  # RiskMatrixDefinition
    risk_thresholds = Column(JSON, nullable=False)  # List[RiskThreshold]
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    # Future: Relate to analyses that use this framework


class Vulnerability(Base):
    """SQLAlchemy model for vulnerabilities"""
    __tablename__ = "vulnerabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String, nullable=False)  # Low, Medium, High, Critical
    cvss_score = Column(Float, nullable=True)
    cvss_vector = Column(String, nullable=True)
    affected_components = Column(JSON, nullable=True)  # Types of components this affects
    attack_vector = Column(String, nullable=True)  # Network, Adjacent, Local, Physical
    attack_complexity = Column(String, nullable=True)  # Low, High
    privileges_required = Column(String, nullable=True)  # None, Low, High
    user_interaction = Column(String, nullable=True)  # None, Required
    scope = Column(String, nullable=True)  # Unchanged, Changed
    confidentiality_impact = Column(String, nullable=True)  # None, Low, High
    integrity_impact = Column(String, nullable=True)  # None, Low, High
    availability_impact = Column(String, nullable=True)  # None, Low, High
    exploitability_score = Column(Float, nullable=True)
    impact_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    cwe_mappings = relationship("VulnerabilityCWEMapping", back_populates="vulnerability")
    cve_mappings = relationship("VulnerabilityCVEMapping", back_populates="vulnerability")
    mitigations = relationship("VulnerabilityMitigation", back_populates="vulnerability")
    assessments = relationship("VulnerabilityAssessment", back_populates="vulnerability")


class VulnerabilityCWEMapping(Base):
    """SQLAlchemy model for vulnerability-CWE mappings"""
    __tablename__ = "vulnerability_cwe_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(String, ForeignKey("vulnerabilities.vulnerability_id"), nullable=False)
    cwe_id = Column(String, nullable=False)
    cwe_name = Column(String, nullable=True)
    cwe_description = Column(Text, nullable=True)
    relationship_type = Column(String, nullable=True)  # Direct, Parent, Child, Related
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    vulnerability = relationship("Vulnerability", back_populates="cwe_mappings")


class VulnerabilityCVEMapping(Base):
    """SQLAlchemy model for vulnerability-CVE mappings"""
    __tablename__ = "vulnerability_cve_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    vulnerability_id = Column(String, ForeignKey("vulnerabilities.vulnerability_id"), nullable=False)
    cve_id = Column(String, nullable=False)
    cve_description = Column(Text, nullable=True)
    published_date = Column(DateTime, nullable=True)
    last_modified = Column(DateTime, nullable=True)
    cvss_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    vulnerability = relationship("Vulnerability", back_populates="cve_mappings")


class VulnerabilityAssessment(Base):
    """SQLAlchemy model for vulnerability assessments"""
    __tablename__ = "vulnerability_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String, unique=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    component_id = Column(String, ForeignKey("components.component_id"), nullable=False)
    vulnerability_id = Column(String, ForeignKey("vulnerabilities.vulnerability_id"), nullable=False)
    likelihood = Column(Integer, nullable=False)  # 1-5 scale
    impact = Column(JSON, nullable=True)  # Impact scores (financial, safety, privacy)
    risk_level = Column(String, nullable=False)  # Low, Medium, High, Critical
    mitigation_status = Column(String, nullable=True)  # Not Started, In Progress, Mitigated
    mitigation_notes = Column(Text, nullable=True)
    confidence_level = Column(Float, nullable=True)  # 0-1 confidence score
    detection_method = Column(String, nullable=True)  # Manual, Automated, Hybrid
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    analysis = relationship("Analysis", backref="vulnerability_assessments")
    component = relationship("Component", backref="vulnerability_assessments")
    vulnerability = relationship("Vulnerability", back_populates="assessments")


class VulnerabilityMitigation(Base):
    """SQLAlchemy model for vulnerability mitigations"""
    __tablename__ = "vulnerability_mitigations"
    
    id = Column(Integer, primary_key=True, index=True)
    mitigation_id = Column(String, unique=True, index=True)
    vulnerability_id = Column(String, ForeignKey("vulnerabilities.vulnerability_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    mitigation_type = Column(String, nullable=True)  # Preventive, Detective, Corrective
    effectiveness = Column(String, nullable=True)  # Low, Medium, High
    implementation_cost = Column(String, nullable=True)  # Low, Medium, High
    implementation_time = Column(String, nullable=True)  # Short, Medium, Long
    prerequisites = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    vulnerability = relationship("Vulnerability", back_populates="mitigations")



