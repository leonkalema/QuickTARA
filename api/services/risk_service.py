"""
Risk Calculation Framework service
"""
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from db.base import RiskFramework
from api.models.risk import (
    RiskFrameworkConfiguration,
    RiskFrameworkCreate,
    RiskFrameworkUpdate
)

logger = logging.getLogger(__name__)


def generate_framework_id() -> str:
    """Generate a unique framework ID"""
    return f"framework_{uuid.uuid4().hex[:8]}"


def create_risk_framework(db: Session, risk_framework: RiskFrameworkCreate) -> RiskFrameworkConfiguration:
    """
    Create a new risk calculation framework
    """
    try:
        # Generate framework ID and timestamps
        now = datetime.now()
        framework_id = generate_framework_id()
        
        # Create new RiskFramework instance
        db_framework = RiskFramework(
            framework_id=framework_id,
            name=risk_framework.name,
            description=risk_framework.description,
            version=risk_framework.version,
            impact_definitions=risk_framework.dict()['impact_definitions'],
            likelihood_definitions=risk_framework.dict()['likelihood_definitions'],
            risk_matrix=risk_framework.dict()['risk_matrix'],
            risk_thresholds=risk_framework.dict()['risk_thresholds'],
            created_at=now,
            updated_at=now,
            is_active=True
        )
        
        # Add to database and commit
        db.add(db_framework)
        db.commit()
        db.refresh(db_framework)
        
        # Convert to Pydantic model and return
        return RiskFrameworkConfiguration(
            framework_id=db_framework.framework_id,
            name=db_framework.name,
            description=db_framework.description,
            version=db_framework.version,
            impact_definitions=db_framework.impact_definitions,
            likelihood_definitions=db_framework.likelihood_definitions,
            risk_matrix=db_framework.risk_matrix,
            risk_thresholds=db_framework.risk_thresholds,
            created_at=db_framework.created_at,
            updated_at=db_framework.updated_at,
            is_active=db_framework.is_active
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating risk framework: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error creating risk framework: {str(e)}")
        raise


def get_risk_framework(db: Session, framework_id: str) -> Optional[RiskFrameworkConfiguration]:
    """
    Get a risk framework by ID
    """
    try:
        db_framework = db.query(RiskFramework).filter(RiskFramework.framework_id == framework_id).first()
        if not db_framework:
            return None
        
        return RiskFrameworkConfiguration(
            framework_id=db_framework.framework_id,
            name=db_framework.name,
            description=db_framework.description,
            version=db_framework.version,
            impact_definitions=db_framework.impact_definitions,
            likelihood_definitions=db_framework.likelihood_definitions,
            risk_matrix=db_framework.risk_matrix,
            risk_thresholds=db_framework.risk_thresholds,
            created_at=db_framework.created_at,
            updated_at=db_framework.updated_at,
            is_active=db_framework.is_active
        )
    except Exception as e:
        logger.error(f"Error retrieving risk framework: {str(e)}")
        raise


def get_active_risk_framework(db: Session) -> Optional[RiskFrameworkConfiguration]:
    """
    Get the currently active risk framework
    """
    try:
        db_framework = db.query(RiskFramework).filter(RiskFramework.is_active == True).first()
        if not db_framework:
            return None
        
        return RiskFrameworkConfiguration(
            framework_id=db_framework.framework_id,
            name=db_framework.name,
            description=db_framework.description,
            version=db_framework.version,
            impact_definitions=db_framework.impact_definitions,
            likelihood_definitions=db_framework.likelihood_definitions,
            risk_matrix=db_framework.risk_matrix,
            risk_thresholds=db_framework.risk_thresholds,
            created_at=db_framework.created_at,
            updated_at=db_framework.updated_at,
            is_active=db_framework.is_active
        )
    except Exception as e:
        logger.error(f"Error retrieving active risk framework: {str(e)}")
        raise


def list_risk_frameworks(db: Session, skip: int = 0, limit: int = 100) -> List[RiskFrameworkConfiguration]:
    """
    List all risk frameworks with pagination
    """
    try:
        db_frameworks = db.query(RiskFramework).offset(skip).limit(limit).all()
        return [
            RiskFrameworkConfiguration(
                framework_id=fw.framework_id,
                name=fw.name,
                description=fw.description,
                version=fw.version,
                impact_definitions=fw.impact_definitions,
                likelihood_definitions=fw.likelihood_definitions,
                risk_matrix=fw.risk_matrix,
                risk_thresholds=fw.risk_thresholds,
                created_at=fw.created_at,
                updated_at=fw.updated_at,
                is_active=fw.is_active
            )
            for fw in db_frameworks
        ]
    except Exception as e:
        logger.error(f"Error listing risk frameworks: {str(e)}")
        raise


def count_risk_frameworks(db: Session) -> int:
    """
    Count all risk frameworks
    """
    try:
        return db.query(RiskFramework).count()
    except Exception as e:
        logger.error(f"Error counting risk frameworks: {str(e)}")
        raise


def update_risk_framework(
    db: Session, 
    framework_id: str, 
    framework_update: RiskFrameworkUpdate
) -> Optional[RiskFrameworkConfiguration]:
    """
    Update an existing risk framework
    """
    try:
        db_framework = db.query(RiskFramework).filter(RiskFramework.framework_id == framework_id).first()
        if not db_framework:
            return None
        
        # Update framework fields if provided
        update_data = framework_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'impact_definitions' and value is not None:
                # Handle impact definitions which is a dictionary of lists
                if hasattr(value, 'dict'):
                    setattr(db_framework, key, value.dict())
                else:
                    # Already a dictionary
                    setattr(db_framework, key, value)
            elif key == 'likelihood_definitions' and value is not None:
                # Handle likelihood definitions which is a list of objects
                if all(hasattr(item, 'dict') for item in value):
                    setattr(db_framework, key, [ld.dict() for ld in value])
                else:
                    # Already a list of dictionaries
                    setattr(db_framework, key, value)
            elif key == 'risk_matrix' and value is not None:
                # Handle risk matrix which is an object
                if hasattr(value, 'dict'):
                    setattr(db_framework, key, value.dict())
                else:
                    # Already a dictionary
                    setattr(db_framework, key, value)
            elif key == 'risk_thresholds' and value is not None:
                # Handle risk thresholds which is a list of objects
                if all(hasattr(item, 'dict') for item in value):
                    setattr(db_framework, key, [rt.dict() for rt in value])
                else:
                    # Already a list of dictionaries
                    setattr(db_framework, key, value)
            elif value is not None:
                setattr(db_framework, key, value)
        
        # Update timestamp
        db_framework.updated_at = datetime.now()
        
        # If this framework is set as active, deactivate all others
        if update_data.get('is_active', False):
            other_frameworks = db.query(RiskFramework).filter(
                RiskFramework.framework_id != framework_id,
                RiskFramework.is_active == True
            ).all()
            for fw in other_frameworks:
                fw.is_active = False
        
        # Commit changes
        db.commit()
        db.refresh(db_framework)
        
        return RiskFrameworkConfiguration(
            framework_id=db_framework.framework_id,
            name=db_framework.name,
            description=db_framework.description,
            version=db_framework.version,
            impact_definitions=db_framework.impact_definitions,
            likelihood_definitions=db_framework.likelihood_definitions,
            risk_matrix=db_framework.risk_matrix,
            risk_thresholds=db_framework.risk_thresholds,
            created_at=db_framework.created_at,
            updated_at=db_framework.updated_at,
            is_active=db_framework.is_active
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating risk framework: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error updating risk framework: {str(e)}")
        raise


def set_framework_active(db: Session, framework_id: str, active: bool = True) -> Optional[RiskFrameworkConfiguration]:
    """
    Set a risk framework as active/inactive
    """
    try:
        db_framework = db.query(RiskFramework).filter(RiskFramework.framework_id == framework_id).first()
        if not db_framework:
            return None
        
        # If setting to active, deactivate all others
        if active:
            other_frameworks = db.query(RiskFramework).filter(
                RiskFramework.framework_id != framework_id,
                RiskFramework.is_active == True
            ).all()
            for fw in other_frameworks:
                fw.is_active = False
        
        # Update active status
        db_framework.is_active = active
        db_framework.updated_at = datetime.now()
        
        # Commit changes
        db.commit()
        db.refresh(db_framework)
        
        return RiskFrameworkConfiguration(
            framework_id=db_framework.framework_id,
            name=db_framework.name,
            description=db_framework.description,
            version=db_framework.version,
            impact_definitions=db_framework.impact_definitions,
            likelihood_definitions=db_framework.likelihood_definitions,
            risk_matrix=db_framework.risk_matrix,
            risk_thresholds=db_framework.risk_thresholds,
            created_at=db_framework.created_at,
            updated_at=db_framework.updated_at,
            is_active=db_framework.is_active
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error setting framework active status: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error setting framework active status: {str(e)}")
        raise


def delete_risk_framework(db: Session, framework_id: str) -> bool:
    """
    Delete a risk framework
    """
    try:
        db_framework = db.query(RiskFramework).filter(RiskFramework.framework_id == framework_id).first()
        if not db_framework:
            return False
        
        db.delete(db_framework)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting risk framework: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error deleting risk framework: {str(e)}")
        raise


def calculate_risk_level(risk_framework: Any, likelihood: int, severity: int) -> str:
    """
    Calculate the risk level (High/Medium/Low) based on likelihood and severity
    using the provided risk framework configuration
    
    Args:
        risk_framework: Risk framework configuration object or dictionary
        likelihood: Likelihood score (1-5)
        severity: Severity score (1-5)
        
    Returns:
        Risk level string (High, Medium, or Low)
    """
    try:
        # Calculate risk score (likelihood x severity)
        risk_score = likelihood * severity
        
        # Handle different types of risk_framework input
        if hasattr(risk_framework, 'risk_thresholds'):
            thresholds = risk_framework.risk_thresholds
        elif isinstance(risk_framework, dict) and 'risk_thresholds' in risk_framework:
            thresholds = risk_framework['risk_thresholds']
        else:
            # Default thresholds if framework is not provided or invalid
            thresholds = [
                {"level": "Low", "max_score": 8},
                {"level": "Medium", "max_score": 16},
                {"level": "High", "max_score": 25}
            ]
        
        # Sort thresholds by max_score in ascending order
        sorted_thresholds = sorted(thresholds, key=lambda x: x.get('max_score', 0) if isinstance(x, dict) else 0)
        
        # Find the appropriate risk level based on risk score
        for threshold in sorted_thresholds:
            max_score = threshold.get('max_score', 0) if isinstance(threshold, dict) else 0
            level = threshold.get('level', 'Unknown') if isinstance(threshold, dict) else 'Unknown'
            
            if risk_score <= max_score:
                return level
        
        # If no matching threshold is found, return the highest level
        if sorted_thresholds:
            return sorted_thresholds[-1].get('level', 'High') if isinstance(sorted_thresholds[-1], dict) else 'High'
        else:
            return 'High'  # Default to high if no thresholds defined
            
    except Exception as e:
        logger.error(f"Error calculating risk level: {str(e)}")
        return 'Unknown'
