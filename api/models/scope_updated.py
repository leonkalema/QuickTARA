"""
Product Scope models for FastAPI (Updated to product-centric approach)
"""
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ProductType(str, Enum):
    """Product types for scope definition"""
    ECU = "ECU"
    GATEWAY = "Gateway"
    SENSOR = "Sensor"
    ACTUATOR = "Actuator"
    NETWORK = "Network"
    EXTERNAL_DEVICE = "ExternalDevice"
    OTHER = "Other"


class SafetyLevel(str, Enum):
    """Product safety levels (ASIL)"""
    QM = "QM"
    ASIL_A = "ASIL A"
    ASIL_B = "ASIL B"
    ASIL_C = "ASIL C"
    ASIL_D = "ASIL D"


class TrustZone(str, Enum):
    """Product trust zones"""
    CRITICAL = "Critical"
    BOUNDARY = "Boundary"
    STANDARD = "Standard"
    UNTRUSTED = "Untrusted"


class ProductScopeBase(BaseModel):
    """Base Product Scope attributes"""
    name: str = Field(..., description="Name of the product being analyzed")
    product_type: ProductType = Field(..., description="Type of product being analyzed")
    description: Optional[str] = Field(None, description="Detailed description of the product")
    boundaries: Optional[List[str]] = Field(default_factory=list, description="Product boundaries")
    objectives: Optional[List[str]] = Field(default_factory=list, description="Analysis objectives")
    stakeholders: Optional[List[str]] = Field(default_factory=list, description="Stakeholders involved")
    
    # Product-wide properties (moved from component level)
    safety_level: SafetyLevel = Field(..., description="Product safety level (ASIL)")
    interfaces: List[str] = Field(default_factory=list, description="Communication interfaces")
    access_points: List[str] = Field(default_factory=list, description="Physical access points")
    location: str = Field(..., description="Physical location (Internal/External)")
    trust_zone: TrustZone = Field(..., description="Security trust zone")


class ProductScopeCreate(ProductScopeBase):
    """Used for creating a new product scope"""
    scope_id: Optional[str] = Field(None, description="Optional unique product identifier")
    
    
class ProductScopeUpdate(BaseModel):
    """Used for updating an existing product scope"""
    name: Optional[str] = None
    product_type: Optional[ProductType] = None
    description: Optional[str] = None
    boundaries: Optional[List[str]] = None
    objectives: Optional[List[str]] = None
    stakeholders: Optional[List[str]] = None
    safety_level: Optional[SafetyLevel] = None
    interfaces: Optional[List[str]] = None
    access_points: Optional[List[str]] = None
    location: Optional[str] = None
    trust_zone: Optional[TrustZone] = None


class ProductScope(ProductScopeBase):
    """Full product scope model with ID, timestamps, and versioning"""
    scope_id: str = Field(..., description="Unique product identifier")
    version: int = Field(1, description="Version number of this product definition")
    is_current: bool = Field(True, description="Whether this is the current version")
    revision_notes: Optional[str] = Field(None, description="Notes on this revision")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = Field(None, description="User who created this product")
    updated_by: Optional[str] = Field(None, description="User who last updated this product")
    
    class Config:
        from_attributes = True


class ProductScopeList(BaseModel):
    """List of product scopes"""
    scopes: List[ProductScope]
    total: int


class ProductScopeHistory(BaseModel):
    """Historical versions of a product scope"""
    product_id: str = Field(..., description="Product identifier")
    versions: List[ProductScope]
    total: int
