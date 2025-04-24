"""
Risk Review Module for QuickTARA
Implements the human review workflow for risk treatment decisions
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Optional, Any
from datetime import datetime

class ReviewStatus(Enum):
    NOT_REVIEWED = "Not Reviewed"
    IN_PROGRESS = "In Progress"
    REVIEWED = "Reviewed"
    APPROVED = "Approved"
    REJECTED = "Rejected"

@dataclass
class ReviewDecision:
    original_decision: str
    final_decision: str
    reviewer: str
    review_date: str
    justification: str
    evidence_references: List[str]
    additional_notes: str
    status: ReviewStatus
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary"""
        return {
            'original_decision': self.original_decision,
            'final_decision': self.final_decision,
            'reviewer': self.reviewer,
            'review_date': self.review_date,
            'justification': self.justification,
            'evidence_references': self.evidence_references,
            'additional_notes': self.additional_notes,
            'status': self.status.value
        }

def apply_review_decisions(report_data: Dict[str, Any], review_decisions: Dict[str, Dict[str, ReviewDecision]]) -> Dict[str, Any]:
    """Apply review decisions to the report data"""
    # Create a copy of the report data to avoid modifying the original
    updated_data = {
        'components': {},
        'generated_at': report_data.get('generated_at', datetime.now().isoformat()),
        'summary': report_data.get('summary', {})
    }
    
    # Copy components and apply review decisions
    for comp_id, comp_data in report_data.get('components', {}).items():
        # Skip non-dictionary components
        if not isinstance(comp_data, dict):
            continue
            
        # Create a copy of the component data
        updated_comp = comp_data.copy()
        
        # Check if there are review decisions for this component
        if comp_id in review_decisions:
            # Apply review decisions to risk acceptance assessments
            if 'risk_acceptance' in updated_comp:
                for threat_name, assessment in updated_comp['risk_acceptance'].items():
                    # Check if there's a review decision for this threat
                    if threat_name in review_decisions[comp_id]:
                        decision = review_decisions[comp_id][threat_name]
                        
                        # Create a copy of the assessment
                        updated_assessment = assessment.copy() if isinstance(assessment, dict) else assessment.to_dict()
                        
                        # Apply review decision
                        updated_assessment['original_decision'] = decision.original_decision
                        updated_assessment['decision'] = decision.final_decision
                        updated_assessment['reviewer'] = decision.reviewer
                        updated_assessment['review_date'] = decision.review_date
                        updated_assessment['justification'] = decision.justification
                        updated_assessment['evidence_references'] = decision.evidence_references
                        updated_assessment['additional_notes'] = decision.additional_notes
                        updated_assessment['review_status'] = decision.status.value
                        
                        # Update the assessment in the component data
                        updated_comp['risk_acceptance'][threat_name] = updated_assessment
        
        # Add the updated component to the result
        updated_data['components'][comp_id] = updated_comp
    
    return updated_data

def format_review_decision(decision: ReviewDecision) -> str:
    """Format review decision for display in reports"""
    result = []
    
    result.append(f"Review Status: {decision.status.value}")
    
    if decision.status != ReviewStatus.NOT_REVIEWED:
        result.append(f"Reviewer: {decision.reviewer}")
        result.append(f"Review Date: {decision.review_date}")
        
        if decision.original_decision != decision.final_decision:
            result.append(f"Original Decision: {decision.original_decision}")
            result.append(f"Final Decision: {decision.final_decision}")
        else:
            result.append(f"Decision: {decision.final_decision}")
        
        result.append(f"\nJustification: {decision.justification}")
        
        if decision.additional_notes:
            result.append(f"\nAdditional Notes: {decision.additional_notes}")
        
        if decision.evidence_references:
            result.append("\nEvidence References:")
            for evidence in decision.evidence_references:
                result.append(f"- {evidence}")
    else:
        result.append("This risk treatment has not been reviewed yet.")
    
    return "\n".join(result)
