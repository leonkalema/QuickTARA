"""
Enhanced error handling utilities for QuickTARA API
"""
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationAPIError(APIError):
    """Validation error with field-level details"""
    def __init__(self, message: str, field_errors: Dict[str, str]):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, {"field_errors": field_errors})

class NotFoundAPIError(APIError):
    """Resource not found error"""
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with ID '{identifier}' not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class ConflictAPIError(APIError):
    """Resource conflict error"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_409_CONFLICT)

class DatabaseAPIError(APIError):
    """Database operation error"""
    def __init__(self, operation: str, details: str = ""):
        message = f"Database error during {operation}"
        if details:
            message += f": {details}"
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)

def handle_database_error(e: Exception, operation: str) -> HTTPException:
    """Convert database errors to appropriate HTTP exceptions"""
    if isinstance(e, IntegrityError):
        # Handle constraint violations
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        
        if "UNIQUE constraint failed" in error_msg or "Duplicate entry" in error_msg:
            return HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f"Resource already exists",
                    "error_type": "duplicate_resource",
                    "operation": operation
                }
            )
        elif "FOREIGN KEY constraint failed" in error_msg or "foreign key constraint" in error_msg.lower():
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Referenced resource does not exist",
                    "error_type": "invalid_reference",
                    "operation": operation
                }
            )
        else:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Data integrity violation",
                    "error_type": "integrity_error",
                    "operation": operation
                }
            )
    
    elif isinstance(e, SQLAlchemyError):
        logger.error(f"Database error during {operation}: {str(e)}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Database operation failed",
                "error_type": "database_error",
                "operation": operation
            }
        )
    
    else:
        logger.error(f"Unexpected error during {operation}: {str(e)}")
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An unexpected error occurred",
                "error_type": "internal_error",
                "operation": operation
            }
        )

def handle_validation_error(e: ValidationError) -> HTTPException:
    """Convert Pydantic validation errors to HTTP exceptions"""
    field_errors = {}
    
    for error in e.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        field_errors[field_path] = error["msg"]
    
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "message": "Validation failed",
            "error_type": "validation_error",
            "field_errors": field_errors
        }
    )

def create_success_response(message: str, data: Any = None, status_code: int = 200) -> Dict[str, Any]:
    """Create standardized success response"""
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    return response

def create_error_response(message: str, error_type: str = "error", details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        "success": False,
        "message": message,
        "error_type": error_type
    }
    
    if details:
        response.update(details)
    
    return response
