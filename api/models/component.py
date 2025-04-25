"""
Component models for FastAPI
"""
from enum import Enum
from typing import List, Optional, Set
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """Component asset types"""
    ECU = "ECU"
    SENSOR = "Sensor"
    GATEWAY = "Gateway"
    ACTUATOR = "Actuator"
    NETWORK = "Network"


class SafetyLevel(str, Enum):
    """Component safety levels (ASIL)"""
    QM = "QM"
    ASIL_A = "ASIL A"
    ASIL_B = "ASIL B"
    ASIL_C = "ASIL C"
    ASIL_D = "ASIL D"


class TrustZone(str, Enum):
    """Component trust zones"""
    CRITICAL = "Critical"
    BOUNDARY = "Boundary"
    STANDARD = "Standard"
    UNTRUSTED = "Untrusted"


class ComponentBase(BaseModel):
    """Base Component attributes"""
    name: str = Field(..., description="Component name")
    type: AssetType = Field(..., description="Component type")
    safety_level: SafetyLevel = Field(..., description="Component safety level (ASIL)")
    interfaces: List[str] = Field(default_factory=list, description="Communication interfaces")
    access_points: List[str] = Field(default_factory=list, description="Physical access points")
    data_types: List[str] = Field(default_factory=list, description="Types of data handled")
    location: str = Field(..., description="Physical location (Internal/External)")
    trust_zone: TrustZone = Field(..., description="Security trust zone")
    connected_to: List[str] = Field(default_factory=list, description="Connected component IDs")
    scope_id: Optional[str] = Field(None, description="Associated system scope ID")


class ComponentCreate(ComponentBase):
    """Used for creating a new component"""
    component_id: str = Field(..., description="Unique component identifier")
    # scope_id is inherited from ComponentBase


class ComponentUpdate(ComponentBase):
    """Used for updating an existing component"""
    name: Optional[str] = None
    type: Optional[AssetType] = None
    safety_level: Optional[SafetyLevel] = None
    interfaces: Optional[List[str]] = None
    access_points: Optional[List[str]] = None
    data_types: Optional[List[str]] = None
    location: Optional[str] = None
    trust_zone: Optional[TrustZone] = None
    connected_to: Optional[List[str]] = None
    scope_id: Optional[str] = None


class Component(ComponentBase):
    """Full component model with ID"""
    component_id: str = Field(..., description="Unique component identifier")
    
    class Config:
        orm_mode = True


class ComponentList(BaseModel):
    """List of components"""
    components: List[Component]
    total: int
