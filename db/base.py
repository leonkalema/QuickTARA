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
