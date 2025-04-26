"""
Threat catalog models for the QuickTARA STRIDE analysis
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class StrideCategory(str, Enum):
    """STRIDE attack categories"""
    SPOOFING = "spoofing"
    TAMPERING = "tampering"
    REPUDIATION = "repudiation"
    INFO_DISCLOSURE = "info_disclosure"
    DENIAL_OF_SERVICE = "denial_of_service"
    ELEVATION = "elevation_of_privilege"


class ComponentType(str, Enum):
    """Component types that can be associated with threats"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    CONTROLLER = "controller"
    GATEWAY = "gateway"
    PROCESSING_UNIT = "processing_unit"
    STORAGE = "storage"
    COMMUNICATION = "communication"
    INTERFACE = "interface"
    HMI = "hmi"
    EXTERNAL_SERVICE = "external_service"
    OTHER = "other"


class TrustZone(str, Enum):
    """Trust zones that can be associated with threats"""
    SECURE = "secure"
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


class AttackVector(str, Enum):
    """Attack vectors for threats"""
    PHYSICAL = "physical"
    LOCAL_NETWORK = "local_network"
    ADJACENT_NETWORK = "adjacent_network"
    NETWORK = "network"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    CAN_BUS = "can_bus"
    USB = "usb"
    SUPPLY_CHAIN = "supply_chain"
    SOCIAL_ENGINEERING = "social_engineering"
    OTHER = "other"


class MitigationStrategy(BaseModel):
    """Mitigation strategy for a threat"""
    title: str = Field(..., description="Title of the mitigation strategy")
    description: str = Field(..., description="Description of the mitigation strategy")
    effectiveness: int = Field(..., ge=1, le=5, description="Effectiveness of the mitigation (1-5)")
    implementation_complexity: int = Field(..., ge=1, le=5, description="Implementation complexity (1-5)")
    references: List[str] = Field(default_factory=list, description="Reference links or documentation")


class ThreatCatalogItem(BaseModel):
    """A single threat in the threat catalog"""
    id: str = Field(..., description="Unique identifier for the threat")
    title: str = Field(..., description="Short title of the threat")
    description: str = Field(..., description="Detailed description of the threat")
    stride_category: StrideCategory = Field(..., description="STRIDE category of the threat")
    applicable_component_types: List[ComponentType] = Field(default_factory=list, description="Component types this threat applies to")
    applicable_trust_zones: List[TrustZone] = Field(default_factory=list, description="Trust zones this threat applies to")
    attack_vectors: List[AttackVector] = Field(default_factory=list, description="Possible attack vectors for this threat")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for this threat to be exploitable")
    typical_likelihood: int = Field(..., ge=1, le=5, description="Typical likelihood of occurrence (1-5)")
    typical_severity: int = Field(..., ge=1, le=5, description="Typical severity if exploited (1-5)")
    mitigation_strategies: List[MitigationStrategy] = Field(default_factory=list, description="Mitigation strategies for this threat")
    cwe_ids: List[str] = Field(default_factory=list, description="Related Common Weakness Enumeration IDs")
    capec_ids: List[str] = Field(default_factory=list, description="Related CAPEC IDs")
    examples: List[str] = Field(default_factory=list, description="Examples of this threat in real-world scenarios")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        orm_mode = True


class ThreatCatalogCreate(BaseModel):
    """Request model for creating a new threat catalog item"""
    title: str = Field(..., description="Short title of the threat")
    description: str = Field(..., description="Detailed description of the threat")
    stride_category: StrideCategory = Field(..., description="STRIDE category of the threat")
    applicable_component_types: List[ComponentType] = Field(default_factory=list, description="Component types this threat applies to")
    applicable_trust_zones: List[TrustZone] = Field(default_factory=list, description="Trust zones this threat applies to")
    attack_vectors: List[AttackVector] = Field(default_factory=list, description="Possible attack vectors for this threat")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for this threat to be exploitable")
    typical_likelihood: int = Field(..., ge=1, le=5, description="Typical likelihood of occurrence (1-5)")
    typical_severity: int = Field(..., ge=1, le=5, description="Typical severity if exploited (1-5)")
    mitigation_strategies: List[MitigationStrategy] = Field(default_factory=list, description="Mitigation strategies for this threat")
    cwe_ids: List[str] = Field(default_factory=list, description="Related Common Weakness Enumeration IDs")
    capec_ids: List[str] = Field(default_factory=list, description="Related CAPEC IDs")
    examples: List[str] = Field(default_factory=list, description="Examples of this threat in real-world scenarios")


