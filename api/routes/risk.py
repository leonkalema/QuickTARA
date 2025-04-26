"""
Risk Calculation Framework API routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from api.deps.db import get_db
from api.models.risk import (
    RiskFrameworkConfiguration,
    RiskFrameworkCreate,
    RiskFrameworkUpdate,
    RiskFrameworkList
)
from api.services.risk_service import (
    create_risk_framework,
    get_risk_framework,
    get_active_risk_framework,
    list_risk_frameworks,
    count_risk_frameworks,
    update_risk_framework,
    set_framework_active,
    delete_risk_framework
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=RiskFrameworkConfiguration, status_code=status.HTTP_201_CREATED)
async def create_new_risk_framework(
    framework: RiskFrameworkCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new risk calculation framework
    """
    try:
        return create_risk_framework(db, framework)
    except Exception as e:
        logger.error(f"Error creating risk framework: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the risk framework: {str(e)}"
        )


@router.get("", response_model=RiskFrameworkList)
async def get_risk_frameworks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all risk frameworks with pagination
    """
    try:
        frameworks = list_risk_frameworks(db, skip=skip, limit=limit)
        total = count_risk_frameworks(db)
        return RiskFrameworkList(frameworks=frameworks, total=total)
    except Exception as e:
        logger.error(f"Error retrieving risk frameworks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving risk frameworks: {str(e)}"
        )


@router.get("/active", response_model=RiskFrameworkConfiguration)
async def get_current_active_framework(
    db: Session = Depends(get_db)
):
    """
    Get the currently active risk framework
    """
    try:
        framework = get_active_risk_framework(db)
        if not framework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active risk framework found"
            )
        return framework
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving active risk framework: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the active risk framework: {str(e)}"
        )


@router.get("/{framework_id}", response_model=RiskFrameworkConfiguration)
async def get_risk_framework_by_id(
    framework_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a risk framework by ID
    """
    try:
        framework = get_risk_framework(db, framework_id)
        if not framework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Risk framework with ID {framework_id} not found"
            )
        return framework
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving risk framework: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the risk framework: {str(e)}"
        )


@router.put("/{framework_id}", response_model=RiskFrameworkConfiguration)
async def update_existing_risk_framework(
    framework_id: str,
    framework_update: RiskFrameworkUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing risk framework
    """
    try:
        updated_framework = update_risk_framework(db, framework_id, framework_update)
        if not updated_framework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Risk framework with ID {framework_id} not found"
            )
        return updated_framework
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating risk framework: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the risk framework: {str(e)}"
        )


@router.put("/{framework_id}/active", response_model=RiskFrameworkConfiguration)
async def set_risk_framework_active_status(
    framework_id: str,
    active: bool = True,
    db: Session = Depends(get_db)
):
    """
    Set a risk framework as active or inactive
    """
    try:
        updated_framework = set_framework_active(db, framework_id, active)
        if not updated_framework:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Risk framework with ID {framework_id} not found"
            )
        return updated_framework
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting framework active status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while setting the framework active status: {str(e)}"
        )


@router.delete("/{framework_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_risk_framework(
    framework_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a risk framework
    """
    try:
        success = delete_risk_framework(db, framework_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Risk framework with ID {framework_id} not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting risk framework: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the risk framework: {str(e)}"
        )
