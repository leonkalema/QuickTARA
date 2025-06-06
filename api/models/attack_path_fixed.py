"""
Attack Path Analysis models for FastAPI
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AttackPathType(str, Enum):
    """Types of attack paths"""
    DIRECT = "Direct"             # Direct path from entry point to target
    MULTI_STEP = "Multi-Step"     # Multi-step attack requiring multiple components
    LATERAL = "Lateral"           # Lateral movement across trust boundaries
    PRIVILEGE_ESCALATION = "Privilege Escalation"  # Path that increases privileges


class AttackStepType(str, Enum):
    """Types of attack steps"""
    INITIAL_ACCESS = "Initial Access"
    EXECUTION = "Execution"
    PERSISTENCE = "Persistence"
    PRIVILEGE_ESCALATION = "Privilege Escalation"
    DEFENSE_EVASION = "Defense Evasion"
    CREDENTIAL_ACCESS = "Credential Access"
    DISCOVERY = "Discovery"
    LATERAL_MOVEMENT = "Lateral Movement"
    COLLECTION = "Collection"
    EXFILTRATION = "Exfiltration"
    COMMAND_AND_CONTROL = "Command and Control"
    IMPACT = "Impact"


class AttackComplexity(str, Enum):
    """Attack complexity levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class StepBase(BaseModel):
    """Base model for attack steps"""
    component_id: str = Field(..., description="The component ID for this step")
    step_type: AttackStepType = Field(..., description="The type of attack step")
    description: str = Field(..., description="Description of the attack step")
    prerequisites: Optional[List[str]] = Field(default_factory=list, description="Prerequisites for this step")
    vulnerability_ids: Optional[List[str]] = Field(default_factory=list, description="Associated vulnerabilities")
    threat_ids: Optional[List[str]] = Field(default_factory=list, description="Associated threats")
    order: int = Field(..., description="The order of this step in the path")


class StepCreate(StepBase):
    """Create model for attack steps"""
    pass


class Step(StepBase):
    """Model for attack steps with ID and timestamps"""
    step_id: str = Field(..., description="Unique identifier for the step")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class PathBase(BaseModel):
    """Base model for attack paths"""
    name: str = Field(..., description="Name of the attack path")
    description: str = Field(..., description="Description of the attack path")
    path_type: AttackPathType = Field(..., description="Type of attack path")
    complexity: AttackComplexity = Field(..., description="Complexity of the attack path")
    entry_point_id: str = Field(..., description="Component ID of the entry point")
    target_id: str = Field(..., description="Component ID of the target")
    success_likelihood: float = Field(..., ge=0.0, le=1.0, description="Likelihood of successful exploitation")
    impact: Dict[str, int] = Field(..., description="Impact ratings (e.g., confidentiality, integrity, availability)")
    risk_score: float = Field(..., ge=0.0, le=10.0, description="Overall risk score")


class PathCreate(PathBase):
    """Create model for attack paths"""
    steps: List[StepCreate] = Field(..., description="Steps in the attack path")
    analysis_id: str = Field(..., description="ID of the analysis this path belongs to")
    scope_id: Optional[str] = Field(None, description="ID of the scope this analysis was performed in")


class Path(PathBase):
    """Model for attack paths with ID and timestamps"""
    path_id: str = Field(..., description="Unique identifier for the path")
    analysis_id: str = Field(..., description="ID of the analysis this path belongs to")
    scope_id: Optional[str] = Field(None, description="ID of the scope this analysis was performed in")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    steps: List[Step] = Field(default_factory=list, description="Steps in the attack path")
    
    class Config:
        from_attributes = True


class ChainBase(BaseModel):
    """Base model for attack chains"""
    name: str = Field(..., description="Name of the attack chain")
    description: str = Field(..., description="Description of the attack chain")
    # Changed from List[str] to str for each individual entry point
    entry_point_id: str = Field(..., description="Component ID of the primary entry point")
    final_target_id: str = Field(..., description="Component ID of the final target")
    attack_goal: str = Field(..., description="The goal of the attack")
    total_steps: int = Field(..., description="Total number of steps in the chain")
    complexity: AttackComplexity = Field(..., description="Complexity of the attack chain")
    success_likelihood: float = Field(..., ge=0.0, le=1.0, description="Likelihood of successful exploitation")
    impact: Dict[str, int] = Field(..., description="Impact ratings (e.g., confidentiality, integrity, availability)")
    risk_score: float = Field(..., ge=0.0, le=10.0, description="Overall risk score")


class ChainCreate(ChainBase):
    """Create model for attack chains"""
    path_ids: List[str] = Field(..., description="IDs of attack paths in this chain")
    analysis_id: str = Field(..., description="ID of the analysis this chain belongs to")
    scope_id: Optional[str] = Field(None, description="ID of the scope this analysis was performed in")


class Chain(ChainBase):
    """Model for attack chains with ID and timestamps"""
    chain_id: str = Field(..., description="Unique identifier for the chain")
    analysis_id: str = Field(..., description="ID of the analysis this chain belongs to")
    scope_id: Optional[str] = Field(None, description="ID of the scope this analysis was performed in")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    paths: List[Path] = Field(default_factory=list, description="Paths in the attack chain")
    
    class Config:
        from_attributes = True


class AttackPathRequest(BaseModel):
    """Request model for generating attack paths"""
    component_ids: List[str] = Field(..., description="IDs of components to analyze")
    analysis_id: Optional[str] = Field(None, description="Optional existing analysis ID")
    scope_id: Optional[str] = Field(None, description="Optional scope ID")
    entry_point_ids: Optional[List[str]] = Field(None, description="Optional specific entry points")
    target_ids: Optional[List[str]] = Field(None, description="Optional specific targets")
    include_chains: bool = Field(True, description="Whether to generate attack chains")
    max_depth: Optional[int] = Field(5, description="Maximum path depth to consider")


class AttackPathList(BaseModel):
    """List of attack paths"""
    paths: List[Path] = Field(..., description="List of attack paths")
    total: int = Field(..., description="Total number of paths")


class AttackChainList(BaseModel):
    """List of attack chains"""
    chains: List[Chain] = Field(..., description="List of attack chains")
    total: int = Field(..., description="Total number of chains")


class AttackPathAnalysisResult(BaseModel):
    """Result of an attack path analysis"""
    analysis_id: str = Field(..., description="ID of the analysis")
    component_count: int = Field(..., description="Number of components analyzed")
    entry_points: List[Dict[str, Any]] = Field(..., description="Entry points identified")
    critical_targets: List[Dict[str, Any]] = Field(..., description="Critical targets identified")
    total_paths: int = Field(..., description="Total number of attack paths identified")
    high_risk_paths: int = Field(..., description="Number of high-risk paths")
    total_chains: int = Field(..., description="Total number of attack chains identified")
    high_risk_chains: int = Field(..., description="Number of high-risk chains")
    created_at: datetime = Field(..., description="Analysis timestamp")
    scope_id: Optional[str] = Field(None, description="ID of the scope")
