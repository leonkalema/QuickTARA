"""
System Scope service functions
"""
import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from db.base import SystemScope
from api.models.scope import SystemScopeCreate, SystemScopeUpdate


def get_scope(db: Session, scope_id: str) -> Optional[SystemScope]:
    """
    Get a system scope by ID
    
    Args:
        db: Database session
        scope_id: Scope identifier
        
    Returns:
        SystemScope object or None if not found
    """
    return db.query(SystemScope).filter(SystemScope.scope_id == scope_id).first()


def get_scopes(db: Session, skip: int = 0, limit: int = 100) -> List[SystemScope]:
    """
    Get all system scopes with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of SystemScope objects
    """
    return db.query(SystemScope).offset(skip).limit(limit).all()


def count_scopes(db: Session) -> int:
    """
    Count total number of system scopes
    
    Args:
        db: Database session
        
    Returns:
        Total number of scopes
    """
    return db.query(SystemScope).count()


def create_scope(db: Session, scope: SystemScopeCreate) -> SystemScope:
    """
    Create a new system scope
    
    Args:
        db: Database session
        scope: Scope data
        
    Returns:
        Created SystemScope object
    """
    # Generate a unique ID if not provided
    scope_id = scope.scope_id or f"scope_{uuid.uuid4().hex[:8]}"
    
    # Create the scope object
    db_scope = SystemScope(
        scope_id=scope_id,
        name=scope.name,
        system_type=scope.system_type,
        description=scope.description,
        boundaries=scope.boundaries,
        objectives=scope.objectives,
        stakeholders=scope.stakeholders
    )
    
    db.add(db_scope)
    db.commit()
    db.refresh(db_scope)
    return db_scope


def update_scope(db: Session, scope_id: str, scope: SystemScopeUpdate) -> Optional[SystemScope]:
    """
    Update an existing system scope
    
    Args:
        db: Database session
        scope_id: Scope identifier
        scope: Updated scope data
        
    Returns:
        Updated SystemScope object or None if not found
    """
    db_scope = get_scope(db, scope_id)
    if not db_scope:
        return None
    
    update_data = scope.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_scope, key, value)
    
    db.commit()
    db.refresh(db_scope)
    return db_scope


def delete_scope(db: Session, scope_id: str) -> bool:
    """
    Delete a system scope
    
    Args:
        db: Database session
        scope_id: Scope identifier
        
    Returns:
        True if scope was deleted, False if not found
    """
    # Use a try-except block to handle potential database errors
    try:
        # Skip the ORM and use a direct SQL query to avoid relationship checks
        from sqlalchemy import text
        
        # First check if the scope exists
        result = db.execute(text("SELECT 1 FROM system_scopes WHERE scope_id = :scope_id"), 
                          {"scope_id": scope_id})
        if not result.scalar():
            return False
        
        # Delete directly with SQL to bypass ORM relationship checks
        db.execute(text("DELETE FROM system_scopes WHERE scope_id = :scope_id"), 
                   {"scope_id": scope_id})
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        # Re-raise as a custom exception with more details
        raise Exception(f"Error deleting scope: {str(e)}")
