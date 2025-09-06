from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
import functools

from .security import security, security_manager, extract_user_from_token
from ..deps.db import get_db
from ..models.user import User, UserRole, user_organizations

class AuthDependency:
    def __init__(self, required_permissions: List[str] = None, require_org_access: bool = True):
        self.required_permissions = required_permissions or []
        self.require_org_access = require_org_access

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    
    # Verify token
    token_payload = security_manager.verify_token(credentials.credentials)
    user_data = extract_user_from_token(token_payload)
    
    # Get user from database
    user = db.query(User).filter(User.user_id == user_data["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check if user is active
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active"
        )
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user (additional validation)"""
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_roles(allowed_roles: List[UserRole]):
    """Decorator to require specific roles"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs or dependencies
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication dependency not properly configured"
                )
            
            # Check if user has any of the allowed roles
            user_roles = get_user_roles(current_user)
            if not any(role in allowed_roles for role in user_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_permissions(required_permissions: List[str], organization_id: Optional[str] = None):
    """Decorator to require specific permissions"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication dependency not properly configured"
                )
            
            # Check permissions
            if not check_user_permissions(current_user, required_permissions, organization_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def get_user_roles(user: User, organization_id: Optional[str] = None) -> List[UserRole]:
    """Get user's roles, optionally filtered by organization"""
    if user.is_superuser:
        return [UserRole.TOOL_ADMIN]
    
    # This would query the user_organizations table to get roles
    # For now, returning a placeholder
    return [UserRole.TARA_ANALYST]  # Default role

def check_user_permissions(user: User, required_permissions: List[str], organization_id: Optional[str] = None) -> bool:
    """Check if user has required permissions"""
    
    # Tool admin has all permissions
    if user.is_superuser:
        return True
    
    # Get user roles
    user_roles = get_user_roles(user, organization_id)
    
    # Import role permissions from user model
    from ..models.user import ROLE_PERMISSIONS
    
    # Check if user has any role that grants the required permissions
    for role in user_roles:
        role_perms = ROLE_PERMISSIONS.get(role, [])
        
        # Check for wildcard permission
        if "*:*" in role_perms:
            return True
        
        # Check each required permission
        for required_perm in required_permissions:
            if required_perm in role_perms:
                return True
            
            # Check for wildcard resource permissions (e.g., "damage_scenarios:*")
            resource = required_perm.split(":")[0]
            if f"{resource}:*" in role_perms:
                return True
    
    return False

# Convenience dependency functions for common roles
async def require_tool_admin(current_user: User = Depends(get_current_active_user)):
    """Require Tool Admin role"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tool Admin access required"
        )
    return current_user

async def require_risk_manager(current_user: User = Depends(get_current_active_user)):
    """Require Risk Manager role or higher"""
    user_roles = get_user_roles(current_user)
    allowed_roles = [UserRole.TOOL_ADMIN, UserRole.ORG_ADMIN, UserRole.RISK_MANAGER]
    
    if not any(role in allowed_roles for role in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Risk Manager access required"
        )
    return current_user

async def require_compliance_officer(current_user: User = Depends(get_current_active_user)):
    """Require Compliance Officer role or higher"""
    user_roles = get_user_roles(current_user)
    allowed_roles = [UserRole.TOOL_ADMIN, UserRole.ORG_ADMIN, UserRole.COMPLIANCE_OFFICER]
    
    if not any(role in allowed_roles for role in user_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compliance Officer access required"
        )
    return current_user

# Optional authentication (for endpoints that work with or without auth)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
