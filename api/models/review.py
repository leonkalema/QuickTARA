"""
Review decision models for FastAPI
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from api.models.analysis import RiskAcceptanceDecision


class ReviewStatus(str, Enum):
    """Risk review status values"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ReviewDecision(BaseModel):
    """Records a manual review decision for a risk treatment"""
    original_decision: RiskAcceptanceDecision = Field(
        ..., description="Original automated decision"
    )
    final_decision: RiskAcceptanceDecision = Field(
        ..., description="Final decision after review"
    )
    reviewer: str = Field(..., description="Name of the reviewer")
    justification: str = Field(..., description="Decision justification")
    additional_notes: str = Field("", description="Optional additional notes")
    review_date: str = Field(..., description="Date of review (YYYY-MM-DD)")
    evidence_references: List[str] = Field(
        default_factory=list, description="References to supporting evidence"
    )


class ComponentReviewDecisions(BaseModel):
    """Review decisions for a single component"""
    component_id: str = Field(..., description="Component ID")
    threat_decisions: Dict[str, ReviewDecision] = Field(
        default_factory=dict, description="Review decisions by threat name"
    )


class ReviewSubmission(BaseModel):
    """Model for submitting review decisions"""
    threat_id: str = Field(..., description="Threat identifier")
    component_id: str = Field(..., description="Component identifier")
    final_decision: RiskAcceptanceDecision = Field(
        ..., description="Final decision after review"
    )
    reviewer: str = Field(..., description="Name of the reviewer")
    justification: str = Field(..., description="Decision justification")
    additional_notes: Optional[str] = Field(None, description="Optional additional notes")
    review_date: str = Field(..., description="Date of review (YYYY-MM-DD)")
    evidence_references: List[str] = Field(
        default_factory=list, description="References to supporting evidence"
    )


class BatchReviewSubmission(BaseModel):
    """Model for submitting multiple review decisions at once"""
    decisions: List[ReviewSubmission] = Field(
        ..., description="List of review decisions"
    )


class ReviewStatusResponse(BaseModel):
    """Response model for review status"""
    analysis_id: str = Field(..., description="Analysis ID")
    status: ReviewStatus = Field(..., description="Overall review status")
    total_risks: int = Field(..., description="Total number of risks")
    reviewed_risks: int = Field(..., description="Number of reviewed risks")
    pending_risks: int = Field(..., description="Number of pending risks")


class RiskForReview(BaseModel):
    """Model for a risk requiring review"""
    component_id: str = Field(..., description="Component ID")
    component_name: str = Field(..., description="Component name")
    threat_id: str = Field(..., description="Threat identifier")
    threat_name: str = Field(..., description="Threat name")
    risk_severity: str = Field(..., description="Risk severity level")
    original_decision: RiskAcceptanceDecision = Field(
        ..., description="Original decision"
    )
    residual_risk: float = Field(
        ..., description="Residual risk percentage", ge=0.0, le=1.0
    )
    justification: str = Field(..., description="Original justification")
    safety_level: str = Field(..., description="Component safety level")
    review_status: ReviewStatus = Field(
        ..., description="Current review status"
    )


class RisksForReviewResponse(BaseModel):
    """Response model for risks requiring review"""
    analysis_id: str = Field(..., description="Analysis ID")
    risks: List[RiskForReview] = Field(..., description="List of risks for review")
    status: ReviewStatus = Field(..., description="Overall review status")
