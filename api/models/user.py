from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()

class UserRole(str, enum.Enum):
    TOOL_ADMIN = "tool_admin"
    ORG_ADMIN = "org_admin"
    RISK_MANAGER = "risk_manager"
    COMPLIANCE_OFFICER = "compliance_officer"
    PRODUCT_OWNER = "product_owner"
    SECURITY_ENGINEER = "security_engineer"
    TARA_ANALYST = "tara_analyst"
    AUDITOR = "auditor"

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
        "*:*"  # Full system access
    ],
    UserRole.ORG_ADMIN: [
        "users:create", "users:read", "users:update", "users:delete",  # Within org only
        "products:create", "products:read", "products:update", "products:delete",
        "reports:generate", "reports:read",
        "org_settings:update"
    ],
    UserRole.RISK_MANAGER: [
        "risk_treatments:approve", "risk_treatments:read", "risk_treatments:update",
        "damage_scenarios:read", "threat_scenarios:read",
        "reports:read", "reports:generate",
        "risk_acceptance:approve"
    ],
    UserRole.COMPLIANCE_OFFICER: [
        "reports:generate", "reports:read", "reports:approve",
        "compliance:review", "compliance:audit",
        "damage_scenarios:read", "threat_scenarios:read", "risk_treatments:read",
        "audit_trail:read"
    ],
    UserRole.PRODUCT_OWNER: [
        "products:create", "products:read", "products:update",
        "assets:create", "assets:read", "assets:update",
        "damage_scenarios:read", "risk_treatments:read",
        "reports:read"
    ],
    UserRole.SECURITY_ENGINEER: [
        "threat_scenarios:create", "threat_scenarios:read", "threat_scenarios:update",
        "attack_paths:create", "attack_paths:read", "attack_paths:update",
        "damage_scenarios:read", "damage_scenarios:update",
        "risk_treatments:create", "risk_treatments:read", "risk_treatments:update"
    ],
    UserRole.TARA_ANALYST: [
        "damage_scenarios:create", "damage_scenarios:read", "damage_scenarios:update",
        "threat_scenarios:create", "threat_scenarios:read", "threat_scenarios:update",
        "attack_paths:create", "attack_paths:read", "attack_paths:update",
        "risk_treatments:create", "risk_treatments:read", "risk_treatments:update",
        "assets:read", "products:read"
    ],
    UserRole.AUDITOR: [
        "damage_scenarios:read", "threat_scenarios:read", "attack_paths:read",
        "risk_treatments:read", "reports:read", "audit_trail:read",
        "products:read", "assets:read"
    ]
}
