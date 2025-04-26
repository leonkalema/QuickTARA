"""
Risk Calculation Framework models for FastAPI
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ImpactCategory(str, Enum):
    """Impact categories for risk assessment"""
    SAFETY = "safety"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    PRIVACY = "privacy"
    REPUTATION = "reputation"
    COMPLIANCE = "compliance"


class SeverityLevel(str, Enum):
    """Severity levels for impact categories"""
    NEGLIGIBLE = "negligible"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"


class LikelihoodLevel(str, Enum):
    """Likelihood levels for risk assessment"""
    RARE = "rare"
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    ALMOST_CERTAIN = "almost_certain"


class RiskLevel(str, Enum):
    """Risk levels derived from risk matrix"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImpactDefinition(BaseModel):
    """Definition of impact for a specific category"""
    category: ImpactCategory = Field(..., description="Impact category")
    level: SeverityLevel = Field(..., description="Severity level")
    description: str = Field(..., description="Description of this impact level")
    numerical_value: int = Field(..., ge=1, le=5, description="Numerical value (1-5)")
    examples: List[str] = Field(default_factory=list, description="Examples of this impact level")


class LikelihoodDefinition(BaseModel):
    """Definition of likelihood level"""
    level: LikelihoodLevel = Field(..., description="Likelihood level")
    description: str = Field(..., description="Description of this likelihood level")
    numerical_value: int = Field(..., ge=1, le=5, description="Numerical value (1-5)")
    probability_range: Optional[Dict[str, float]] = Field(None, description="Probability range (min/max)")
    examples: List[str] = Field(default_factory=list, description="Examples of this likelihood level")


class RiskThreshold(BaseModel):
    """Risk acceptance threshold"""
    level: RiskLevel = Field(..., description="Risk level")
    description: str = Field(..., description="Description of this threshold")
    requires_approval: bool = Field(default=False, description="Whether this risk level requires approval")
    approvers: List[str] = Field(default_factory=list, description="Required approvers for this risk level")
    max_acceptable_score: int = Field(..., ge=1, le=25, description="Maximum acceptable risk score")


class RiskMatrixCell(BaseModel):
    """Single cell in the risk matrix"""
    impact: int = Field(..., ge=1, le=5, description="Impact value")
    likelihood: int = Field(..., ge=1, le=5, description="Likelihood value")
    risk_level: RiskLevel = Field(..., description="Resulting risk level")
    numerical_score: int = Field(..., ge=1, le=25, description="Numerical risk score")


class RiskMatrixDefinition(BaseModel):
    """Definition of the risk matrix"""
    matrix: List[RiskMatrixCell] = Field(..., description="Risk matrix cells")
    description: str = Field(..., description="Description of risk matrix")


class RiskFrameworkConfiguration(BaseModel):
    """Complete risk framework configuration"""
    framework_id: str = Field(..., description="Unique identifier for this framework")
    name: str = Field(..., description="Framework name")
    description: Optional[str] = Field(None, description="Framework description")
    version: str = Field(..., description="Framework version")
    impact_definitions: Dict[str, List[ImpactDefinition]] = Field(
        ..., description="Impact definitions by category"
    )
    likelihood_definitions: List[LikelihoodDefinition] = Field(
        ..., description="Likelihood definitions"
    )
    risk_matrix: RiskMatrixDefinition = Field(..., description="Risk matrix definition")
    risk_thresholds: List[RiskThreshold] = Field(..., description="Risk thresholds")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(default=True, description="Whether this framework is active")

    class Config:
        orm_mode = True


class RiskFrameworkCreate(BaseModel):
    """Request model for creating a new risk framework"""
    name: str = Field(..., description="Framework name")
    description: Optional[str] = Field(None, description="Framework description")
    version: str = Field(..., description="Framework version")
    impact_definitions: Dict[str, List[ImpactDefinition]] = Field(
        ..., description="Impact definitions by category"
    )
    likelihood_definitions: List[LikelihoodDefinition] = Field(
        ..., description="Likelihood definitions"
    )
    risk_matrix: RiskMatrixDefinition = Field(..., description="Risk matrix definition")
    risk_thresholds: List[RiskThreshold] = Field(..., description="Risk thresholds")


class RiskFrameworkUpdate(BaseModel):
    """Request model for updating an existing risk framework"""
    name: Optional[str] = Field(None, description="Framework name")
    description: Optional[str] = Field(None, description="Framework description")
    version: Optional[str] = Field(None, description="Framework version")
    impact_definitions: Optional[Dict[str, List[ImpactDefinition]]] = Field(
        None, description="Impact definitions by category"
    )
    likelihood_definitions: Optional[List[LikelihoodDefinition]] = Field(
        None, description="Likelihood definitions"
    )
    risk_matrix: Optional[RiskMatrixDefinition] = Field(None, description="Risk matrix definition")
    risk_thresholds: Optional[List[RiskThreshold]] = Field(None, description="Risk thresholds")
    is_active: Optional[bool] = Field(None, description="Whether this framework is active")


class RiskFrameworkList(BaseModel):
    """List of risk frameworks"""
    frameworks: List[RiskFrameworkConfiguration] = Field(..., description="List of risk frameworks")
    total: int = Field(..., description="Total number of risk frameworks")
