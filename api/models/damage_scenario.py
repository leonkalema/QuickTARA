"""
Damage Scenario models for FastAPI
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, field_validator, model_validator
from datetime import datetime


class DamageCategory(str, Enum):
    """Damage categories for damage scenarios"""
    PHYSICAL = "Physical"
    OPERATIONAL = "Operational"
    FINANCIAL = "Financial"
    PRIVACY = "Privacy"
    SAFETY = "Safety"
    ENVIRONMENTAL = "Environmental"
    REPUTATIONAL = "Reputational"
    LEGAL = "Legal"
    OTHER = "Other"


class ImpactType(str, Enum):
    """Impact types for damage scenarios"""
    DIRECT = "Direct"
    INDIRECT = "Indirect"
    CASCADING = "Cascading"


class SeverityLevel(str, Enum):
    """Severity levels for damage scenarios"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ImpactRatingLevel(str, Enum):
    """Impact rating levels"""
    NEGLIGIBLE = "negligible"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"


class ImpactRating(BaseModel):
    """Impact rating for different categories"""
    safety: ImpactRatingLevel = Field(default=ImpactRatingLevel.NEGLIGIBLE, description="Safety impact level")
    financial: ImpactRatingLevel = Field(default=ImpactRatingLevel.NEGLIGIBLE, description="Financial impact level")
    operational: ImpactRatingLevel = Field(default=ImpactRatingLevel.NEGLIGIBLE, description="Operational impact level")
    privacy: ImpactRatingLevel = Field(default=ImpactRatingLevel.NEGLIGIBLE, description="Privacy impact level")


class DamageScenarioBase(BaseModel):
    """Base Damage Scenario attributes"""
    damage_scenario_id: Optional[str] = Field(None, description="Unique damage scenario ID (e.g., DS-001)")
    name: str = Field(..., description="Scenario name")
    description: Optional[str] = Field(None, description="Detailed description of the damage scenario")
    damage_category: DamageCategory = Field(..., description="Category of damage")
    impact_type: ImpactType = Field(..., description="Type of impact")
    
    # Security properties affected
    confidentiality_impact: bool = Field(
        default=False, 
        description="Whether confidentiality is affected"
    )
    integrity_impact: bool = Field(
        default=False, 
        description="Whether integrity is affected"
    )
    availability_impact: bool = Field(
        default=False, 
        description="Whether availability is affected"
    )
    
    # Severity and impact details
    severity: SeverityLevel = Field(..., description="Severity level of the damage")
    impact_details: Optional[dict] = Field(
        default=None, 
        description="Detailed impact information"
    )
    
    # Impact ratings (Safety, Financial, Operational, Privacy)
    impact_rating: Optional[ImpactRating] = Field(None, description="Impact ratings for different categories")
    impact_rating_notes: Optional[str] = Field(None, description="Notes about impact ratings")
    
    # Audit fields for regulatory compliance
    sfop_rating_auto_generated: bool = Field(default=True, description="Whether ratings were auto-generated")
    sfop_rating_last_edited_by: Optional[str] = Field(None, description="Username who last modified the ratings")
    sfop_rating_last_edited_at: Optional[datetime] = Field(None, description="When ratings were last modified")
    sfop_rating_override_reason: Optional[str] = Field(None, description="Reason for overriding auto-ratings")
    
    # Related components
    scope_id: str = Field(..., description="Associated system scope ID")
    primary_component_id: Optional[str] = Field(None, description="Primary affected component ID")
    affected_component_ids: List[str] = Field(
        default_factory=list, 
        description="IDs of all affected components"
    )
    
    @model_validator(mode='after')
    def validate_cia_impacts(self):
        """Validate that at least one CIA property is impacted"""
        if not any([self.confidentiality_impact, self.integrity_impact, self.availability_impact]):
            raise ValueError("At least one security property (CIA) must be impacted")
        
        return self
    
    @field_validator('affected_component_ids')
    def validate_affected_components(cls, v, info):
        """Validate that primary component is included in affected components"""
        # Get the primary_component_id from the validation context
        primary_id = info.data.get('primary_component_id')
        if primary_id and primary_id not in v:
            v.append(primary_id)
        return v


