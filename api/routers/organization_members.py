from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime

from ..deps.db import get_db
from ..models.user import User, Organization, user_organizations, UserRole
from ..auth.dependencies import get_current_user
from ..auth.rbac import user_can_manage_org_members, user_can_view_organization
from pydantic import BaseModel

router = APIRouter(prefix="/api/organizations", tags=["organization-members"])

class MemberResponse(BaseModel):
    user_id: str
    email: str
    username: str
    first_name: str
    last_name: str
    role: str
    joined_at: datetime

class AddMemberRequest(BaseModel):
    user_id: str
    role: UserRole

class UpdateMemberRoleRequest(BaseModel):
    role: UserRole

@router.get("/{organization_id}/members", response_model=List[MemberResponse])
async def get_organization_members(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all members of an organization"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Getting members for org {organization_id}, user: {current_user.user_id}")
        
        # Verify organization exists
        org = db.query(Organization).filter(Organization.organization_id == organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check permissions - Tool admins can always view
        if not current_user.is_superuser and not user_can_view_organization(db, current_user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view organization members"
            )

        # Get members with their roles using raw SQL to avoid SQLAlchemy issues
        from sqlalchemy import text
        members_query = db.execute(
            text("""
                SELECT u.user_id, u.email, u.username, u.first_name, u.last_name, 
                       uo.role, uo.created_at
                FROM users u 
                JOIN user_organizations uo ON u.user_id = uo.user_id 
                WHERE uo.organization_id = :org_id
            """),
            {"org_id": organization_id}
        ).fetchall()
        
        members = []
        for row in members_query:
            members.append(MemberResponse(
                user_id=row.user_id,
                email=row.email,
                username=row.username,
                first_name=row.first_name,
                last_name=row.last_name,
                role=row.role,
                joined_at=row.created_at
            ))
        
        return members
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization members: {str(e)}"
        )

@router.post("/{organization_id}/members")
async def add_organization_member(
    organization_id: str,
    member_data: AddMemberRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a user to an organization with a specific role"""
    try:
        # Check permissions first
        if not user_can_manage_org_members(db, current_user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage organization members"
            )

        # Verify organization exists
        org = db.query(Organization).filter(Organization.organization_id == organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Verify user exists
        user = db.query(User).filter(User.user_id == member_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check if user is already a member
        existing = db.execute(
            user_organizations.select().where(
                and_(
                    user_organizations.c.user_id == member_data.user_id,
                    user_organizations.c.organization_id == organization_id
                )
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization"
            )

        # Add membership
        db.execute(
            user_organizations.insert().values(
                user_id=member_data.user_id,
                organization_id=organization_id,
                role=member_data.role,
                created_at=datetime.utcnow()
            )
        )
        db.commit()

        return {"message": "User added to organization successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add user to organization: {str(e)}"
        )

@router.put("/{organization_id}/members/{user_id}")
async def update_member_role(
    organization_id: str,
    user_id: str,
    role_data: UpdateMemberRoleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a member's role in an organization"""
    try:
        # Check permissions
        if not user_can_manage_org_members(db, current_user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage organization members"
            )
        # Verify membership exists
        existing = db.execute(
            user_organizations.select().where(
                and_(
                    user_organizations.c.user_id == user_id,
                    user_organizations.c.organization_id == organization_id
                )
            )
        ).first()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this organization"
            )

        # Update role
        db.execute(
            user_organizations.update().where(
                and_(
                    user_organizations.c.user_id == user_id,
                    user_organizations.c.organization_id == organization_id
                )
            ).values(role=role_data.role)
        )
        db.commit()

        return {"message": "Member role updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update member role: {str(e)}"
        )

@router.delete("/{organization_id}/members/{user_id}")
async def remove_organization_member(
    organization_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove a user from an organization"""
    try:
        # Check permissions
        if not user_can_manage_org_members(db, current_user, organization_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to manage organization members"
            )
        # Verify membership exists
        existing = db.execute(
            user_organizations.select().where(
                and_(
                    user_organizations.c.user_id == user_id,
                    user_organizations.c.organization_id == organization_id
                )
            )
        ).first()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this organization"
            )

        # Check if this is the last ORG_ADMIN (case-insensitive)
        from sqlalchemy import func
        admin_count = db.execute(
            user_organizations.select().where(
                and_(
                    user_organizations.c.organization_id == organization_id,
                    func.lower(user_organizations.c.role) == 'org_admin'
                )
            )
        ).fetchall()
        
        existing_role_lower = (existing.role or '').lower()
        if len(admin_count) == 1 and existing_role_lower == 'org_admin':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the last organization admin"
            )

        # Remove membership
        db.execute(
            user_organizations.delete().where(
                and_(
                    user_organizations.c.user_id == user_id,
                    user_organizations.c.organization_id == organization_id
                )
            )
        )
        db.commit()

        return {"message": "User removed from organization successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove user from organization: {str(e)}"
        )
