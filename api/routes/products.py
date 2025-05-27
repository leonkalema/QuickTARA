"""
Product API routes for product-centric model
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from api.deps.db import get_db
from api.models.scope_updated import ProductScope, ProductScopeCreate, ProductScopeUpdate, ProductScopeList, ProductScopeHistory
from db.product_asset_models import ProductScope as DBProductScope, ProductScopeHistory as DBProductScopeHistory

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=ProductScopeList)
async def list_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    List all products with pagination
    """
    try:
        products = db.query(DBProductScope).filter(DBProductScope.is_current == True).offset(skip).limit(limit).all()
        total = db.query(DBProductScope).filter(DBProductScope.is_current == True).count()
        logger.info(f"Found {total} products")
        
        return {"scopes": products, "total": total}
    except Exception as e:
        logger.error(f"Error listing products: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing products: {str(e)}"
        )


@router.post("", response_model=ProductScope, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductScopeCreate,
    db: Session = Depends(get_db),
    user: str = None
):
    """
    Create a new product
    """
    try:
        # Generate scope_id if not provided
        if not product.scope_id:
            import uuid
            product.scope_id = f"product_{uuid.uuid4().hex[:8]}"
        
        # Check if product with ID already exists
        existing = db.query(DBProductScope).filter(DBProductScope.scope_id == product.scope_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with ID {product.scope_id} already exists"
            )
        
        # Create new product
        new_product = DBProductScope(
            scope_id=product.scope_id,
            name=product.name,
            product_type=product.product_type,
            description=product.description,
            safety_level=product.safety_level,
            interfaces=product.interfaces,
            access_points=product.access_points,
            location=product.location,
            trust_zone=product.trust_zone,
            boundaries=product.boundaries,
            objectives=product.objectives,
            stakeholders=product.stakeholders,
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=user,
            updated_by=user
        )
        db.add(new_product)
        
        # Create initial history record
        product_history = DBProductScopeHistory(
            scope_id=product.scope_id,
            version=1,
            name=product.name,
            product_type=product.product_type,
            description=product.description,
            safety_level=product.safety_level,
            interfaces=product.interfaces,
            access_points=product.access_points,
            location=product.location,
            trust_zone=product.trust_zone,
            boundaries=product.boundaries,
            objectives=product.objectives,
            stakeholders=product.stakeholders,
            is_current=True,
            revision_notes="Initial creation",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=user,
            updated_by=user
        )
        db.add(product_history)
        
        db.commit()
        db.refresh(new_product)
        
        return new_product
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating product: {str(e)}"
        )


@router.get("/{scope_id}", response_model=ProductScope)
async def get_product(
    scope_id: str, 
    db: Session = Depends(get_db)
):
    """
    Get a product by ID
    """
    product = db.query(DBProductScope).filter(
        DBProductScope.scope_id == scope_id,
        DBProductScope.is_current == True
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {scope_id} not found"
        )
    return product


@router.put("/{scope_id}", response_model=ProductScope)
async def update_product(
    scope_id: str, 
    product: ProductScopeUpdate,
    db: Session = Depends(get_db),
    user: str = None
):
    """
    Update a product
    """
    try:
        # Get current product
        existing = db.query(DBProductScope).filter(
            DBProductScope.scope_id == scope_id,
            DBProductScope.is_current == True
        ).first()
        
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {scope_id} not found"
            )
        
        # Create new version
        new_version = existing.version + 1
        
        # Check if history record already exists for this version before creating one
        existing_history = db.query(DBProductScopeHistory).filter(
            DBProductScopeHistory.scope_id == scope_id,
            DBProductScopeHistory.version == existing.version
        ).first()
        
        if not existing_history:
            # Only create history record if one doesn't already exist
            history_record = DBProductScopeHistory(
                scope_id=scope_id,
                version=existing.version,
                name=existing.name,
                product_type=existing.product_type,
                description=existing.description,
                safety_level=existing.safety_level,
                interfaces=existing.interfaces,
                access_points=existing.access_points,
                location=existing.location,
                trust_zone=existing.trust_zone,
                boundaries=existing.boundaries,
                objectives=existing.objectives,
                stakeholders=existing.stakeholders,
                is_current=False,
                revision_notes="Archived version",
                created_at=existing.created_at,
                updated_at=existing.updated_at,
                created_by=existing.created_by,
                updated_by=existing.updated_by
            )
            db.add(history_record)
        
        # Update the existing record in-place instead of creating a new one
        # This avoids UNIQUE constraint errors with the scope_id
        existing.version = new_version
        existing.name = product.name if product.name is not None else existing.name
        existing.product_type = product.product_type if product.product_type is not None else existing.product_type
        existing.description = product.description if product.description is not None else existing.description
        existing.safety_level = product.safety_level if product.safety_level is not None else existing.safety_level
        existing.interfaces = product.interfaces if product.interfaces is not None else existing.interfaces
        existing.access_points = product.access_points if product.access_points is not None else existing.access_points
        existing.location = product.location if product.location is not None else existing.location
        existing.trust_zone = product.trust_zone if product.trust_zone is not None else existing.trust_zone
        existing.boundaries = product.boundaries if product.boundaries is not None else existing.boundaries
        existing.objectives = product.objectives if product.objectives is not None else existing.objectives
        existing.stakeholders = product.stakeholders if product.stakeholders is not None else existing.stakeholders
        existing.updated_at = datetime.now()
        existing.updated_by = user
        existing.revision_notes = "Updated product"
        existing.is_current = True  # Ensure this is still marked as current
        
        db.commit()
        
        return existing
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating product: {str(e)}"
        )


@router.delete("/{scope_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    scope_id: str, 
    db: Session = Depends(get_db)
):
    """
    Delete a product (logical delete via is_current flag)
    """
    try:
        # Get current product
        product = db.query(DBProductScope).filter(
            DBProductScope.scope_id == scope_id,
            DBProductScope.is_current == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {scope_id} not found"
            )
        
        # Check if there are associated assets
        # Import Asset model from the correct location
        from db.product_asset_models import Asset
        
        assets_count = db.query(Asset).filter(
            Asset.scope_id == scope_id,
            Asset.is_current == True
        ).count()
        
        if assets_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete product with {assets_count} associated assets. Delete assets first."
            )
        
        # Mark as deleted (set is_current to False)
        product.is_current = False
        product.revision_notes = "Deleted product"
        db.add(product)
        
        db.commit()
        
        return None
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting product: {str(e)}"
        )


@router.get("/{scope_id}/history", response_model=List[ProductScopeHistory])
async def get_product_history(
    scope_id: str, 
    db: Session = Depends(get_db)
):
    """
    Get the version history of a product
    """
    history = db.query(DBProductScopeHistory).filter(
        DBProductScopeHistory.scope_id == scope_id
    ).order_by(DBProductScopeHistory.version.desc()).all()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No history found for product with ID {scope_id}"
        )
    
    return history
