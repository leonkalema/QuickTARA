"""
Database model for threat scenarios
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class ThreatScenario(Base):
    """Threat scenario database model"""
    __tablename__ = "threat_scenarios"
    
    # Primary key and identifiers
    id = Column(Integer, primary_key=True, index=True)
    threat_scenario_id = Column(String(50), unique=True, index=True, nullable=False)
    damage_scenario_id = Column(String(50), index=True, nullable=False)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    attack_vector = Column(String(100), nullable=False)
    
    # Scope and versioning
    scope_id = Column(String(50), nullable=False, index=True)
    scope_version = Column(Integer, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    revision_notes = Column(Text, nullable=True)
    
    # Status and audit
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ThreatScenario(id='{self.threat_scenario_id}', name='{self.name}')>"
