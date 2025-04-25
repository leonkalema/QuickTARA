"""
System Scope models for FastAPI
"""
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SystemType(str, Enum):
    """System types for scope definition"""
    SUBSYSTEM = "subsystem"
    API = "api"
    BACKEND = "backend"
    FULLSYSTEM = "fullsystem"
    EMBEDDED = "embedded"
    OTHER = "other"


class SystemScopeBase(BaseModel):
    """Base System Scope attributes"""
    name: str = Field(..., description="Name of the system being analyzed")
    system_type: SystemType = Field(..., description="Type of system being analyzed")
    description: Optional[str] = Field(None, description="Detailed description of the system scope")
    boundaries: Optional[List[str]] = Field(default_factory=list, description="System boundaries")
    objectives: Optional[List[str]] = Field(default_factory=list, description="Analysis objectives")
    stakeholders: Optional[List[str]] = Field(default_factory=list, description="Stakeholders involved")


class SystemScopeCreate(SystemScopeBase):
    """Used for creating a new system scope"""
    scope_id: Optional[str] = Field(None, description="Optional unique scope identifier")


class SystemScopeUpdate(BaseModel):
    """Used for updating an existing system scope"""
    name: Optional[str] = None
    system_type: Optional[SystemType] = None
    description: Optional[str] = None
    boundaries: Optional[List[str]] = None
    objectives: Optional[List[str]] = None
    stakeholders: Optional[List[str]] = None


class SystemScope(SystemScopeBase):
    """Full system scope model with ID and timestamps"""
    scope_id: str = Field(..., description="Unique scope identifier")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class SystemScopeList(BaseModel):
    """List of system scopes"""
    scopes: List[SystemScope]
    total: int
