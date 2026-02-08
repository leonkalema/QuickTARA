from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime

from ..deps.db import get_db
from ..auth.dependencies import get_current_user, get_current_active_user, require_tool_admin
from ..auth.security import security_manager
from ..models.user import User, UserRole, UserStatus

router = APIRouter(prefix="/api/users", tags=["users"])

# Pydantic models
class UserBase(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.ANALYST
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    user_id: str
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get users - Tool Admin sees all, Org Admin/Risk Manager sees only their department members"""
    from ..models.user import user_organizations
    import logging
    logger = logging.getLogger(__name__)
    
    # Tool Admin sees all users
    if current_user.is_superuser:
        users = db.query(User).offset(skip).limit(limit).all()
        return users
    
    # Get current user's organizations where they have management roles
    user_org_memberships = db.execute(
        user_organizations.select().where(user_organizations.c.user_id == current_user.user_id)
    ).fetchall()
    
    logger.info(f"User {current_user.user_id} memberships: {[(m.organization_id, m.role) for m in user_org_memberships]}")
    
    # Check if user has a management role (ORG_ADMIN or RISK_MANAGER) in any organization
    management_roles = ['org_admin', 'risk_manager']
    is_org_manager = any((m.role or '').lower() in management_roles for m in user_org_memberships)

    # Org managers are allowed to view all non-superuser users so they can add them to their department
    if is_org_manager:
        users = db.query(User).filter(
            User.is_superuser == False
        ).offset(skip).limit(limit).all()
        return users

    admin_org_ids = [m.organization_id for m in user_org_memberships if (m.role or '').lower() in management_roles]
    
    # If no management role, check if they have ANY org membership - let them see their own org's users
    if not admin_org_ids:
        # Fall back to any org membership
        admin_org_ids = [m.organization_id for m in user_org_memberships]
        logger.info(f"User has no management role, falling back to all org memberships: {admin_org_ids}")
    
    if not admin_org_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view users. You must be a member of at least one department."
        )
    
    # Get all users who are members of the organizations where current user is a member
    member_user_ids = db.execute(
        user_organizations.select().where(user_organizations.c.organization_id.in_(admin_org_ids))
    ).fetchall()
    
    user_ids = list(set([m.user_id for m in member_user_ids]))
    
    # Filter out superusers (Tool Admins) - non-admins should not see them
    users = db.query(User).filter(
        User.user_id.in_(user_ids),
        User.is_superuser == False  # Exclude Tool Admins
    ).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tool_admin)
):
    """Get user by ID (admin only)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tool_admin)
):
    """Create new user (admin only)"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = security_manager.get_password_hash(user_data.password)
    db_user = User(
        user_id=str(uuid.uuid4()),
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password,
        status=user_data.status,
        is_verified=True,  # Admin-created users are auto-verified
        is_superuser=(user_data.role == "tool_admin")
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tool_admin)
):
    """Update user (admin only)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields if provided
    update_data = user_data.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = security_manager.get_password_hash(update_data.pop("password"))
        update_data["password_changed_at"] = datetime.utcnow()
    
    if "role" in update_data:
        update_data["is_superuser"] = (update_data["role"] == "tool_admin")
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tool_admin)
):
    """Delete user (admin only)"""
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

class PasswordReset(BaseModel):
    new_password: str

@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    password_data: PasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tool_admin)
):
    """Reset user password (admin only)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.hashed_password = security_manager.get_password_hash(password_data.new_password)
    user.password_changed_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.patch("/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tool_admin)
):
    """Toggle user active/inactive status (admin only)"""
    if user_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own status"
        )
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Toggle between ACTIVE and INACTIVE
    user.status = UserStatus.INACTIVE if user.status == UserStatus.ACTIVE else UserStatus.ACTIVE
    user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    
    return {"message": f"User status changed to {user.status.value}", "status": user.status}
