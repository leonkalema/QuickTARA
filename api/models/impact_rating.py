"""
Impact Rating models for FastAPI
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from api.models.damage_scenario import SeverityLevel, ImpactRatingLevel


class ImpactRatingExplanation(BaseModel):
    """Explanations for impact ratings"""
    safety_impact: str
    financial_impact: str
    operational_impact: str
    privacy_impact: str


class ImpactRatingUpdate(BaseModel):
    """Model for updating impact ratings"""
    safety_impact: Optional[ImpactRatingLevel] = None
    financial_impact: Optional[ImpactRatingLevel] = None
    operational_impact: Optional[ImpactRatingLevel] = None
    privacy_impact: Optional[ImpactRatingLevel] = None
    impact_rating_notes: Optional[str] = None
    sfop_rating_override_reason: Optional[str] = None  # Required when manually overriding auto-ratings


class ImpactRatingSuggestion(BaseModel):
    """Suggested impact ratings based on component and damage properties"""
    safety_impact: ImpactRatingLevel
    financial_impact: ImpactRatingLevel
    operational_impact: ImpactRatingLevel
    privacy_impact: ImpactRatingLevel
    explanations: ImpactRatingExplanation
