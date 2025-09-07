from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from ..deps.db import get_db
from ..models.user import Organization
from ..auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/organizations", tags=["organizations"])

class OrganizationCreate(BaseModel):
    name: str
    description: str = ""

class OrganizationUpdate(BaseModel):
    name: str
    description: str = ""

class OrganizationResponse(BaseModel):
    organization_id: str
    name: str
    description: str
    created_at: datetime
    user_count: int = 0

    class Config:
        from_attributes = True

@router.get("", response_model=dict)
async def get_organizations(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all organizations"""
    try:
        organizations = db.query(Organization).all()
        
        org_list = []
        for org in organizations:
            # Count users in this organization (simplified for now)
            user_count = len(org.users) if org.users else 0
            
            org_list.append({
                "organization_id": org.organization_id,
                "name": org.name,
                "description": org.description or "",
                "created_at": org.created_at.isoformat(),
                "user_count": user_count
            })
        
        return {"organizations": org_list}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organizations: {str(e)}"
        )

@router.post("", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new organization"""
    try:
        new_org = Organization(
            organization_id=str(uuid.uuid4()),
            name=org_data.name,
            description=org_data.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        
        return OrganizationResponse(
            organization_id=new_org.organization_id,
            name=new_org.name,
            description=new_org.description or "",
            created_at=new_org.created_at,
            user_count=0
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )

@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: str,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an organization"""
    try:
        org = db.query(Organization).filter(Organization.organization_id == organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        org.name = org_data.name
        org.description = org_data.description
        org.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(org)
        
        user_count = len(org.users) if org.users else 0
        
        return OrganizationResponse(
            organization_id=org.organization_id,
            name=org.name,
            description=org.description or "",
            created_at=org.created_at,
            user_count=user_count
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update organization: {str(e)}"
        )

@router.delete("/{organization_id}")
async def delete_organization(
    organization_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an organization"""
    try:
        org = db.query(Organization).filter(Organization.organization_id == organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Check if organization has users
        if org.users and len(org.users) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete organization with existing users"
            )
        
        db.delete(org)
        db.commit()
        
        return {"message": "Organization deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete organization: {str(e)}"
        )
