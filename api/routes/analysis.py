"""
Analysis API routes
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import logging

from api.deps.db import get_db
from api.models.analysis import Analysis, AnalysisCreate, AnalysisList
from api.services.analysis_service import run_analysis, list_analyses, count_analyses, get_analysis, get_stride_analysis, get_attack_paths

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=Analysis, status_code=status.HTTP_201_CREATED)
async def run_analysis(
    analysis_create: AnalysisCreate,
    db: Session = Depends(get_db)
):
    """
    Run analysis on selected components
    """
    try:
        logger.info(f"Starting analysis for components: {analysis_create.component_ids}")
        analysis = run_analysis(db, analysis_create)
        return analysis
    except ValueError as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during analysis: {str(e)}"
        )


@router.get("", response_model=AnalysisList)
async def list_analyses(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    List all analyses with pagination
    """
    analyses = list_analyses(db, skip=skip, limit=limit)
    total = count_analyses(db)
    return AnalysisList(analyses=analyses, total=total)


@router.get("/{analysis_id}", response_model=Analysis)
async def get_analysis_results(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analysis results by ID
    """
    analysis = get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    return analysis


@router.get("/{analysis_id}/stride")
async def get_stride_analysis(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get STRIDE analysis for all components in the analysis
    """
    # Check if analysis exists
    analysis = get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    
    # Get STRIDE analysis
    stride_results = get_stride_analysis(db, analysis_id)
    return stride_results


@router.get("/{analysis_id}/attack-paths")
async def get_attack_paths(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get attack path analysis for all components in the analysis
    """
    # Check if analysis exists
    analysis = get_analysis(db, analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    
    # Get attack paths
    attack_paths = get_attack_paths(db, analysis_id)
    return attack_paths


@router.post("/{analysis_id}/background", status_code=status.HTTP_202_ACCEPTED)
async def run_background_analysis(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Run a background analysis task (for long-running analyses)
    """
    # This is a placeholder for future implementation of background tasks
    # Will be useful for very large analyses that take a long time to complete
    return {"status": "Analysis started in background", "analysis_id": analysis_id}
