"""
SQLAlchemy models for Risk Treatment
"""
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Text, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from datetime import datetime

from db.base import Base


class RiskTreatment(Base):
    """SQLAlchemy model for risk treatments"""
    __tablename__ = "risk_treatments"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_treatment_id = Column(String, unique=True, index=True)
    
    # Links to related entities
    damage_scenario_id = Column(String, ForeignKey("damage_scenarios.scenario_id"), nullable=False)
    attack_path_id = Column(String, ForeignKey("attack_paths.attack_path_id"), nullable=False)
    scope_id = Column(String, ForeignKey("system_scopes.scope_id"), nullable=False)
    
    # Calculated risk data (stored when attack path is created)
    impact_level = Column(String, nullable=False)  # Negligible, Moderate, Major, Severe
    feasibility_level = Column(String, nullable=False)  # Very Low, Low, Medium, High, Very High
    risk_level = Column(String, nullable=False)  # Low, Medium, High, Critical
    feasibility_score = Column(Float, nullable=False)  # Attack path overall_rating
    
    # Treatment decision data
    suggested_treatment = Column(String, nullable=False)  # Auto-suggested: Avoiding, Reducing, Sharing, Retaining
    selected_treatment = Column(String, nullable=True)  # User-selected treatment
    treatment_goal = Column(Text, nullable=True)  # Security goal/claim text
    treatment_status = Column(String, default="draft")  # draft, approved, implemented
    
    # Approval workflow
    approved_by = Column(String, nullable=True)  # Username who approved
    approved_at = Column(DateTime, nullable=True)  # When approved
    approval_notes = Column(Text, nullable=True)  # Approval comments
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String, nullable=True)  # Username who created
    updated_by = Column(String, nullable=True)  # Username who last updated
    
    # Relationships
    damage_scenario = relationship("DamageScenario")
    scope = relationship("SystemScope")
