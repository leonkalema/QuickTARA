"""
Simple Attack Path models for Risk Assessment
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class FeasibilityRating(BaseModel):
    """Feasibility rating for attack paths"""
    elapsed_time: int = Field(..., ge=0, le=19, description="Time required (0=≤1 day, 19=>6 months)")
    specialist_expertise: int = Field(..., ge=0, le=8, description="Expertise level (0=Layman, 8=Multiple Experts)")
    knowledge_of_target: int = Field(..., ge=0, le=11, description="Target knowledge (0=Public, 11=Strictly confidential)")
    window_of_opportunity: int = Field(..., ge=0, le=10, description="Opportunity window (0=Unlimited, 10=Difficult/none)")
    equipment: int = Field(..., ge=0, le=9, description="Equipment needed (0=Standard, 9=Multiple bespoke)")
    overall_rating: Optional[float] = Field(None, description="Calculated total score")

class AttackPathDB(Base):
    """Database model for attack paths"""
    __tablename__ = "attack_paths"
    
    attack_path_id = Column(String, primary_key=True, default=lambda: f"attack_path_{uuid.uuid4().hex[:8]}")
    threat_scenario_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    attack_steps = Column(Text, nullable=False)  # Multi-line text with steps
    
    # Feasibility rating fields
    elapsed_time = Column(Integer, nullable=False)
    specialist_expertise = Column(Integer, nullable=False)
    knowledge_of_target = Column(Integer, nullable=False)
    window_of_opportunity = Column(Integer, nullable=False)
    equipment = Column(Integer, nullable=False)
    overall_rating = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AttackPathBase(BaseModel):
    """Base model for attack paths"""
    threat_scenario_id: str = Field(..., description="ID of the associated threat scenario")
    name: str = Field(..., description="Name of the attack path")
    description: Optional[str] = Field(None, description="Description of the attack path")
    attack_steps: str = Field(..., description="Multi-line text with attack steps")
    feasibility_rating: FeasibilityRating = Field(..., description="Feasibility assessment")

class AttackPathCreate(AttackPathBase):
    """Create model for attack paths"""
    pass

class AttackPath(AttackPathBase):
    """Full attack path model with ID and timestamps"""
    attack_path_id: str = Field(..., description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True

class AttackPathResponse(BaseModel):
    """Response model for attack path lists"""
    attack_paths: List[AttackPath] = Field(..., description="List of attack paths")
    total: int = Field(..., description="Total number of attack paths")
