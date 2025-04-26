"""
Report models for FastAPI
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ReportFormat(str, Enum):
    """Report export formats"""
    TXT = "txt"
    JSON = "json"
    XLSX = "xlsx"
    PDF = "pdf"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportType(str, Enum):
    """Report types"""
    PRELIMINARY = "preliminary"  # Initial automated analysis
    FINAL = "final"  # After human review


class ReportConfiguration(BaseModel):
    """Configuration options for report generation"""
    include_components: bool = Field(True, description="Include component details")
    include_threats: bool = Field(True, description="Include threat analysis")
    include_stride: bool = Field(True, description="Include STRIDE analysis")
    include_compliance: bool = Field(True, description="Include compliance mappings")
    include_attacker_feasibility: bool = Field(True, description="Include attacker feasibility assessments")
    include_risk_acceptance: bool = Field(True, description="Include risk acceptance decisions")
    include_attack_paths: bool = Field(True, description="Include attack path analysis")
    include_review_decisions: bool = Field(True, description="Include review decisions")
    
    # Format-specific options
    excel_separate_sheets: bool = Field(True, description="Use separate sheets for each section in Excel")
    pdf_include_charts: bool = Field(True, description="Include charts in PDF output")
    max_threats_per_component: int = Field(0, description="Maximum threats to show per component (0 for all)")


class ReportCreate(BaseModel):
    """Request model for creating a new report"""
    analysis_id: str = Field(..., description="Analysis ID to create report from")
    format: ReportFormat = Field(ReportFormat.JSON, description="Report format")
    name: Optional[str] = Field(None, description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    report_type: ReportType = Field(ReportType.PRELIMINARY, description="Report type")
    configuration: Optional[ReportConfiguration] = Field(None, description="Report configuration options")


class Report(BaseModel):
    """Complete report model"""
    id: str = Field(..., description="Report ID")
    analysis_id: str = Field(..., description="Analysis ID")
    name: Optional[str] = Field(None, description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    format: ReportFormat = Field(..., description="Report format")
    report_type: ReportType = Field(..., description="Report type")
    status: ReportStatus = Field(..., description="Report generation status")
    file_path: Optional[str] = Field(None, description="Path to generated report file")
    file_size: Optional[int] = Field(None, description="Size of generated report file in bytes")
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    configuration: ReportConfiguration = Field(..., description="Report configuration options")
    
    class Config:
        from_attributes = True


class ReportSummary(BaseModel):
    """Summary of a report for listings"""
    id: str = Field(..., description="Report ID")
    analysis_id: str = Field(..., description="Analysis ID")
    name: Optional[str] = Field(None, description="Report name")
    format: ReportFormat = Field(..., description="Report format")
    report_type: ReportType = Field(..., description="Report type")
    status: ReportStatus = Field(..., description="Report generation status")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class ReportList(BaseModel):
    """List of reports with pagination"""
    reports: List[ReportSummary] = Field(..., description="List of report summaries")
    total: int = Field(..., description="Total number of reports")


class ReportError(BaseModel):
    """Error information for failed reports"""
    report_id: str = Field(..., description="Report ID")
    error_message: str = Field(..., description="Error message")
    error_details: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(..., description="Error timestamp")
