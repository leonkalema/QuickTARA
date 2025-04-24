"""
Analysis models for FastAPI
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class StrideCategory(str, Enum):
    """STRIDE attack categories"""
    SPOOFING = "spoofing"
    TAMPERING = "tampering"
    REPUDIATION = "repudiation"
    INFO_DISCLOSURE = "info_disclosure"
    DENIAL_OF_SERVICE = "denial_of_service"
    ELEVATION = "elevation_of_privilege"


class ImpactScore(BaseModel):
    """Impact scores for different categories"""
    financial: int = Field(1, ge=1, le=5, description="Financial impact (1-5)")
    safety: int = Field(1, ge=1, le=5, description="Safety impact (1-5)")
    privacy: int = Field(1, ge=1, le=5, description="Privacy impact (1-5)")


class RiskFactors(BaseModel):
    """Component risk factors"""
    exposure: float = Field(..., ge=0.0, le=1.0, description="Exposure risk factor")
    complexity: float = Field(..., ge=0.0, le=1.0, description="Complexity risk factor")
    attack_surface: float = Field(..., ge=0.0, le=1.0, description="Attack surface risk factor")


class Threat(BaseModel):
    """Threat model for a component"""
    name: str = Field(..., description="Threat name")
    description: str = Field(..., description="Threat description")
    likelihood: int = Field(..., ge=1, le=5, description="Likelihood (1-5)")
    impact: ImpactScore = Field(..., description="Impact scores")
    risk_factors: RiskFactors = Field(..., description="Risk factors")


class StrideRecommendation(BaseModel):
    """STRIDE analysis recommendation"""
    category: StrideCategory = Field(..., description="STRIDE category")
    risk_level: str = Field(..., description="Risk level (High/Medium/Low)")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")


class ComplianceRequirement(BaseModel):
    """Compliance mapping to standards"""
    standard: str = Field(..., description="Standard name (e.g., ISO 21434)")
    requirement: str = Field(..., description="Requirement identifier")
    description: str = Field(..., description="Requirement description")


class AttackerProfile(BaseModel):
    """Attacker profile assessment"""
    profile_type: str = Field(..., description="Attacker type (Hobbyist, Criminal, etc.)")
    relevance: int = Field(..., ge=1, le=5, description="Relevance score (1-5)")
    capabilities: List[str] = Field(default_factory=list, description="Key capabilities")


class AttackerFeasibility(BaseModel):
    """Attacker feasibility assessment"""
    feasibility_level: str = Field(..., description="Overall feasibility level")
    technical_capability: int = Field(..., ge=1, le=5, description="Technical capability required")
    knowledge_required: int = Field(..., ge=1, le=5, description="Knowledge required")
    resources_needed: int = Field(..., ge=1, le=5, description="Resources needed")
    time_required: int = Field(..., ge=1, le=5, description="Time required")
    overall_score: int = Field(..., ge=1, le=5, description="Overall feasibility score")
    enabling_factors: List[str] = Field(default_factory=list, description="Enabling factors")
    mitigating_factors: List[str] = Field(default_factory=list, description="Mitigating factors")
    attacker_profiles: List[AttackerProfile] = Field(default_factory=list, description="Relevant attacker profiles")


class RiskAcceptanceDecision(str, Enum):
    """Risk acceptance decisions"""
    ACCEPT = "Accept"
    ACCEPT_WITH_CONTROLS = "Accept with Controls"
    TRANSFER = "Transfer"
    AVOID = "Avoid"
    MITIGATE = "Mitigate"


class RiskSeverity(str, Enum):
    """Risk severity levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RiskAcceptance(BaseModel):
    """Risk acceptance assessment"""
    decision: RiskAcceptanceDecision = Field(..., description="Risk decision")
    risk_severity: RiskSeverity = Field(..., description="Risk severity")
    residual_risk: float = Field(..., ge=0.0, le=1.0, description="Residual risk percentage")
    justification: str = Field(..., description="Decision justification")
    conditions: List[str] = Field(default_factory=list, description="Acceptance conditions")
    approvers: List[str] = Field(default_factory=list, description="Required approvers")
    reassessment_period: int = Field(..., ge=0, description="Reassessment period in months")


class AttackPath(BaseModel):
    """Attack path between components"""
    path: List[str] = Field(..., description="Component IDs in the attack path")
    risk: Dict[str, int] = Field(..., description="Risk scores for the attack path")


class ComponentAnalysis(BaseModel):
    """Analysis results for a single component"""
    component_id: str = Field(..., description="Component ID")
    name: str = Field(..., description="Component name")
    type: str = Field(..., description="Component type")
    safety_level: str = Field(..., description="Safety level")
    threats: List[Threat] = Field(default_factory=list, description="Identified threats")
    stride_analysis: Dict[str, StrideRecommendation] = Field(default_factory=dict, description="STRIDE analysis")
    compliance: List[ComplianceRequirement] = Field(default_factory=list, description="Compliance requirements")
    feasibility_assessments: Dict[str, AttackerFeasibility] = Field(default_factory=dict, description="Attacker feasibility")
    risk_acceptance: Dict[str, RiskAcceptance] = Field(default_factory=dict, description="Risk acceptance decisions")
    attack_paths: List[AttackPath] = Field(default_factory=list, description="Attack paths")


class AnalysisCreate(BaseModel):
    """Request model for creating a new analysis"""
    component_ids: List[str] = Field(..., description="Component IDs to analyze")
    name: Optional[str] = Field(None, description="Analysis name")
    description: Optional[str] = Field(None, description="Analysis description")


class AnalysisSummary(BaseModel):
    """Summary of analysis results"""
    total_components: int = Field(..., description="Total components analyzed")
    total_threats: int = Field(..., description="Total threats identified")
    critical_components: int = Field(..., description="Number of critical components")
    high_risk_threats: int = Field(..., description="Number of high risk threats")


class Analysis(BaseModel):
    """Complete analysis model"""
    id: str = Field(..., description="Analysis ID")
    name: Optional[str] = Field(None, description="Analysis name")
    description: Optional[str] = Field(None, description="Analysis description")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    components: Dict[str, ComponentAnalysis] = Field(default_factory=dict, description="Component analysis results")
    summary: AnalysisSummary = Field(..., description="Analysis summary")
    
    class Config:
        orm_mode = True


class AnalysisList(BaseModel):
    """List of analyses with pagination"""
    analyses: List[Analysis] = Field(..., description="List of analyses")
    total: int = Field(..., description="Total number of analyses")