class DamageScenarioCreate(DamageScenarioBase):
    """Used for creating a new damage scenario"""
    scenario_id: Optional[str] = Field(None, description="Optional unique scenario identifier")
    version: int = Field(default=1, description="Version number")
    revision_notes: Optional[str] = Field(None, description="Notes about this revision")


class DamageScenarioUpdate(BaseModel):
    """Used for updating an existing damage scenario"""
    name: Optional[str] = None
    description: Optional[str] = None
    damage_category: Optional[DamageCategory] = None
    impact_type: Optional[ImpactType] = None
    confidentiality_impact: Optional[bool] = None
    integrity_impact: Optional[bool] = None
    availability_impact: Optional[bool] = None
    severity: Optional[SeverityLevel] = None
    impact_details: Optional[Dict[str, Any]] = None
    scope_id: Optional[str] = None
    primary_component_id: Optional[str] = None
    affected_component_ids: Optional[List[str]] = None
    version: Optional[int] = None
    revision_notes: Optional[str] = None
    
    # SFOP impact ratings
    safety_impact: Optional[SeverityLevel] = None
    financial_impact: Optional[SeverityLevel] = None
    operational_impact: Optional[SeverityLevel] = None
    privacy_impact: Optional[SeverityLevel] = None
    impact_rating_notes: Optional[str] = None
    
    # Audit fields for regulatory compliance
    sfop_rating_auto_generated: Optional[bool] = None
    sfop_rating_last_edited_by: Optional[str] = None
    sfop_rating_last_edited_at: Optional[datetime] = None
    sfop_rating_override_reason: Optional[str] = None  # Required when manually overriding auto-ratings
    
    @model_validator(mode='after')
    def validate_cia_impacts(self):
        """Validate that CIA impacts are consistent if all are provided"""
        # Only validate if all three are being updated
        if all(x is not None for x in [self.confidentiality_impact, self.integrity_impact, self.availability_impact]):
            if not any([self.confidentiality_impact, self.integrity_impact, self.availability_impact]):
                raise ValueError("At least one security property (CIA) must be impacted")
        
        return self


class DamageScenario(DamageScenarioBase):
    """Full damage scenario model with ID and timestamps"""
    scenario_id: str = Field(..., description="Unique scenario identifier")
    version: int = Field(..., description="Version number")
    revision_notes: Optional[str] = Field(None, description="Notes about this revision")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    status: str = Field(default="accepted", description="Review status: draft or accepted")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DamageScenarioList(BaseModel):
    """List of damage scenarios"""
    scenarios: List[DamageScenario]
    total: int


class PropagationRule(BaseModel):
    """Rule for impact propagation"""
    source_type: str = Field(..., description="Source component type")
    target_type: str = Field(..., description="Target component type")
    confidentiality_propagation: bool = Field(default=False)
    integrity_propagation: bool = Field(default=False)
    availability_propagation: bool = Field(default=False)
    propagation_likelihood: float = Field(..., description="Likelihood of propagation (0-1)")


class PropagationSuggestion(BaseModel):
    """Suggestion for impact propagation"""
    source_component_id: str
    target_component_id: str
    confidentiality_impact: bool = False
    integrity_impact: bool = False
    availability_impact: bool = False
    damage_category: DamageCategory
    impact_type: ImpactType
    severity: SeverityLevel
    confidence: float = Field(..., description="Confidence score (0-1)")
    path: List[str] = Field(default_factory=list, description="Propagation path component IDs")


class PropagationSuggestionResponse(BaseModel):
    """Response containing propagation suggestions"""
    suggestions: List[PropagationSuggestion]
    total: int