class ThreatCatalogUpdate(BaseModel):
    """Request model for updating an existing threat catalog item"""
    title: Optional[str] = Field(None, description="Short title of the threat")
    description: Optional[str] = Field(None, description="Detailed description of the threat")
    stride_category: Optional[StrideCategory] = Field(None, description="STRIDE category of the threat")
    applicable_component_types: Optional[List[ComponentType]] = Field(None, description="Component types this threat applies to")
    applicable_trust_zones: Optional[List[TrustZone]] = Field(None, description="Trust zones this threat applies to")
    attack_vectors: Optional[List[AttackVector]] = Field(None, description="Possible attack vectors for this threat")
    prerequisites: Optional[List[str]] = Field(None, description="Prerequisites for this threat to be exploitable")
    typical_likelihood: Optional[int] = Field(None, ge=1, le=5, description="Typical likelihood of occurrence (1-5)")
    typical_severity: Optional[int] = Field(None, ge=1, le=5, description="Typical severity if exploited (1-5)")
    mitigation_strategies: Optional[List[MitigationStrategy]] = Field(None, description="Mitigation strategies for this threat")
    cwe_ids: Optional[List[str]] = Field(None, description="Related Common Weakness Enumeration IDs")
    capec_ids: Optional[List[str]] = Field(None, description="Related CAPEC IDs")
    examples: Optional[List[str]] = Field(None, description="Examples of this threat in real-world scenarios")


class ThreatMatchResult(BaseModel):
    """Result model for threat matching against a component"""
    threat_id: str = Field(..., description="ID of the matched threat")
    component_id: str = Field(..., description="ID of the component")
    title: str = Field(..., description="Title of the threat")
    stride_category: StrideCategory = Field(..., description="STRIDE category of the threat")
    match_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the match (0.0-1.0)")
    calculated_likelihood: int = Field(..., ge=1, le=5, description="Calculated likelihood for this component (1-5)")
    calculated_severity: int = Field(..., ge=1, le=5, description="Calculated severity for this component (1-5)")
    calculated_risk_score: int = Field(..., ge=1, le=25, description="Calculated risk score (likelihood * severity)")
    applicable_mitigation_strategies: List[MitigationStrategy] = Field(default_factory=list, description="Applicable mitigation strategies")
    notes: Optional[str] = Field(None, description="Additional notes about this match")


class ComponentThreatAnalysis(BaseModel):
    """Full threat analysis for a component"""
    component_id: str = Field(..., description="ID of the component")
    component_name: str = Field(..., description="Name of the component")
    component_type: str = Field(..., description="Type of the component")
    total_threats_identified: int = Field(..., description="Total number of threats identified")
    high_risk_threats: int = Field(..., description="Number of high-risk threats")
    medium_risk_threats: int = Field(..., description="Number of medium-risk threats")
    low_risk_threats: int = Field(..., description="Number of low-risk threats")
    threat_matches: List[ThreatMatchResult] = Field(default_factory=list, description="List of threat matches")
    stride_summary: Dict[str, int] = Field(default_factory=dict, description="Summary count of threats by STRIDE category")


class ThreatCatalogList(BaseModel):
    """List response model for threat catalog items"""
    catalog_items: List[ThreatCatalogItem] = Field(..., description="List of threat catalog items")
    total: int = Field(..., description="Total number of catalog items")


class ThreatAnalysisRequest(BaseModel):
    """Request model for performing a threat analysis"""
    component_ids: List[str] = Field(..., description="List of component IDs to analyze")
    custom_threats: Optional[List[ThreatCatalogItem]] = Field(None, description="Optional custom threats to include in the analysis")
    risk_framework_id: Optional[str] = Field(None, description="Risk framework ID to use for risk calculation")

    
class ThreatAnalysisResponse(BaseModel):
    """Response model for a threat analysis"""
    analysis_id: str = Field(..., description="ID of the created analysis")
    component_analyses: List[ComponentThreatAnalysis] = Field(..., description="Threat analyses for each component")
    total_components: int = Field(..., description="Total number of components analyzed")
    total_threats: int = Field(..., description="Total number of threats identified")
    high_risk_threats: int = Field(..., description="Total number of high-risk threats")
    stride_summary: Dict[str, int] = Field(default_factory=dict, description="Summary count of threats by STRIDE category")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the analysis")
