"""
Component API routes
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import StringIO
import logging

from api.deps.db import get_db
from api.models.component import Component, ComponentCreate, ComponentUpdate, ComponentList
from api.services import component_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=ComponentList)
async def list_components(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    List all components with pagination
    """
    components = component_service.get_components(db, skip=skip, limit=limit)
    total = component_service.count_components(db)
    return ComponentList(components=components, total=total)


@router.post("", response_model=Component, status_code=status.HTTP_201_CREATED)
async def create_component(
    component: ComponentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new component
    """
    try:
        return component_service.create_component(db, component)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{component_id}", response_model=Component)
async def get_component(
    component_id: str, 
    db: Session = Depends(get_db)
):
    """
    Get a component by ID
    """
    component = component_service.get_component(db, component_id)
    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component with ID {component_id} not found"
        )
    return component


@router.put("/{component_id}", response_model=Component)
async def update_component(
    component_id: str, 
    component: ComponentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a component
    """
    updated = component_service.update_component(db, component_id, component)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component with ID {component_id} not found"
        )
    return updated


@router.delete("/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_component(
    component_id: str, 
    db: Session = Depends(get_db)
):
    """
    Delete a component
    """
    success = component_service.delete_component(db, component_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Component with ID {component_id} not found"
        )
    return None


@router.post("/import", status_code=status.HTTP_200_OK)
async def import_components(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Import components from CSV file
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        content = await file.read()
        csv_content = content.decode('utf-8')
        result = component_service.import_components_from_csv(db, csv_content)
        return result
    except Exception as e:
        logger.error(f"Error importing components: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing components: {str(e)}"
        )


@router.get("/export", status_code=status.HTTP_200_OK)
async def export_components(db: Session = Depends(get_db)):
    """
    Export components to CSV file
    """
    try:
        csv_content = component_service.export_components_to_csv(db)
        return StreamingResponse(
            StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=components.csv"
            }
        )
    except Exception as e:
        logger.error(f"Error exporting components: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting components: {str(e)}"
        )
