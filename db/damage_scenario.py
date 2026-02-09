"""
SQLAlchemy models for Damage Scenarios
"""
from sqlalchemy import Column, String, ForeignKey, Table, DateTime, Integer, Text, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime

from db.base import Base

# Association table for many-to-many relationship between components and damage scenarios
component_damage_scenario = Table(
    'component_damage_scenario',
    Base.metadata,
    Column('component_id', String, ForeignKey('components.component_id')),
    Column('scenario_id', String, ForeignKey('damage_scenarios.scenario_id')),
    UniqueConstraint('component_id', 'scenario_id', name='uq_component_damage_scenario')
)


class DamageScenario(Base):
    """SQLAlchemy model for damage scenarios"""
    __tablename__ = "damage_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Damage scenario properties
    damage_category = Column(String, nullable=False)  # Physical, Operational, Financial, Privacy, etc.
    impact_type = Column(String, nullable=False)  # Direct, Indirect, Cascading
    
    # Security properties affected (C-I-A)
    confidentiality_impact = Column(Boolean, default=False)
    integrity_impact = Column(Boolean, default=False)
    availability_impact = Column(Boolean, default=False)
    
    # Severity and impact details
    severity = Column(String, nullable=False)  # Low, Medium, High, Critical
    impact_details = Column(JSON, nullable=True)  # Detailed impact information
    
    # SFOP impact ratings
    safety_impact = Column(String, nullable=True)  # Low, Medium, High, Critical
    financial_impact = Column(String, nullable=True)  # Low, Medium, High, Critical
    operational_impact = Column(String, nullable=True)  # Low, Medium, High, Critical
    privacy_impact = Column(String, nullable=True)  # Low, Medium, High, Critical
    impact_rating_notes = Column(Text, nullable=True)  # Notes about impact ratings
    
    # Audit fields for regulatory compliance (UN R155 and ISO 21434)
    sfop_rating_auto_generated = Column(Boolean, default=True, nullable=False)  # Flag to indicate if ratings were auto-generated
    sfop_rating_last_edited_by = Column(String, nullable=True)  # Username who last modified the ratings
    sfop_rating_last_edited_at = Column(DateTime, nullable=True)  # When ratings were last modified
    sfop_rating_override_reason = Column(Text, nullable=True)  # Reason for overriding auto-ratings
    
    # Review status: draft (auto-generated) or accepted (reviewed by analyst)
    status = Column(String, default="accepted", nullable=False)
    
    # Versioning and audit
    version = Column(Integer, default=1)
    revision_notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)  # Soft delete flag
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Foreign keys
    scope_id = Column(String, ForeignKey("system_scopes.scope_id"), nullable=False)
    primary_component_id = Column(String, ForeignKey("components.component_id"), nullable=False)
    
    # Relationships
    scope = relationship("SystemScope", back_populates="damage_scenarios")
    primary_component = relationship("Component", foreign_keys=[primary_component_id])
    affected_components = relationship(
        "Component",
        secondary=component_damage_scenario,
        back_populates="damage_scenarios"
    )
