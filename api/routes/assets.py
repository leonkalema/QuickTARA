"""
Asset API routes for product-centric model
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from datetime import datetime

from api.deps.db import get_db
from core.audit_helpers import get_user_from_request, audit_create, audit_update, audit_delete
from api.models.asset import Asset, AssetCreate, AssetUpdate, AssetList, AssetHistory
from api.utils.error_handlers import handle_database_error, create_success_response, NotFoundAPIError
from db.product_asset_models import Asset as DBAsset, AssetHistory as DBAssetHistory
from db.product_asset_models import ProductScope as DBProductScope

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=AssetList)
async def list_assets(
    skip: int = 0, 
    limit: int = 100,
    scope_id: Optional[str] = None,
    asset_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all assets with pagination and optional filtering
    """
    try:
        # Validate pagination parameters
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Skip parameter must be non-negative", "error_type": "invalid_parameter"}
            )
        if limit <= 0 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Limit must be between 1 and 1000", "error_type": "invalid_parameter"}
            )
        
        query = db.query(DBAsset).filter(DBAsset.is_current == True)
        
        # Apply filters if provided
        if scope_id:
            # Validate scope exists
            scope_exists = db.query(DBProductScope).filter(
                DBProductScope.scope_id == scope_id,
                DBProductScope.is_current == True
            ).first()
            if not scope_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"message": f"Product scope '{scope_id}' not found", "error_type": "resource_not_found"}
                )
            query = query.filter(DBAsset.scope_id == scope_id)
        
        if asset_type:
            # Validate asset_type is valid
            valid_types = ["Hardware", "Software", "Data", "Communication"]
            if asset_type not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": f"Invalid asset type '{asset_type}'",
                        "error_type": "invalid_parameter",
                        "valid_types": valid_types
                    }
                )
            query = query.filter(DBAsset.asset_type == asset_type)
        
        # Get count before pagination
        total = query.count()
        
        # Apply pagination
        assets = query.offset(skip).limit(limit).all()
        
        logger.info(f"Found {total} assets (showing {len(assets)})")
        
        return {"assets": assets, "total": total}
        
    except HTTPException:
        raise
    except (IntegrityError, SQLAlchemyError) as e:
        raise handle_database_error(e, "list assets")
    except Exception as e:
        logger.error(f"Unexpected error listing assets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to retrieve assets", "error_type": "internal_error"}
        )


@router.post("", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset: AssetCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: str = None
):
    """
    Create a new asset
    """
    try:
        # Validate required fields
        if not asset.name or not asset.name.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Asset name is required",
                    "error_type": "validation_error",
                    "field_errors": {"name": "Asset name cannot be empty"}
                }
            )
        
        if len(asset.name.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Asset name too short",
                    "error_type": "validation_error",
                    "field_errors": {"name": "Asset name must be at least 3 characters"}
                }
            )
        
        # Verify product exists
        product = db.query(DBProductScope).filter(
            DBProductScope.scope_id == asset.scope_id,
            DBProductScope.is_current == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": f"Product scope '{asset.scope_id}' not found",
                    "error_type": "resource_not_found",
                    "field_errors": {"scope_id": "Selected product does not exist"}
                }
            )
        
        # Generate asset_id if not provided
        if not asset.asset_id:
            import uuid
            asset.asset_id = f"asset_{uuid.uuid4().hex[:8]}"
        
        # Check if asset with ID already exists
        existing = db.query(DBAsset).filter(DBAsset.asset_id == asset.asset_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f"Asset with ID '{asset.asset_id}' already exists",
                    "error_type": "duplicate_resource",
                    "field_errors": {"asset_id": "This asset ID is already in use"}
                }
            )
        
        # Create new asset
        new_asset = DBAsset(
            asset_id=asset.asset_id,
            name=asset.name,
            description=asset.description,
            asset_type=asset.asset_type,
            data_types=asset.data_types,
            storage_location=asset.storage_location,
            scope_id=asset.scope_id,
            scope_version=product.version,
            confidentiality=asset.confidentiality,
            integrity=asset.integrity,
            availability=asset.availability,
            authenticity_required=asset.authenticity_required,
            authorization_required=asset.authorization_required,
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=user,
            updated_by=user
        )
        db.add(new_asset)
        
        # Create initial history record
        asset_history = DBAssetHistory(
            asset_id=asset.asset_id,
            version=1,
            name=asset.name,
            description=asset.description,
            asset_type=asset.asset_type,
            data_types=asset.data_types,
            storage_location=asset.storage_location,
            scope_id=asset.scope_id,
            scope_version=product.version,
            confidentiality=asset.confidentiality,
            integrity=asset.integrity,
            availability=asset.availability,
            authenticity_required=asset.authenticity_required,
            authorization_required=asset.authorization_required,
            is_current=True,
            revision_notes="Initial creation",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=user,
            updated_by=user
        )
        db.add(asset_history)
        
        performer = get_user_from_request(request)
        audit_create(db, "asset", asset.asset_id, performer, scope_id=asset.scope_id)
        db.commit()
        db.refresh(new_asset)
        
        logger.info(f"Successfully created asset {asset.asset_id}")
        
        return new_asset
        
    except HTTPException:
        db.rollback()
        raise
    except (IntegrityError, SQLAlchemyError) as e:
        db.rollback()
        raise handle_database_error(e, "create asset")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating asset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Failed to create asset", "error_type": "internal_error"}
        )


@router.get("/{asset_id}", response_model=Asset)
async def get_asset(
    asset_id: str, 
    db: Session = Depends(get_db)
):
    """
    Get an asset by ID
    """
    asset = db.query(DBAsset).filter(
        DBAsset.asset_id == asset_id,
        DBAsset.is_current == True
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with ID {asset_id} not found"
        )
    return asset


