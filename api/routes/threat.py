"""
API routes for threat catalog and STRIDE analysis
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps.db import get_db
from api.models.threat import (
    ThreatCatalogItem,
    ThreatCatalogCreate,
    ThreatCatalogUpdate,
    ThreatCatalogList,
    ThreatAnalysisRequest,
    ThreatAnalysisResponse,
    StrideCategory
)
from api.services.threat_service import (
    create_threat_catalog_item,
    get_threat_catalog_items,
    get_threat_catalog_item,
    update_threat_catalog_item,
    delete_threat_catalog_item,
    perform_threat_analysis
)
from core.threat_catalog.catalog_seeder import seed_from_stix, get_catalog_stats
from api.auth.dependencies import get_current_active_user
from api.models.user import User

router = APIRouter(
    prefix="",  # Remove the /threat prefix since it will be added in app.py
    tags=["threat"],
    responses={404: {"description": "Resource not found"}},
)


@router.post("/catalog", response_model=ThreatCatalogItem, status_code=status.HTTP_201_CREATED)
async def create_new_catalog_item(
    threat: ThreatCatalogCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new threat catalog item
    """
    return create_threat_catalog_item(db, threat)


@router.get("/catalog", response_model=ThreatCatalogList)
async def list_catalog_items(
    skip: int = 0, 
    limit: int = 100,
    stride_category: Optional[StrideCategory] = None,
    component_type: Optional[str] = None,
    trust_zone: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List threat catalog items with optional filtering
    """
    items = get_threat_catalog_items(
        db, 
        skip=skip, 
        limit=limit, 
        stride_category=stride_category,
        component_type=component_type,
        trust_zone=trust_zone
    )
    return {"catalog_items": items, "total": len(items)}

# Insert bulk endpoint right after /catalog (list/create) routes to ensure it is matched before /catalog/{threat_id}
@router.post("/catalog/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_create_catalog_items(
    threats: List[ThreatCatalogCreate],
    db: Session = Depends(get_db)
):
    """Bulk create threat catalog items"""
    created_items = [create_threat_catalog_item(db, t) for t in threats]
    return {"inserted": len(created_items), "catalog_items": created_items}

@router.post("/catalog/seed-mitre")
async def seed_mitre_catalog(
    force_update: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Seed threat catalog from MITRE ATT&CK ICS STIX bundle.
    Requires Tool Admin role. Set force_update=true to overwrite user-modified entries.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Tool Admin access required")
    result = seed_from_stix(db, force_update=force_update)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=f"Seed failed: {result['error']}")
    return result


@router.get("/catalog/stats")
async def catalog_statistics(db: Session = Depends(get_db)):
    """Return summary statistics about the threat catalog."""
    return get_catalog_stats(db)


@router.get("/catalog/{threat_id}", response_model=ThreatCatalogItem)
async def get_catalog_item(threat_id: str, db: Session = Depends(get_db)):
    """
    Get a specific threat catalog item by ID
    """
    item = get_threat_catalog_item(db, threat_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Threat catalog item with ID {threat_id} not found"
        )
    return item


@router.put("/catalog/{threat_id}", response_model=ThreatCatalogItem)
async def update_catalog_item(
    threat_id: str, 
    threat_update: ThreatCatalogUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing threat catalog item
    """
    updated_item = update_threat_catalog_item(db, threat_id, threat_update)
    if not updated_item:
        raise HTTPException(
            status_code=404,
            detail=f"Threat catalog item with ID {threat_id} not found"
        )
    return updated_item


@router.delete("/catalog/{threat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalog_item(threat_id: str, db: Session = Depends(get_db)):
    """
    Delete a threat catalog item
    """
    success = delete_threat_catalog_item(db, threat_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Threat catalog item with ID {threat_id} not found"
        )
    return None


@router.post("/analyze", response_model=ThreatAnalysisResponse)
async def analyze_threats(
    analysis_request: ThreatAnalysisRequest, 
    db: Session = Depends(get_db)
):
    """
    Perform STRIDE threat analysis for the specified components
    """
    # Check if component IDs exist
    if not analysis_request.component_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one component ID is required for analysis"
        )
    
    try:
        return perform_threat_analysis(db, analysis_request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing threat analysis: {str(e)}"
        )


