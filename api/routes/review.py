"""
Risk review API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from api.deps.db import get_db
from api.models.review import (
    ReviewStatus, 
    ReviewSubmission, 
    BatchReviewSubmission,
    ReviewStatusResponse,
    RisksForReviewResponse
)
from api.services.review_service import ReviewService

router = APIRouter()


@router.get("/{analysis_id}", response_model=RisksForReviewResponse)
async def get_risk_decisions(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get risk decisions for review
    
    This endpoint returns all risks that require review for an analysis, along with their current review status.
    """
    try:
        return ReviewService.get_risks_for_review(db, analysis_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving risks: {str(e)}")


@router.post("/{analysis_id}/submit", status_code=status.HTTP_201_CREATED)
async def submit_risk_review(
    analysis_id: str,
    submission: ReviewSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit a review decision for a risk
    
    This endpoint allows submitting a review decision for a single risk.
    """
    try:
        review_decision = ReviewService.submit_review(db, analysis_id, submission)
        return {
            "analysis_id": analysis_id,
            "component_id": submission.component_id,
            "threat_id": submission.threat_id,
            "status": "success",
            "message": "Review decision submitted successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting review: {str(e)}")


@router.post("/{analysis_id}/batch", status_code=status.HTTP_201_CREATED)
async def submit_batch_reviews(
    analysis_id: str,
    submissions: BatchReviewSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit multiple review decisions at once
    
    This endpoint allows submitting multiple review decisions in a single request.
    """
    try:
        successful, failed = ReviewService.submit_batch_review(db, analysis_id, submissions.decisions)
        return {
            "analysis_id": analysis_id,
            "successful": successful,
            "failed": failed,
            "total": len(submissions.decisions),
            "status": "success",
            "message": f"Processed {successful} reviews successfully, {failed} failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting batch reviews: {str(e)}")


@router.get("/{analysis_id}/status", response_model=ReviewStatusResponse)
async def get_review_status(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of a risk review
    
    This endpoint returns the current status of the review process for an analysis,
    including total risks, reviewed risks, and pending risks.
    """
    try:
        return ReviewService.get_review_status(db, analysis_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving review status: {str(e)}")


@router.post("/{analysis_id}/apply")
async def apply_reviews(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Apply review decisions to an analysis
    
    This endpoint applies all review decisions to the analysis and returns the updated analysis.
    """
    try:
        updated_analysis = ReviewService.apply_reviews_to_analysis(db, analysis_id)
        return {
            "analysis_id": analysis_id,
            "status": "success",
            "message": "Review decisions applied successfully",
            "analysis": updated_analysis
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying reviews: {str(e)}")
