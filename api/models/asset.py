"""
Asset models for FastAPI (Replaces component.py in product-centric approach)
"""
from enum import Enum
from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator


class AssetType(str, Enum):
    """Types of assets within a product"""
    FIRMWARE = "Firmware"
    SOFTWARE = "Software"
    CONFIGURATION = "Configuration"
    CALIBRATION = "Calibration"
    DATA = "Data"
    DIAGNOSTIC = "Diagnostic"
    COMMUNICATION = "Communication"
    HARDWARE = "Hardware"
    INTERFACE = "Interface"
    OTHER = "Other"


class SecurityLevel(str, Enum):
    """Security levels for CIA properties"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NOT_APPLICABLE = "N/A"


class AssetBase(BaseModel):
    """Base Asset attributes"""
    name: str = Field(..., description="Asset name")
    description: Optional[str] = Field(None, description="Detailed asset description")
    asset_type: AssetType = Field(..., description="Type of asset")
    data_types: List[str] = Field(default_factory=list, description="Types of data handled by this asset")
    storage_location: Optional[str] = Field(None, description="Where the asset is stored/located within the product")
    
    # Scope reference (required)
    scope_id: str = Field(..., description="Parent product (scope) ID")
    scope_version: Optional[int] = Field(1, description="Version of the parent product this asset is associated with")
    
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


class AssetCreate(AssetBase):
    """Used for creating a new asset"""
    asset_id: Optional[str] = Field(None, description="Optional unique asset identifier")


class AssetUpdate(BaseModel):
    """Used for updating an existing asset"""
    name: Optional[str] = None
    description: Optional[str] = None
    asset_type: Optional[AssetType] = None
    data_types: Optional[List[str]] = None
    storage_location: Optional[str] = None
    scope_id: Optional[str] = None
    scope_version: Optional[int] = None
    
    # Security properties
    confidentiality: Optional[SecurityLevel] = None
    integrity: Optional[SecurityLevel] = None
    availability: Optional[SecurityLevel] = None
    authenticity_required: Optional[bool] = None
    authorization_required: Optional[bool] = None


class Asset(AssetBase):
    """Full asset model with ID, timestamps, and versioning"""
    asset_id: str = Field(..., description="Unique asset identifier")
    version: int = Field(1, description="Version number of this asset")
    is_current: bool = Field(True, description="Whether this is the current version")
    revision_notes: Optional[str] = Field(None, description="Notes on this revision")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = Field(None, description="User who created this asset")
    updated_by: Optional[str] = Field(None, description="User who last updated this asset")
    
    class Config:
        from_attributes = True


class AssetList(BaseModel):
    """List of assets"""
    assets: List[Asset]
    total: int


class AssetHistory(BaseModel):
    """Historical versions of an asset"""
    asset_id: str = Field(..., description="Asset identifier")
    versions: List[Asset]
    total: int
