"""
Reports API routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import logging

from api.deps.db import get_db
from api.models.report import (
    Report, ReportCreate, ReportList, ReportFormat, ReportType
)
from api.services.report_service import ReportService
from config.settings import load_settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Load configuration for reports directory
config = load_settings()
reports_dir = config.get("storage", {}).get("reports_dir", "./reports")

def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    """
    Get ReportService instance with DB session dependency injection
    """
    return ReportService(db, reports_dir)


@router.post("", response_model=Report, status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    service: ReportService = Depends(get_report_service),
    db: Session = Depends(get_db)
):
    """
    Generate a report from analysis results
    
    The report generation will run in the background and the status
    can be checked using the GET endpoint.
    """
    try:
        # Create the report record
        report = service.create_report(report_data)
        
        # Start report generation in background
        background_tasks.add_task(service.generate_report, report.id)
        
        return report
    except ValueError as e:
        logger.error(f"Error creating report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the report: {str(e)}"
        )


@router.get("", response_model=ReportList)
async def list_reports(
    skip: int = 0,
    limit: int = 100,
    analysis_id: Optional[str] = None,
    service: ReportService = Depends(get_report_service),
    db: Session = Depends(get_db)
):
    """
    List all generated reports with optional filtering
    """
    return service.list_reports(skip=skip, limit=limit, analysis_id=analysis_id)


@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
    db: Session = Depends(get_db)
):
    """
    Get report details by ID
    """
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
    db: Session = Depends(get_db)
):
    """
    Download a generated report
    """
    # Get report details
    report = service.get_report(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    # Check if report is ready
    if report.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report is not ready for download (status: {report.status})"
        )
    
    # Check if file exists
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    # Set appropriate filename for download
    filename = os.path.basename(report.file_path)
    return FileResponse(
        path=report.file_path,
        filename=filename,
        media_type=_get_media_type(report.format)
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
    db: Session = Depends(get_db)
):
    """
    Delete a generated report
    """
    result = service.delete_report(report_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    return None


def _get_media_type(format: ReportFormat) -> str:
    """
    Get the appropriate MIME type for a report format
    """
    if format == ReportFormat.JSON:
        return "application/json"
    elif format == ReportFormat.XLSX:
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == ReportFormat.PDF:
        return "application/pdf"
    elif format == ReportFormat.TXT:
        return "text/plain"
    else:
        return "application/octet-stream"
