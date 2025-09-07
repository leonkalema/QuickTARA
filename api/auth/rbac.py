from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from ..models.user import User, UserRole, user_organizations

def get_user_organizations_with_roles(db: Session, user_id: str) -> List[dict]:
    """Get all organizations a user belongs to with their roles"""
    try:
        memberships = db.execute(
            user_organizations.select().where(
                user_organizations.c.user_id == user_id
            )
        ).fetchall()
        
        return [
            {
                "organization_id": membership.organization_id,
                "role": membership.role,
                "joined_at": membership.created_at
            }
            for membership in memberships
        ]
    except Exception:
        return []

def get_user_role_in_organization(db: Session, user_id: str, organization_id: str) -> Optional[UserRole]:
    """Get user's role in a specific organization"""
    try:
        membership = db.execute(
            user_organizations.select().where(
                and_(
                    user_organizations.c.user_id == user_id,
                    user_organizations.c.organization_id == organization_id
                )
            )
        ).first()
        
        return membership.role if membership else None
    except Exception:
        return None

def user_has_org_permission(db: Session, user_id: str, organization_id: str, required_role: UserRole) -> bool:
    """Check if user has required role or higher in organization"""
    user_role = get_user_role_in_organization(db, user_id, organization_id)
    if not user_role:
        return False
    
    # Role hierarchy (higher roles include lower role permissions)
    role_hierarchy = {
        UserRole.VIEWER: 1,
        UserRole.TARA_ANALYST: 2,
        UserRole.RISK_MANAGER: 3,
        UserRole.ORG_ADMIN: 4,
        UserRole.TOOL_ADMIN: 5
    }
    
    user_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level

def user_is_tool_admin(user: User) -> bool:
    """Check if user is a tool admin (superuser)"""
    return user.is_superuser

def user_can_manage_organization(db: Session, user: User, organization_id: str) -> bool:
    """Check if user can manage an organization (Tool Admin or Org Admin)"""
    if user_is_tool_admin(user):
        return True
    
    return user_has_org_permission(db, user.user_id, organization_id, UserRole.ORG_ADMIN)

def user_can_manage_org_members(db: Session, user: User, organization_id: str) -> bool:
    """Check if user can manage organization members"""
    return user_can_manage_organization(db, user, organization_id)

def user_can_view_organization(db: Session, user: User, organization_id: str) -> bool:
    """Check if user can view an organization"""
    if user_is_tool_admin(user):
        return True
    
    return user_has_org_permission(db, user.user_id, organization_id, UserRole.VIEWER)

def get_user_accessible_organizations(db: Session, user: User) -> List[str]:
    """Get list of organization IDs user has access to"""
    if user_is_tool_admin(user):
        # Tool admins can access all organizations
        from ..models.user import Organization
        orgs = db.query(Organization.organization_id).all()
        return [org.organization_id for org in orgs]
    
    # Regular users can only access their member organizations
    memberships = get_user_organizations_with_roles(db, user.user_id)
    return [membership["organization_id"] for membership in memberships]

# Permission constants for different operations
class OrgPermissions:
    VIEW = "org:view"
    EDIT = "org:edit"
    DELETE = "org:delete"
    MANAGE_MEMBERS = "org:manage_members"
    VIEW_MEMBERS = "org:view_members"

# Role to permissions mapping
ROLE_PERMISSIONS = {
    UserRole.VIEWER: [
        OrgPermissions.VIEW,
        OrgPermissions.VIEW_MEMBERS
    ],
    UserRole.TARA_ANALYST: [
        OrgPermissions.VIEW,
        OrgPermissions.VIEW_MEMBERS
    ],
    UserRole.RISK_MANAGER: [
        OrgPermissions.VIEW,
        OrgPermissions.VIEW_MEMBERS
    ],
    UserRole.ORG_ADMIN: [
        OrgPermissions.VIEW,
        OrgPermissions.EDIT,
        OrgPermissions.MANAGE_MEMBERS,
        OrgPermissions.VIEW_MEMBERS
    ],
    UserRole.TOOL_ADMIN: [
        OrgPermissions.VIEW,
        OrgPermissions.EDIT,
        OrgPermissions.DELETE,
        OrgPermissions.MANAGE_MEMBERS,
        OrgPermissions.VIEW_MEMBERS
    ]
}

def user_has_permission(db: Session, user: User, organization_id: str, permission: str) -> bool:
    """Check if user has specific permission in organization"""
    if user_is_tool_admin(user):
        return True
    
    user_role = get_user_role_in_organization(db, user.user_id, organization_id)
    if not user_role:
        return False
    
    allowed_permissions = ROLE_PERMISSIONS.get(user_role, [])
    return permission in allowed_permissions
