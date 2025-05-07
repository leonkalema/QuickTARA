"""
Component models for FastAPI
"""
from enum import Enum
from typing import List, Optional, Set, Union
from pydantic import BaseModel, Field, validator


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


class SecurityLevel(str, Enum):
    """Security levels for CIA properties"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NOT_APPLICABLE = "N/A"


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
    
    # Security properties (C-I-A)
    confidentiality: SecurityLevel = Field(
        default=SecurityLevel.MEDIUM,
        description="Degree of protection for data from unauthorized access"
    )
    integrity: SecurityLevel = Field(
        default=SecurityLevel.MEDIUM, 
        description="Degree of protection from improper modification"
    )
    availability: SecurityLevel = Field(
        default=SecurityLevel.MEDIUM,
        description="Degree of reliable accessibility when needed"
    )
    authenticity_required: bool = Field(
        default=False,
        description="Whether data origin authentication is required"
    )
    authorization_required: bool = Field(
        default=False,
        description="Whether access controls are required"
    )
    
    @validator('confidentiality', 'integrity', 'availability', pre=True)
    def set_smart_defaults(cls, v, values):
        # If value is already specified, return it
        if v is not None:
            return v
            
        # Default to MEDIUM if we can't calculate
        if 'type' not in values or 'safety_level' not in values or 'trust_zone' not in values:
            return SecurityLevel.MEDIUM
        
        component_type = values['type']
        safety_level = values['safety_level']
        trust_zone = values['trust_zone']
        
        # Get the field name from validator context
        field_name = None
        for field in cls.__fields__.values():
            if field.name in ('confidentiality', 'integrity', 'availability'):
                if field.validate_default() == v:
                    field_name = field.name
                    break
                    
        if not field_name:
            return SecurityLevel.MEDIUM
        
        # For safety-critical components (ASIL C or D)
        if safety_level in (SafetyLevel.ASIL_C, SafetyLevel.ASIL_D):
            if field_name in ('integrity', 'availability'):
                return SecurityLevel.HIGH
        
        # For critical trust zone
        if trust_zone == TrustZone.CRITICAL:
            if field_name in ('integrity', 'availability'):
                return SecurityLevel.HIGH
        
        # Type-specific defaults
        if component_type == AssetType.ECU:
            if field_name == 'integrity':
                return SecurityLevel.HIGH
            elif field_name == 'authorization_required':
                return True
        elif component_type == AssetType.GATEWAY:
            if field_name in ('confidentiality', 'integrity'):
                return SecurityLevel.HIGH
            elif field_name in ('authenticity_required', 'authorization_required'):
                return True
        elif component_type == AssetType.SENSOR:
            if field_name == 'integrity':
                return SecurityLevel.HIGH
        elif component_type == AssetType.ACTUATOR:
            if field_name in ('integrity', 'availability'):
                return SecurityLevel.HIGH
        
        # Default if no special case applies
        return SecurityLevel.MEDIUM


class ComponentCreate(ComponentBase):
    """Used for creating a new component"""
    component_id: str = Field(..., description="Unique component identifier")
    # scope_id is inherited from ComponentBase


class ComponentUpdate(BaseModel):
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
    
    # Security properties
    confidentiality: Optional[SecurityLevel] = None
    integrity: Optional[SecurityLevel] = None
    availability: Optional[SecurityLevel] = None
    authenticity_required: Optional[bool] = None
    authorization_required: Optional[bool] = None


class Component(ComponentBase):
    """Full component model with ID"""
    component_id: str = Field(..., description="Unique component identifier")
    
    class Config:
        from_attributes = True


class ComponentList(BaseModel):
    """List of components"""
    components: List[Component]
    total: int
