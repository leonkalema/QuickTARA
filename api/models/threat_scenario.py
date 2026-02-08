"""
Threat Scenario models for the QuickTARA TARA workflow
Links damage scenarios to specific threat instances
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ImpactRatingLevel(str, Enum):
    """Impact rating levels"""
    NEGLIGIBLE = "negligible"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"


class ImpactRating(BaseModel):
    """Impact rating for different categories"""
    safety: ImpactRatingLevel = Field(..., description="Safety impact level")
    financial: ImpactRatingLevel = Field(..., description="Financial impact level")
    operational: ImpactRatingLevel = Field(..., description="Operational impact level")
    privacy: ImpactRatingLevel = Field(..., description="Privacy impact level")


class ThreatScenarioBase(BaseModel):
    """Base threat scenario model"""
    threat_scenario_id: str = Field(..., description="Unique threat scenario ID (e.g., TS-001)")
    damage_scenario_id: Optional[str] = Field(None, description="Associated damage scenario ID (deprecated - use damage_scenario_ids)")
    name: str = Field(..., description="Threat scenario name")
    description: str = Field(..., description="How an attacker could cause the damage")
    attack_vector: str = Field(..., description="Attack vector used")
    scope_id: str = Field(..., description="Product scope ID")
    scope_version: int = Field(..., description="Product scope version")


class ThreatScenarioCreate(ThreatScenarioBase):
    """Create threat scenario request"""
    threat_scenario_id: Optional[str] = Field(None, description="Will be auto-generated if not provided")
    damage_scenario_ids: Optional[List[str]] = Field(None, description="List of associated damage scenario IDs")


class ThreatScenarioUpdate(BaseModel):
    """Update threat scenario request"""
    name: Optional[str] = Field(None, description="Threat scenario name")
    description: Optional[str] = Field(None, description="How an attacker could cause the damage")
    attack_vector: Optional[str] = Field(None, description="Attack vector used")


class ThreatScenario(ThreatScenarioBase):
    """Full threat scenario model with timestamps"""
    version: int = Field(..., description="Version number")
    revision_notes: Optional[str] = Field(None, description="Notes about this revision")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    status: str = Field(default="accepted", description="Review status: draft or accepted")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ThreatScenarioList(BaseModel):
    """List of threat scenarios"""
    threat_scenarios: List[ThreatScenario]
    total: int
