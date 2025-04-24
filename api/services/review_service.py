"""
Review Service for QuickTARA API

This service handles the risk review workflow, including:
- Retrieving risks that require review
- Submitting review decisions
- Tracking review status
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_
from sqlalchemy.orm import Session

# Import SQLAlchemy models
from db.base import ReviewDecision as DbReviewDecision

from api.models.review import (
    ReviewDecision, 
    ReviewStatus, 
    RiskForReview, 
    ReviewSubmission,
    ReviewStatusResponse,
    RisksForReviewResponse
)
from api.models.analysis import RiskAcceptanceDecision

from core.risk_review import apply_review_decisions, ReviewStatus as CoreReviewStatus, ReviewDecision as CoreReviewDecision


class ReviewService:
    """Service for managing the risk review workflow"""

    @staticmethod
    def load_review_decisions(db: Session, analysis_id: str) -> Dict:
        """Load existing review decisions for an analysis from the database"""
        # Query review decisions from database
        db_review_decisions = db.query(DbReviewDecision).filter(
            DbReviewDecision.analysis_id == analysis_id
        ).all()
        
        # Convert to dictionary format for compatibility
        result = {}
        for decision in db_review_decisions:
            if decision.component_id not in result:
                result[decision.component_id] = {}
            
            result[decision.component_id][decision.threat_id] = {
                'original_decision': decision.original_decision,
                'final_decision': decision.final_decision,
                'reviewer': decision.reviewer,
                'justification': decision.justification,
                'additional_notes': decision.additional_notes or '',
                'review_date': decision.review_date,
                'evidence_references': decision.evidence_references or [],
                'status': decision.status
            }
        
        return result

    @staticmethod
    def save_review_decision(db: Session, analysis_id: str, component_id: str, 
                            threat_id: str, decision_data: Dict) -> bool:
        """Save a review decision to the database"""
        try:
            # Check if review decision already exists
            existing = db.query(DbReviewDecision).filter(
                and_(
                    DbReviewDecision.analysis_id == analysis_id,
                    DbReviewDecision.component_id == component_id,
                    DbReviewDecision.threat_id == threat_id
                )
            ).first()
            
            if existing:
                # Update existing decision
                existing.original_decision = decision_data.get('original_decision')
                existing.final_decision = decision_data.get('final_decision')
                existing.reviewer = decision_data.get('reviewer')
                existing.justification = decision_data.get('justification')
                existing.additional_notes = decision_data.get('additional_notes', '')
                existing.review_date = decision_data.get('review_date')
                existing.evidence_references = decision_data.get('evidence_references', [])
                existing.updated_at = datetime.now()
                existing.status = decision_data.get('status', 'completed')
            else:
                # Create new decision
                new_decision = DbReviewDecision(
                    id=str(uuid.uuid4()),
                    analysis_id=analysis_id,
                    component_id=component_id,
                    threat_id=threat_id,
                    original_decision=decision_data.get('original_decision'),
                    final_decision=decision_data.get('final_decision'),
                    reviewer=decision_data.get('reviewer'),
                    justification=decision_data.get('justification'),
                    additional_notes=decision_data.get('additional_notes', ''),
                    review_date=decision_data.get('review_date'),
                    evidence_references=decision_data.get('evidence_references', []),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    status=decision_data.get('status', 'completed')
                )
                db.add(new_decision)
            
            # Commit changes
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error saving review decision: {e}")
            return False

    @staticmethod
    def get_risks_for_review(db: Session, analysis_id: str) -> RisksForReviewResponse:
        """
        Get all risks for an analysis that require review
        """
        from api.services.analysis_service import get_analysis
        
        # Get the analysis
        analysis = get_analysis(db, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found")
        
        # Load existing review decisions
        review_decisions = ReviewService.load_review_decisions(db, analysis_id)
        
        # Track which risks have been reviewed
        reviewed_risks = set()
        for comp_id, threats in review_decisions.items():
            for threat_id in threats:
                reviewed_risks.add(f"{comp_id}:{threat_id}")
        
        # Prepare risks for review
        risks = []
        for comp_id, comp_data in analysis['components'].items():
            comp_name = comp_data.get('name', comp_id)
            safety_level = comp_data.get('safety_level', 'QM')
            
            # Get risk acceptance data
            risk_acceptance = comp_data.get('risk_acceptance', {})
            
            for threat_name, assessment in risk_acceptance.items():
                # Check review status
                review_status = (
                    ReviewStatus.COMPLETED 
                    if f"{comp_id}:{threat_name}" in reviewed_risks 
                    else ReviewStatus.PENDING
                )
                
                # Create risk for review
                risks.append(RiskForReview(
                    component_id=comp_id,
                    component_name=comp_name,
                    threat_id=threat_name,
                    threat_name=threat_name,
                    risk_severity=assessment.get('risk_severity', 'Medium'),
                    original_decision=RiskAcceptanceDecision(assessment.get('decision', 'Mitigate')),
                    residual_risk=assessment.get('residual_risk', 0.5),
                    justification=assessment.get('justification', ''),
                    safety_level=safety_level,
                    review_status=review_status
                ))
        
        # Determine overall status
        status = ReviewStatus.COMPLETED if risks and all(r.review_status == ReviewStatus.COMPLETED for r in risks) else (
            ReviewStatus.IN_PROGRESS if any(r.review_status == ReviewStatus.COMPLETED for r in risks) else ReviewStatus.PENDING
        )
        
        return RisksForReviewResponse(
            analysis_id=analysis_id,
            risks=risks,
            status=status
        )

    @staticmethod
    def get_review_status(db: Session, analysis_id: str) -> ReviewStatusResponse:
        """
        Get the status of the review process for an analysis
        """
        from api.services.analysis_service import get_analysis
        
        # Get the analysis
        analysis = get_analysis(db, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found")
        
        # Load existing review decisions
        review_decisions = ReviewService.load_review_decisions(db, analysis_id)
        
        # Count total risks and reviewed risks
        total_risks = 0
        reviewed_risks = 0
        
        # Track which risks have been reviewed
        reviewed_set = set()
        for comp_id, threats in review_decisions.items():
            for threat_id in threats:
                reviewed_set.add(f"{comp_id}:{threat_id}")
        
        # Count risks
        for comp_id, comp_data in analysis['components'].items():
            if isinstance(comp_data, dict):
                risk_acceptance = comp_data.get('risk_acceptance', {})
                total_risks += len(risk_acceptance)
                
                for threat_name in risk_acceptance:
                    if f"{comp_id}:{threat_name}" in reviewed_set:
                        reviewed_risks += 1
        
        # Determine status
        status = ReviewStatus.COMPLETED if total_risks > 0 and reviewed_risks == total_risks else (
            ReviewStatus.IN_PROGRESS if reviewed_risks > 0 else ReviewStatus.PENDING
        )
        
        return ReviewStatusResponse(
            analysis_id=analysis_id,
            status=status,
            total_risks=total_risks,
            reviewed_risks=reviewed_risks,
            pending_risks=total_risks - reviewed_risks
        )

    @staticmethod
    def submit_review(db: Session, analysis_id: str, submission: ReviewSubmission) -> Optional[ReviewDecision]:
        """
        Submit a review decision for a risk
        """
        from api.services.analysis_service import get_analysis
        
        # Get the analysis
        analysis = get_analysis(db, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found")
        
        # Verify component and threat exist
        component_id = submission.component_id
        threat_id = submission.threat_id
        
        if component_id not in analysis['components']:
            raise ValueError(f"Component {component_id} not found in analysis")
        
        component = analysis['components'][component_id]
        if 'risk_acceptance' not in component or threat_id not in component['risk_acceptance']:
            raise ValueError(f"Threat {threat_id} not found for component {component_id}")
        
        # Get original decision
        risk_acceptance = component['risk_acceptance'][threat_id]
        original_decision = RiskAcceptanceDecision(risk_acceptance.get('decision', 'Mitigate'))
        
        # Create review decision
        review_decision = ReviewDecision(
            original_decision=original_decision,
            final_decision=submission.final_decision,
            reviewer=submission.reviewer,
            justification=submission.justification,
            additional_notes=submission.additional_notes or "",
            review_date=submission.review_date,
            evidence_references=submission.evidence_references
        )
        
        # Create a dictionary from the review decision
        decision_data = review_decision.dict()
        decision_data['status'] = 'completed'
        
        # Save review decision to database
        if not ReviewService.save_review_decision(db, analysis_id, component_id, threat_id, decision_data):
            raise Exception("Failed to save review decision")
        
        return review_decision

    @staticmethod
    def submit_batch_review(db: Session, analysis_id: str, submissions: List[ReviewSubmission]) -> Tuple[int, int]:
        """
        Submit multiple review decisions at once
        """
        successful = 0
        failed = 0
        
        for submission in submissions:
            try:
                ReviewService.submit_review(db, analysis_id, submission)
                successful += 1
            except Exception:
                failed += 1
        
        return successful, failed

    @staticmethod
    def apply_reviews_to_analysis(db: Session, analysis_id: str) -> Dict:
        """
        Apply review decisions to an analysis and return the updated analysis
        """
        from api.services.analysis_service import get_analysis
        
        # Get the analysis
        analysis = get_analysis(db, analysis_id)
        if not analysis:
            raise ValueError(f"Analysis with ID {analysis_id} not found")
        
        # Convert analysis Pydantic model to dict for processing
        analysis_dict = analysis.dict()
        
        # Load review decisions
        review_decisions_data = ReviewService.load_review_decisions(db, analysis_id)
        
        if not review_decisions_data:
            return analysis_dict  # No reviews to apply
        
        # Convert the loaded data to the format expected by apply_review_decisions
        review_decisions = {}
        for comp_id, threats in review_decisions_data.items():
            review_decisions[comp_id] = {}
            for threat_id, decision_data in threats.items():
                # Convert dict to CoreReviewDecision object for the core module
                original_decision = decision_data['original_decision']
                final_decision = decision_data['final_decision']
                
                review_decisions[comp_id][threat_id] = CoreReviewDecision(
                    original_decision=original_decision,
                    final_decision=final_decision,
                    reviewer=decision_data['reviewer'],
                    review_date=decision_data['review_date'],
                    justification=decision_data['justification'],
                    evidence_references=decision_data.get('evidence_references', []),
                    additional_notes=decision_data.get('additional_notes', ''),
                    status=CoreReviewStatus.REVIEWED
                )
        
        # Apply the reviews to the analysis
        updated_analysis = apply_review_decisions(analysis_dict, review_decisions)
        
        return updated_analysis
