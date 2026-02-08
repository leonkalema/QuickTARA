"""
Product and Asset Database Models for QuickTARA

This file contains updated SQLAlchemy models to support a product-centric approach
where Scope represents a product (e.g., an ECU) and Components represent assets 
within that product.
"""
from sqlalchemy import Column, String, Enum, ForeignKey, Table, DateTime, Integer, Float, Text, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON, ARRAY
from sqlalchemy.sql import func
import enum
from datetime import datetime

Base = declarative_base()

# Association tables for many-to-many relationships
asset_connections = Table(
    'asset_connections',
    Base.metadata,
    Column('asset_id', String, ForeignKey('assets.asset_id'), primary_key=True),
    Column('connected_to_id', String, ForeignKey('assets.asset_id'), primary_key=True)
)

asset_damage_scenario = Table(
    "asset_damage_scenario",
    Base.metadata,
    Column("asset_id", String, ForeignKey("assets.asset_id")),
    Column("scenario_id", String, ForeignKey("damage_scenarios.scenario_id"))
)


# Enums for database constraints
class ProductTypeEnum(str, enum.Enum):
    """Product types for scope definition"""
    ECU = "ECU"
    GATEWAY = "Gateway"
    SENSOR = "Sensor"
    ACTUATOR = "Actuator"
    NETWORK = "Network"
    EXTERNAL_DEVICE = "ExternalDevice"
    OTHER = "Other"


class SafetyLevelEnum(str, enum.Enum):
    """Safety levels (ASIL)"""
    QM = "QM"
    ASIL_A = "ASIL A"
    ASIL_B = "ASIL B"
    ASIL_C = "ASIL C"
    ASIL_D = "ASIL D"


class TrustZoneEnum(str, enum.Enum):
    """Trust zones"""
    CRITICAL = "Critical"
    BOUNDARY = "Boundary"
    STANDARD = "Standard"
    UNTRUSTED = "Untrusted"


class AssetTypeEnum(str, enum.Enum):
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


