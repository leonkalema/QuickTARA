"""
System Scope API routes
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from api.deps.db import get_db
from api.models.scope import SystemScope, SystemScopeCreate, SystemScopeUpdate, SystemScopeList
from api.services.scope_service import (
    create_scope as service_create_scope,
    get_scope as service_get_scope,
    get_scopes,
    count_scopes,
    update_scope as service_update_scope,
    delete_scope as service_delete_scope
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=SystemScopeList)
async def list_scopes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all system scopes with pagination
    """
    try:
        scopes = get_scopes(db, skip=skip, limit=limit)
        total = count_scopes(db)
        logger.info(f"Found {total} scopes")
        
        # Return directly as a dictionary rather than using the model constructor
        # This bypasses potential orm_mode issues
        return {"scopes": scopes, "total": total}
    except Exception as e:
        logger.error(f"Error listing scopes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing scopes: {str(e)}"
        )


@router.post("", response_model=SystemScope, status_code=status.HTTP_201_CREATED)
async def create_scope(
    scope: SystemScopeCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new system scope
    """
    try:
        return service_create_scope(db, scope)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{scope_id}", response_model=SystemScope)
async def get_scope(
    scope_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a system scope by ID
    """
    scope = service_get_scope(db, scope_id)
    if not scope:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"System scope with ID {scope_id} not found"
        )
    return scope


@router.put("/{scope_id}", response_model=SystemScope)
async def update_scope(
    scope_id: str,
    scope: SystemScopeUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a system scope
    """
    updated = service_update_scope(db, scope_id, scope)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"System scope with ID {scope_id} not found"
        )
    return updated


@router.delete("/{scope_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scope(
    scope_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a system scope
    """
    try:
        success = service_delete_scope(db, scope_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"System scope with ID {scope_id} not found"
            )
        return None
    except Exception as e:
        logger.error(f"Error deleting scope {scope_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting scope: {str(e)}"
        )