@router.put("/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: str, 
    asset: AssetUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: str = None
):
    """
    Update an asset
    """
    try:
        # Get current asset
        existing = db.query(DBAsset).filter(
            DBAsset.asset_id == asset_id,
            DBAsset.is_current == True
        ).first()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with ID {asset_id} not found"
            )
        
        # Check if product exists if changing product
        if asset.scope_id and asset.scope_id != existing.scope_id:
            product = db.query(DBProductScope).filter(
                DBProductScope.scope_id == asset.scope_id,
                DBProductScope.is_current == True
            ).first()
            
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {asset.scope_id} not found"
                )
            
            scope_version = product.version
        else:
            scope_version = existing.scope_version
        
        # Create new version
        new_version = existing.version + 1
        
        # Archive current version (set is_current to False)
        existing.is_current = False
        db.add(existing)
        
        # Check if a history record for this version already exists to avoid duplicates
        existing_history = db.query(DBAssetHistory).filter(
            DBAssetHistory.asset_id == asset_id,
            DBAssetHistory.version == existing.version
        ).first()
        
        if not existing_history:
            # Only create a history record if one doesn't exist
            history_record = DBAssetHistory(
                asset_id=asset_id,
                version=existing.version,
                name=existing.name,
                description=existing.description,
                asset_type=existing.asset_type,
                data_types=existing.data_types,
                storage_location=existing.storage_location,
                scope_id=existing.scope_id,
                scope_version=existing.scope_version,
                confidentiality=existing.confidentiality,
                integrity=existing.integrity,
                availability=existing.availability,
                authenticity_required=existing.authenticity_required,
                authorization_required=existing.authorization_required,
                is_current=False,
                revision_notes="Archived version",
                created_at=existing.created_at,
                updated_at=existing.updated_at,
                created_by=existing.created_by,
                updated_by=existing.updated_by
            )
            db.add(history_record)
        
        # Instead of creating a new record, update the existing one
        # First query for the original asset (which was marked is_current=False)
        original_asset = db.query(DBAsset).filter(DBAsset.asset_id == asset_id).first()
        
        # Update its fields
        original_asset.version = new_version
        original_asset.is_current = True
        original_asset.name = asset.name if asset.name is not None else existing.name
        original_asset.description = asset.description if asset.description is not None else existing.description
        original_asset.asset_type = asset.asset_type if asset.asset_type is not None else existing.asset_type
        original_asset.data_types = asset.data_types if asset.data_types is not None else existing.data_types
        original_asset.storage_location = asset.storage_location if asset.storage_location is not None else existing.storage_location
        original_asset.scope_id = asset.scope_id if asset.scope_id is not None else existing.scope_id
        original_asset.scope_version = scope_version
        original_asset.confidentiality = asset.confidentiality if asset.confidentiality is not None else existing.confidentiality
        original_asset.integrity = asset.integrity if asset.integrity is not None else existing.integrity
        original_asset.availability = asset.availability if asset.availability is not None else existing.availability
        original_asset.authenticity_required = asset.authenticity_required if asset.authenticity_required is not None else existing.authenticity_required
        original_asset.authorization_required = asset.authorization_required if asset.authorization_required is not None else existing.authorization_required
        original_asset.updated_at = datetime.now()
        original_asset.updated_by = user
        original_asset.revision_notes = "Updated asset"
        
        # No need to db.add as the object is already attached to the session
        
        performer = get_user_from_request(request)
        audit_update(db, "asset", asset_id, performer, scope_id=original_asset.scope_id, summary="Asset updated")
        db.commit()
        db.refresh(original_asset)
        
        return original_asset
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating asset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating asset: {str(e)}"
        )


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: str, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Delete an asset (logical delete via is_current flag)
    """
    try:
        # Get current asset
        asset = db.query(DBAsset).filter(
            DBAsset.asset_id == asset_id,
            DBAsset.is_current == True
        ).first()
        
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with ID {asset_id} not found"
            )
        
        # Mark as deleted (set is_current to False)
        asset.is_current = False
        asset.revision_notes = "Deleted asset"
        db.add(asset)
        
        performer = get_user_from_request(request)
        audit_delete(db, "asset", asset_id, performer, scope_id=asset.scope_id)
        db.commit()
        
        return None
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting asset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting asset: {str(e)}"
        )


@router.get("/{asset_id}/history", response_model=List[AssetHistory])
async def get_asset_history(
    asset_id: str, 
    db: Session = Depends(get_db)
):
    """
    Get the version history of an asset
    """
    history = db.query(DBAssetHistory).filter(
        DBAssetHistory.asset_id == asset_id
    ).order_by(DBAssetHistory.version.desc()).all()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No history found for asset with ID {asset_id}"
        )
    
    return history


@router.get("/product/{scope_id}", response_model=AssetList)
async def get_assets_by_product(
    scope_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all assets for a specific product
    """
    # Verify product exists
    product = db.query(DBProductScope).filter(
        DBProductScope.scope_id == scope_id,
        DBProductScope.is_current == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {scope_id} not found"
        )
    
    # Get assets for the product
    assets = db.query(DBAsset).filter(
        DBAsset.scope_id == scope_id,
        DBAsset.is_current == True
    ).offset(skip).limit(limit).all()
    
    total = db.query(DBAsset).filter(
        DBAsset.scope_id == scope_id,
        DBAsset.is_current == True
    ).count()
    
    return {"assets": assets, "total": total}
