from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()

class UserRole(str, enum.Enum):
    TOOL_ADMIN = "tool_admin"      # System administration only
    ORG_ADMIN = "org_admin"        # Full access within organization (includes product management)
    ANALYST = "analyst"            # TARA analysis work: assets, damage/threat scenarios, attack paths
    RISK_MANAGER = "risk_manager"  # Risk approvals and treatments
    AUDITOR = "auditor"            # Read-only access + compliance review
    VIEWER = "viewer"              # Read-only access to assigned products

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

# Association table for user-organization many-to-many relationship
user_organizations = Table(
    'user_organizations',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.user_id'), primary_key=True),
    Column('organization_id', String, ForeignKey('organizations.organization_id'), primary_key=True),
    Column('role', Enum(UserRole), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Organization(Base):
    __tablename__ = "organizations"
    
    organization_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    domain = Column(String(255))  # Email domain for auto-assignment
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_organizations, back_populates="organizations")

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # User status and metadata
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)  # Tool Admin flag
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Security fields
    failed_login_attempts = Column(String, default="0")
    locked_until = Column(DateTime)
    
    # Relationships
    organizations = relationship("Organization", secondary=user_organizations, back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_role_in_organization(self, organization_id: str) -> UserRole:
        """Get user's role in a specific organization"""
        # This would be implemented with a query to user_organizations table
        pass
    
    def has_permission(self, permission: str, organization_id: str = None) -> bool:
        """Check if user has a specific permission"""
        # This would implement the RBAC logic
        pass

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    token_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    token_hash = Column(String(255), nullable=False)  # Hashed refresh token
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Device/session tracking
    device_info = Column(String(500))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

class Permission(Base):
    __tablename__ = "permissions"
    
    permission_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    resource = Column(String(100), nullable=False)  # e.g., 'damage_scenarios', 'reports'
    action = Column(String(50), nullable=False)     # e.g., 'create', 'read', 'update', 'delete'
    
class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    role = Column(Enum(UserRole), primary_key=True)
    permission_id = Column(String, ForeignKey('permissions.permission_id'), primary_key=True)
    organization_scope = Column(Boolean, default=True)  # Whether permission is org-scoped
    
    # Relationships
    permission = relationship("Permission")

# RBAC Permission Definitions
ROLE_PERMISSIONS = {
    UserRole.TOOL_ADMIN: [
        "users:create", "users:read", "users:update", "users:delete",
        "organizations:create", "organizations:read", "organizations:update", "organizations:delete",
        "system:configure", "system:backup", "system:monitor",
        "audit_trail:read", "templates:*"
    ],
    UserRole.ORG_ADMIN: [
        # User management within org
        "users:create", "users:read", "users:update", "users:delete",
        # Full product/asset management (includes Product Owner capabilities)
        "products:create", "products:read", "products:update", "products:delete",
        "assets:create", "assets:read", "assets:update", "assets:delete",
        # Full analysis capabilities
        "damage_scenarios:create", "damage_scenarios:read", "damage_scenarios:update", "damage_scenarios:delete",
        "threat_scenarios:create", "threat_scenarios:read", "threat_scenarios:update", "threat_scenarios:delete",
        "attack_paths:create", "attack_paths:read", "attack_paths:update", "attack_paths:delete",
        "risk_treatments:create", "risk_treatments:read", "risk_treatments:update", "risk_treatments:delete",
        # Reports and settings
        "reports:generate", "reports:read",
        "org_settings:update"
    ],
    UserRole.ANALYST: [
        # Asset management
        "assets:create", "assets:read", "assets:update", "assets:delete",
        # Full TARA analysis work
        "damage_scenarios:create", "damage_scenarios:read", "damage_scenarios:update", "damage_scenarios:delete",
        "threat_scenarios:create", "threat_scenarios:read", "threat_scenarios:update", "threat_scenarios:delete",
        "attack_paths:create", "attack_paths:read", "attack_paths:update", "attack_paths:delete",
        "risk_treatments:create", "risk_treatments:read", "risk_treatments:update",
        # Read access to products
        "products:read",
        # Reports access
        "reports:read", "reports:generate"
    ],
    UserRole.RISK_MANAGER: [
        # Risk approvals
        "risk_treatments:approve", "risk_treatments:read", "risk_treatments:update",
        "risk_acceptance:approve",
        # Read access to analysis data
        "damage_scenarios:read", "threat_scenarios:read", "attack_paths:read",
        "products:read", "assets:read",
        # Reports
        "reports:generate", "reports:read"
    ],
    UserRole.AUDITOR: [
        # Read-only access to everything + compliance
        "products:read", "assets:read",
        "damage_scenarios:read", "threat_scenarios:read", "attack_paths:read",
        "risk_treatments:read", "reports:read", "audit_trail:read",
        "compliance:review", "compliance:audit"
    ],
    UserRole.VIEWER: [
        # Read-only access to assigned products
        "products:read", "assets:read",
        "damage_scenarios:read", "threat_scenarios:read",
        "reports:read"
    ]
}
