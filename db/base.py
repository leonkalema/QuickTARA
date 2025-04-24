"""
SQLAlchemy models definitions
"""
from sqlalchemy import Column, String, Enum, ForeignKey, Table, DateTime, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
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