class SecurityLevelEnum(str, enum.Enum):
    """Security levels for CIA properties"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NOT_APPLICABLE = "N/A"


# ProductScope model (represents a product, e.g., ECU)
class ProductScope(Base):
    """SQLAlchemy model for product scopes (e.g., ECUs)"""
    __tablename__ = "product_scopes"
    
    # Primary Key
    scope_id = Column(String, primary_key=True, index=True)
    
    # Organization/Department ownership
    organization_id = Column(String, nullable=True, index=True)
    
    # Basic Information
    name = Column(String, nullable=False)
    product_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Product Properties (moved from component level)
    safety_level = Column(String, nullable=False)
    interfaces = Column(JSON, default=lambda: [])
    access_points = Column(JSON, default=lambda: [])
    location = Column(String, nullable=False)
    trust_zone = Column(String, nullable=False)
    
    # Additional fields
    boundaries = Column(JSON, default=lambda: [])
    objectives = Column(JSON, default=lambda: [])
    stakeholders = Column(JSON, default=lambda: [])
    
    # Versioning and audit
    version = Column(Integer, default=1, nullable=False)
    is_current = Column(Boolean, default=True, nullable=False)
    revision_notes = Column(Text, nullable=True)
    
    # Timestamps and audit
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    # Relationships
    assets = relationship("Asset", back_populates="product_scope")
    damage_scenarios = relationship("DamageScenario", back_populates="product_scope")
    history = relationship(
        "ProductScopeHistory",
        back_populates="product_scope",
        order_by="desc(ProductScopeHistory.version)"
    )


# Product Scope History for versioning
class ProductScopeHistory(Base):
    """SQLAlchemy model for product scope history/versions"""
    __tablename__ = "product_scope_history"
    
    # Primary Key (composite)
    id = Column(Integer, primary_key=True, autoincrement=True)
    scope_id = Column(String, ForeignKey("product_scopes.scope_id"), nullable=False)
    version = Column(Integer, nullable=False)
    
    # Basic Information
    name = Column(String, nullable=False)
    product_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Product Properties
    safety_level = Column(String, nullable=False)
    interfaces = Column(JSON, default=lambda: [])
    access_points = Column(JSON, default=lambda: [])
    location = Column(String, nullable=False)
    trust_zone = Column(String, nullable=False)
    
    # Additional fields
    boundaries = Column(JSON, default=lambda: [])
    objectives = Column(JSON, default=lambda: [])
    stakeholders = Column(JSON, default=lambda: [])
    
    # Versioning and audit
    is_current = Column(Boolean, default=False, nullable=False)
    revision_notes = Column(Text, nullable=True)
    
    # Timestamps and audit
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    # Relationship back to current version
    product_scope = relationship("ProductScope", back_populates="history")
    
    # Ensure uniqueness of scope_id and version combination
    __table_args__ = (
        UniqueConstraint('scope_id', 'version', name='unique_product_version'),
    )


# Asset model (represents assets within a product)
class Asset(Base):
    """SQLAlchemy model for assets (valuable items within a product)"""
    __tablename__ = "assets"
    
    # Primary Key
    asset_id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    asset_type = Column(String, nullable=False)
    data_types = Column(JSON, default=lambda: [])
    storage_location = Column(String, nullable=True)
    
    # Scope reference
    scope_id = Column(String, ForeignKey("product_scopes.scope_id"), nullable=False)
    scope_version = Column(Integer, default=1, nullable=False)
    
    # Security properties
    confidentiality = Column(String, default="Medium", nullable=False)
    integrity = Column(String, default="Medium", nullable=False)
    availability = Column(String, default="Medium", nullable=False)
    authenticity_required = Column(Boolean, default=False, nullable=False)
    authorization_required = Column(Boolean, default=False, nullable=False)
    
    # Versioning and audit
    version = Column(Integer, default=1, nullable=False)
    is_current = Column(Boolean, default=True, nullable=False)
    revision_notes = Column(Text, nullable=True)
    
    # Timestamps and audit
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    # Relationships
    product_scope = relationship("ProductScope", back_populates="assets")
    connected_to = relationship(
        "Asset",
        secondary=asset_connections,
        primaryjoin=asset_id==asset_connections.c.asset_id,
        secondaryjoin=asset_id==asset_connections.c.connected_to_id,
        backref="connected_from"
    )
    damage_scenarios = relationship(
        "DamageScenario",
        secondary=asset_damage_scenario,
        back_populates="affected_assets"
    )
    history = relationship(
        "AssetHistory",
        back_populates="asset",
        order_by="desc(AssetHistory.version)"
    )


# Asset History for versioning
class AssetHistory(Base):
    """SQLAlchemy model for asset history/versions"""
    __tablename__ = "asset_history"
    
    # Primary Key (composite)
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String, ForeignKey("assets.asset_id"), nullable=False)
    version = Column(Integer, nullable=False)
    
    # Basic Information
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    asset_type = Column(String, nullable=False)
    data_types = Column(JSON, default=lambda: [])
    storage_location = Column(String, nullable=True)
    
    # Scope reference
    scope_id = Column(String, ForeignKey("product_scopes.scope_id"), nullable=False)
    scope_version = Column(Integer, nullable=False)
    
    # Security properties
    confidentiality = Column(String, nullable=False)
    integrity = Column(String, nullable=False)
    availability = Column(String, nullable=False)
    authenticity_required = Column(Boolean, nullable=False)
    authorization_required = Column(Boolean, nullable=False)
    
    # Versioning and audit
    is_current = Column(Boolean, default=False, nullable=False)
    revision_notes = Column(Text, nullable=True)
    
    # Timestamps and audit
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    
    # Relationship back to current version
    asset = relationship("Asset", back_populates="history")
    
    # Ensure uniqueness of asset_id and version combination
    __table_args__ = (
        UniqueConstraint('asset_id', 'version', name='unique_asset_version'),
    )


# Update DamageScenario to work with assets instead of components
class DamageScenario(Base):
    """SQLAlchemy model for damage scenarios (updated for asset-based model)"""
    __tablename__ = "damage_scenarios"
    
    # Primary Key
    scenario_id = Column(String, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Relationships
    scope_id = Column(String, ForeignKey("product_scopes.scope_id"), nullable=False)
    
    # Security Properties being violated
    violated_properties = Column(JSON, nullable=False)
    
    # Categorization (new column)
    category = Column(String, nullable=True)

    # Legacy columns kept for backward compatibility (NOT NULL constraints in existing DB)
    damage_category = Column(String, nullable=False)
    impact_type = Column(String, nullable=False, default="Direct")
    severity = Column(String, nullable=False, default="Medium")
    confidentiality_impact = Column(Boolean, default=False)
    integrity_impact = Column(Boolean, default=False)
    availability_impact = Column(Boolean, default=False)
    primary_component_id = Column(String, nullable=True)
    
    # SFOP Impact Ratings (severity levels)
    safety_impact = Column(String, default="negligible")
    financial_impact = Column(String, default="negligible")
    operational_impact = Column(String, default="negligible")
    privacy_impact = Column(String, default="negligible")
    
    # Review status: draft (auto-generated) or accepted (reviewed by analyst)
    status = Column(String, default="accepted", nullable=False)
    
    # Versioning & Traceability
    version = Column(Integer, default=1, nullable=False)
    is_current = Column(Boolean, default=True, nullable=False)
    revision_notes = Column(Text, nullable=True)
    
    # Timestamps and audit
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    product_scope = relationship("ProductScope", back_populates="damage_scenarios")
    threat_scenarios = relationship("ThreatScenario", back_populates="damage_scenario")
    
    # Many-to-many relationship with assets
    affected_assets = relationship(
        "Asset",
        secondary=asset_damage_scenario,
        back_populates="damage_scenarios"
    )


# Compatibility with existing ThreatScenario model
class ThreatScenario(Base):
    """SQLAlchemy model for threat scenarios (updated for compatibility)"""
    __tablename__ = "threat_scenarios"
    
    # Primary Key
    scenario_id = Column(String, primary_key=True, index=True)
    
    # Link to damage scenario
    damage_scenario_id = Column(String, ForeignKey("damage_scenarios.scenario_id"))
    
    # Basic Information
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Additional fields (preserved from existing model)
    # Add any fields that are currently in your ThreatScenario model
    
    # Relationships
    damage_scenario = relationship("DamageScenario", back_populates="threat_scenarios")
