from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional

from ..deps.db import get_db
from ..models.user import User, UserRole, UserStatus, Organization, RefreshToken
from ..auth.security import security_manager, create_user_token_data
from ..auth.dependencies import get_current_user, require_tool_admin

router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic models for request/response
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    password: str
    organization_id: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    first_name: str
    last_name: str
    status: UserStatus
    is_verified: bool
    created_at: datetime
    organizations: list

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Hash password
    hashed_password = security_manager.get_password_hash(user_data.password)
    
    # Create user
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password,
        status=UserStatus.PENDING,  # Requires activation
        is_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        user_id=new_user.user_id,
        email=new_user.email,
        username=new_user.username,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        status=new_user.status,
        is_verified=new_user.is_verified,
        created_at=new_user.created_at,
        organizations=[]
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens"""
    
    # Find user
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not security_manager.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check user status
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active"
        )
    
    # Get user roles and organizations (simplified for now)
    user_roles = [UserRole.TOOL_ADMIN] if user.is_superuser else [UserRole.TARA_ANALYST]
    user_orgs = []  # Would query user_organizations table
    
    # Create token data
    token_data = create_user_token_data(
        user_id=user.user_id,
        email=user.email,
        roles=[role.value for role in user_roles],
        organizations=user_orgs
    )
    
    # Generate tokens
    access_token = security_manager.create_access_token(token_data)
    refresh_token = security_manager.create_refresh_token({"sub": user.user_id})
    
    # Store refresh token in database
    device_info = request.headers.get("User-Agent", "")
    ip_address = request.client.host if request.client else ""
    
    raw_refresh_token, token_hash = security_manager.generate_refresh_token_hash(
        user.user_id, device_info
    )
    
    refresh_token_record = RefreshToken(
        user_id=user.user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(days=7),
        device_info=device_info,
        ip_address=ip_address,
        user_agent=request.headers.get("User-Agent", "")
    )
    
    db.add(refresh_token_record)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh_token,
        expires_in=30 * 60  # 30 minutes
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    # Verify refresh token format
    try:
        token_payload = security_manager.verify_token(refresh_data.refresh_token, "refresh")
        user_id = token_payload.get("sub")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Find user
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Verify refresh token in database
    device_info = request.headers.get("User-Agent", "")
    
    refresh_token_record = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not refresh_token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found or expired"
        )
    
    # Verify token hash
    if not security_manager.verify_refresh_token_hash(
        refresh_data.refresh_token, refresh_token_record.token_hash, user_id, device_info
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Generate new access token
    user_roles = [UserRole.TOOL_ADMIN] if user.is_superuser else [UserRole.TARA_ANALYST]
    user_orgs = []
    
    token_data = create_user_token_data(
        user_id=user.user_id,
        email=user.email,
        roles=[role.value for role in user_roles],
        organizations=user_orgs
    )
    
    new_access_token = security_manager.create_access_token(token_data)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_data.refresh_token,  # Keep same refresh token
        expires_in=30 * 60
    )

@router.post("/logout")
async def logout_user(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user by revoking refresh token"""
    
    # Revoke refresh token
    refresh_token_record = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.user_id,
        RefreshToken.is_revoked == False
    ).first()
    
    if refresh_token_record:
        refresh_token_record.is_revoked = True
        db.commit()
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        status=current_user.status,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        organizations=[]  # Would populate from relationships
    )

@router.post("/activate-user/{user_id}")
async def activate_user(
    user_id: str,
    admin_user: User = Depends(require_tool_admin),
    db: Session = Depends(get_db)
):
    """Activate a pending user (Tool Admin only)"""
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.status = UserStatus.ACTIVE
    user.is_verified = True
    db.commit()
    
    return {"message": f"User {user.email} activated successfully"}

@router.get("/users")
async def list_users(
    admin_user: User = Depends(require_tool_admin),
    db: Session = Depends(get_db)
):
    """List all users (Tool Admin only)"""
    
    users = db.query(User).all()
    return [
        {
            "user_id": user.user_id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "status": user.status,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
        for user in users
    ]

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(require_tool_admin),
    db: Session = Depends(get_db)
):
    """Delete a user (Tool Admin only)"""
    
    # Prevent admin from deleting themselves
    if user_id == admin_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Find the user to delete
    user_to_delete = db.query(User).filter(User.user_id == user_id).first()
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Store user info for response
    deleted_user_info = {
        "user_id": user_to_delete.user_id,
        "email": user_to_delete.email,
        "username": user_to_delete.username,
        "full_name": user_to_delete.full_name
    }
    
    # Delete the user (cascade will handle related records like refresh tokens)
    db.delete(user_to_delete)
    db.commit()
    
    return {
        "message": f"User {deleted_user_info['email']} deleted successfully",
        "deleted_user": deleted_user_info
    }

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status: UserStatus,
    admin_user: User = Depends(require_tool_admin),
    db: Session = Depends(get_db)
):
    """Update user status (Tool Admin only)"""
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from suspending themselves
    if user_id == admin_user.user_id and status in [UserStatus.SUSPENDED, UserStatus.INACTIVE]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot suspend or deactivate your own account"
        )
    
    old_status = user.status
    user.status = status
    
    # If activating, also verify the user
    if status == UserStatus.ACTIVE:
        user.is_verified = True
    
    db.commit()
    
    return {
        "message": f"User {user.email} status changed from {old_status} to {status}",
        "user_id": user.user_id,
        "email": user.email,
        "old_status": old_status,
        "new_status": status
    }
