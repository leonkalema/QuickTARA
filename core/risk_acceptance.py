"""
Risk Acceptance Module for QuickTARA
Implements Clause 14 compliance by providing formal risk acceptance criteria
and rationale for accepting or rejecting risks
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Tuple

class RiskSeverity(Enum):
    NEGLIGIBLE = "Negligible"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class AcceptanceDecision(Enum):
    ACCEPT = "Accept"
    ACCEPT_WITH_CONTROLS = "Accept with Controls"
    TRANSFER = "Transfer"
    AVOID = "Avoid"
    MITIGATE = "Mitigate"

class StakeholderConcern(Enum):
    COMPLIANCE = "Regulatory Compliance"
    SAFETY = "Safety Impact"
    PRIVACY = "Privacy & Data Protection"
    FINANCIAL = "Financial Impact"
    REPUTATION = "Reputation & Brand"
    OPERATIONAL = "Operational Continuity"

@dataclass
class AcceptanceCriteria:
    max_severity: RiskSeverity
    required_controls: int  # Minimum number of controls required (0-5)
    stakeholder_approval: List[StakeholderConcern]
    residual_risk_threshold: float  # Maximum acceptable residual risk (0.0-1.0)
    reassessment_period: int  # Months before reassessment
    conditional_factors: List[str]  # Factors that might change the decision
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary"""
        return {
            'max_severity': self.max_severity.value,
            'required_controls': self.required_controls,
            'stakeholder_approval': [s.value for s in self.stakeholder_approval],
            'residual_risk_threshold': self.residual_risk_threshold,
            'reassessment_period': self.reassessment_period,
            'conditional_factors': self.conditional_factors
        }

@dataclass
class RiskAcceptanceAssessment:
    risk_severity: RiskSeverity
    decision: AcceptanceDecision
    criteria: AcceptanceCriteria
    justification: str
    conditions: List[str]
    residual_risk: float
    approvers: List[StakeholderConcern]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to serializable dictionary"""
        return {
            'risk_severity': self.risk_severity.value,
            'decision': self.decision.value,
            'criteria': self.criteria.to_dict(),
            'justification': self.justification,
            'conditions': self.conditions,
            'residual_risk': self.residual_risk,
            'approvers': [a.value for a in self.approvers]
        }

def get_default_criteria(component_type: str, safety_level: str) -> Dict[RiskSeverity, AcceptanceCriteria]:
    """Get default acceptance criteria based on component type and safety level"""
    # Base criteria
    base_criteria = {
        RiskSeverity.NEGLIGIBLE: AcceptanceCriteria(
            max_severity=RiskSeverity.NEGLIGIBLE,
            required_controls=0,
            stakeholder_approval=[],
            residual_risk_threshold=0.1,
            reassessment_period=24,
            conditional_factors=["Significant architecture change"]
        ),
        RiskSeverity.LOW: AcceptanceCriteria(
            max_severity=RiskSeverity.LOW,
            required_controls=1,
            stakeholder_approval=[StakeholderConcern.OPERATIONAL],
            residual_risk_threshold=0.3,
            reassessment_period=12,
            conditional_factors=["New vulnerability discovered", "Component update"]
        ),
        RiskSeverity.MEDIUM: AcceptanceCriteria(
            max_severity=RiskSeverity.MEDIUM,
            required_controls=2,
            stakeholder_approval=[StakeholderConcern.OPERATIONAL, StakeholderConcern.FINANCIAL],
            residual_risk_threshold=0.2,
            reassessment_period=6,
            conditional_factors=["New vulnerability discovered", "Threat landscape change", "Component update"]
        ),
        RiskSeverity.HIGH: AcceptanceCriteria(
            max_severity=RiskSeverity.HIGH,
            required_controls=3,
            stakeholder_approval=[StakeholderConcern.COMPLIANCE, StakeholderConcern.FINANCIAL, StakeholderConcern.REPUTATION],
            residual_risk_threshold=0.1,
            reassessment_period=3,
            conditional_factors=["New vulnerability discovered", "Threat landscape change", "Regulatory update", "Component update"]
        ),
        RiskSeverity.CRITICAL: AcceptanceCriteria(
            max_severity=RiskSeverity.CRITICAL,
            required_controls=5,
            stakeholder_approval=[StakeholderConcern.COMPLIANCE, StakeholderConcern.FINANCIAL, StakeholderConcern.REPUTATION, StakeholderConcern.SAFETY, StakeholderConcern.PRIVACY],
            residual_risk_threshold=0.05,
            reassessment_period=1,
            conditional_factors=["Any relevant change in system or environment"]
        )
    }
    
    # Adjust criteria based on safety level
    safety_adjustments = {
        "ASIL D": {
            RiskSeverity.MEDIUM: AcceptanceCriteria(
                max_severity=RiskSeverity.MEDIUM,
                required_controls=3,
                stakeholder_approval=[StakeholderConcern.OPERATIONAL, StakeholderConcern.FINANCIAL, StakeholderConcern.SAFETY],
                residual_risk_threshold=0.1,
                reassessment_period=3,
                conditional_factors=["New vulnerability discovered", "Threat landscape change", "Component update", "Safety requirements change"]
            ),
            RiskSeverity.HIGH: AcceptanceCriteria(
                max_severity=RiskSeverity.HIGH,
                required_controls=4,
                stakeholder_approval=[StakeholderConcern.COMPLIANCE, StakeholderConcern.FINANCIAL, StakeholderConcern.REPUTATION, StakeholderConcern.SAFETY],
                residual_risk_threshold=0.05,
                reassessment_period=1,
                conditional_factors=["New vulnerability discovered", "Threat landscape change", "Regulatory update", "Component update", "Safety requirements change"]
            ),
            RiskSeverity.CRITICAL: AcceptanceCriteria(
                max_severity=RiskSeverity.CRITICAL,
                required_controls=5,
                stakeholder_approval=[StakeholderConcern.COMPLIANCE, StakeholderConcern.FINANCIAL, StakeholderConcern.REPUTATION, StakeholderConcern.SAFETY, StakeholderConcern.PRIVACY, StakeholderConcern.OPERATIONAL],
                residual_risk_threshold=0.01,
                reassessment_period=1,
                conditional_factors=["Any change in system or environment"]
            )
        },
        "ASIL C": {
            RiskSeverity.HIGH: AcceptanceCriteria(
                max_severity=RiskSeverity.HIGH,
                required_controls=4,
                stakeholder_approval=[StakeholderConcern.COMPLIANCE, StakeholderConcern.FINANCIAL, StakeholderConcern.SAFETY],
                residual_risk_threshold=0.05,
                reassessment_period=2,
                conditional_factors=["New vulnerability discovered", "Threat landscape change", "Regulatory update", "Component update"]
            )
        }
    }
    
    # Component-specific adjustments
    component_adjustments = {
        "Gateway": {
            RiskSeverity.MEDIUM: AcceptanceCriteria(
                max_severity=RiskSeverity.MEDIUM,
                required_controls=3,
                stakeholder_approval=[StakeholderConcern.OPERATIONAL, StakeholderConcern.FINANCIAL, StakeholderConcern.PRIVACY],
                residual_risk_threshold=0.15,
                reassessment_period=6,
                conditional_factors=["New vulnerability discovered", "Threat landscape change", "Component update", "Connected systems change"]
            )
        },
        "ECU": {
            RiskSeverity.HIGH: AcceptanceCriteria(
                max_severity=RiskSeverity.HIGH,
                required_controls=4,
                stakeholder_approval=[StakeholderConcern.COMPLIANCE, StakeholderConcern.SAFETY],
                residual_risk_threshold=0.05,
                reassessment_period=3,
                conditional_factors=["New vulnerability discovered", "Threat landscape change", "Regulatory update", "Component update", "Safety requirements change"]
            )
        }
    }
    
    # Create adjusted criteria dictionary
    adjusted_criteria = base_criteria.copy()
    
    # Apply safety level adjustments if applicable
    if safety_level in safety_adjustments:
        for severity, criteria in safety_adjustments[safety_level].items():
            adjusted_criteria[severity] = criteria
    
    # Apply component type adjustments if applicable
    for component_key, adjustments in component_adjustments.items():
        if component_key.lower() in component_type.lower():
            for severity, criteria in adjustments.items():
                adjusted_criteria[severity] = criteria
    
    return adjusted_criteria

def calculate_risk_severity(impact_scores: Dict[str, int], likelihood: int) -> RiskSeverity:
    """Calculate overall risk severity based on impact scores and likelihood.

    If impact_scores contains SFOP keys (safety, financial, operational, privacy)
    the SFOP-aware calculator is used. Otherwise falls back to max-based scoring.
    """
    sfop_keys = {"safety", "financial", "operational", "privacy"}
    if sfop_keys.issubset(impact_scores.keys()):
        return calculate_risk_severity_sfop(impact_scores, likelihood)
    # Legacy fallback: max-based scoring
    max_impact = max(impact_scores.values()) if impact_scores else 0
    risk_score = max_impact * likelihood
    if risk_score <= 4:
        return RiskSeverity.NEGLIGIBLE
    elif risk_score <= 8:
        return RiskSeverity.LOW
    elif risk_score <= 12:
        return RiskSeverity.MEDIUM
    elif risk_score <= 20:
        return RiskSeverity.HIGH
    else:
        return RiskSeverity.CRITICAL


def calculate_risk_severity_sfop(
    impact_scores: Dict[str, int], likelihood: int
) -> RiskSeverity:
    """SFOP-aware risk severity using core.sfop_risk_calculator.

    Maps SFOP integer scores (1-5) to ImpactLevel strings, derives overall
    impact via worst-case, then combines with likelihood via the ISO 21434
    risk matrix.
    """
    from core.sfop_risk_calculator import calculate_risk, RiskLevel
    score_to_level = {0: "negligible", 1: "negligible", 2: "moderate", 3: "major", 4: "severe", 5: "severe"}
    likelihood_to_feas = {1: "very_low", 2: "low", 3: "medium", 4: "high", 5: "very_high"}
    result = calculate_risk(
        safety=score_to_level.get(impact_scores.get("safety", 0), "negligible"),
        financial=score_to_level.get(impact_scores.get("financial", 0), "negligible"),
        operational=score_to_level.get(impact_scores.get("operational", 0), "negligible"),
        privacy=score_to_level.get(impact_scores.get("privacy", 0), "negligible"),
        feasibility=likelihood_to_feas.get(likelihood, "medium"),
    )
    risk_map = {
        RiskLevel.NEGLIGIBLE: RiskSeverity.NEGLIGIBLE,
        RiskLevel.LOW: RiskSeverity.LOW,
        RiskLevel.MEDIUM: RiskSeverity.MEDIUM,
        RiskLevel.HIGH: RiskSeverity.HIGH,
        RiskLevel.CRITICAL: RiskSeverity.CRITICAL,
    }
    return risk_map.get(result.risk_level, RiskSeverity.MEDIUM)

def calculate_residual_risk(impact_scores: Dict[str, int], likelihood: int, controls_count: int) -> float:
    """Calculate residual risk after controls (0.0-1.0 scale)"""
    # Get the maximum impact score
    max_impact = max(impact_scores.values()) if impact_scores else 0
    
    # Base risk (0.0-1.0)
    base_risk = (max_impact * likelihood) / 25.0
    
    # Reduction factor based on controls (diminishing returns)
    if controls_count <= 0:
        reduction_factor = 0.0
    elif controls_count == 1:
        reduction_factor = 0.3
    elif controls_count == 2:
        reduction_factor = 0.5
    elif controls_count == 3:
        reduction_factor = 0.7
    elif controls_count == 4:
        reduction_factor = 0.8
    else:
        reduction_factor = 0.9
    
    # Calculate residual risk
    residual_risk = base_risk * (1.0 - reduction_factor)
    
    return max(0.0, min(1.0, residual_risk))  # Ensure it's between 0 and 1

def determine_acceptance_decision(
    severity: RiskSeverity,
    residual_risk: float,
    criteria: AcceptanceCriteria
) -> AcceptanceDecision:
    """Determine the acceptance decision based on severity and residual risk"""
    # Automatic decisions based on severity
    severity_decisions = {
        RiskSeverity.NEGLIGIBLE: AcceptanceDecision.ACCEPT,
        RiskSeverity.CRITICAL: AcceptanceDecision.AVOID
    }
    
    if severity in severity_decisions:
        return severity_decisions[severity]
    
    # Decision based on residual risk vs threshold
    if residual_risk <= criteria.residual_risk_threshold:
        if severity == RiskSeverity.LOW:
            return AcceptanceDecision.ACCEPT
        else:
            return AcceptanceDecision.ACCEPT_WITH_CONTROLS
    elif severity == RiskSeverity.HIGH:
        return AcceptanceDecision.MITIGATE
    else:
        return AcceptanceDecision.TRANSFER

def generate_justification(
    severity: RiskSeverity,
    decision: AcceptanceDecision,
    residual_risk: float,
    impact_categories: List[str],
    criteria: AcceptanceCriteria
) -> str:
    """Generate a justification for the acceptance decision"""
    justification_templates = {
        AcceptanceDecision.ACCEPT: [
            "Risk is within acceptable limits with a residual risk of {residual:.1%}.",
            "The {severity} severity and minimal {impact} impact justifies acceptance.",
            "Formal acceptance based on {severity} severity classification with {residual:.1%} residual risk."
        ],
        AcceptanceDecision.ACCEPT_WITH_CONTROLS: [
            "Risk can be accepted with {controls} controls, reducing residual risk to {residual:.1%}.",
            "The {severity} severity requires conditions including {controls} controls to maintain residual risk at {residual:.1%}.",
            "Conditional acceptance based on implementing controls to address {impact} impacts."
        ],
        AcceptanceDecision.TRANSFER: [
            "Risk transfer recommended due to {severity} severity and potential {impact} impact.",
            "The {severity} severity combined with residual risk of {residual:.1%} requires risk transfer.",
            "Risk transfer approach required due to exceeding acceptable thresholds for {impact} impacts."
        ],
        AcceptanceDecision.AVOID: [
            "Risk avoidance required due to {severity} severity with significant {impact} impact.",
            "The {severity} severity classification mandates risk avoidance per acceptance criteria.",
            "Automatic risk avoidance triggered by {severity} severity classification."
        ],
        AcceptanceDecision.MITIGATE: [
            "Additional mitigation required to reduce {severity} severity risk with {impact} impact.",
            "Risk mitigation needed as residual risk of {residual:.1%} exceeds threshold of {threshold:.1%}.",
            "Mitigation required to address {impact} impacts before reconsideration."
        ]
    }
    
    # Select template based on decision
    templates = justification_templates.get(decision, justification_templates[AcceptanceDecision.MITIGATE])
    template = templates[hash(str(severity) + str(decision)) % len(templates)]
    
    # Format the template
    impact_str = " and ".join(impact_categories[:2])
    justification = template.format(
        severity=severity.value,
        residual=residual_risk,
        impact=impact_str,
        controls=criteria.required_controls,
        threshold=criteria.residual_risk_threshold
    )
    
    return justification

def generate_conditions(
    decision: AcceptanceDecision,
    criteria: AcceptanceCriteria,
    component_type: str
) -> List[str]:
    """Generate conditions for risk acceptance"""
    # Base conditions by decision type
    base_conditions = {
        AcceptanceDecision.ACCEPT: [
            "Annual risk review required",
            "Report changes that could affect risk assessment"
        ],
        AcceptanceDecision.ACCEPT_WITH_CONTROLS: [
            f"Implement at least {criteria.required_controls} security controls",
            f"Risk reassessment required every {criteria.reassessment_period} months",
            "Document control effectiveness evidence"
        ],
        AcceptanceDecision.TRANSFER: [
            "Identify appropriate risk transfer mechanism",
            "Establish contractual requirements for external parties",
            "Maintain backup capabilities for critical functions"
        ],
        AcceptanceDecision.AVOID: [
            "Redesign to eliminate risk source",
            "Implement alternative solution without identified risk",
            "Document design changes and verification of risk elimination"
        ],
        AcceptanceDecision.MITIGATE: [
            "Develop detailed risk treatment plan",
            f"Implement additional controls beyond minimum {criteria.required_controls}",
            "Perform validation testing of mitigations",
            f"Reassess in {max(1, criteria.reassessment_period // 2)} months"
        ]
    }
    
    # Get base conditions for this decision
    conditions = base_conditions.get(decision, [])
    
    # Add component-specific conditions
    if "ECU" in component_type:
        if decision in [AcceptanceDecision.ACCEPT_WITH_CONTROLS, AcceptanceDecision.MITIGATE]:
            conditions.append("Validate mitigations through ECU-specific testing")
    elif "Gateway" in component_type:
        if decision in [AcceptanceDecision.ACCEPT_WITH_CONTROLS, AcceptanceDecision.MITIGATE]:
            conditions.append("Ensure network segmentation and filtering rules are validated")
    elif "Sensor" in component_type:
        if decision in [AcceptanceDecision.ACCEPT_WITH_CONTROLS, AcceptanceDecision.MITIGATE]:
            conditions.append("Implement plausibility checks for sensor data")
    
    # Add conditional factors from criteria
    for factor in criteria.conditional_factors[:2]:
        conditions.append(f"Reassess if {factor.lower()} occurs")
    
    return conditions

def assess_risk_acceptance(
    component_type: str,
    safety_level: str,
    threat_name: str,
    threat_description: str,
    impact_scores: Dict[str, int],
    likelihood: int,
    implemented_controls: int = 0
) -> RiskAcceptanceAssessment:
    """Assess risk acceptance for a specific threat"""
    # Calculate risk severity
    severity = calculate_risk_severity(impact_scores, likelihood)
    
    # Get acceptance criteria based on component type and safety level
    criteria_set = get_default_criteria(component_type, safety_level)
    criteria = criteria_set.get(severity, criteria_set[RiskSeverity.MEDIUM])
    
    # Calculate residual risk
    residual_risk = calculate_residual_risk(impact_scores, likelihood, implemented_controls)
    
    # Determine acceptance decision
    decision = determine_acceptance_decision(severity, residual_risk, criteria)
    
    # Generate justification
    impact_categories = list(impact_scores.keys())
    justification = generate_justification(severity, decision, residual_risk, impact_categories, criteria)
    
    # Generate conditions
    conditions = generate_conditions(decision, criteria, component_type)
    
    # Determine required approvers based on criteria and decision
    if decision == AcceptanceDecision.ACCEPT:
        approvers = criteria.stakeholder_approval[:1]  # Minimal approval for accepted risks
    else:
        approvers = criteria.stakeholder_approval  # Full approval list for other decisions
    
    # Create assessment
    assessment = RiskAcceptanceAssessment(
        risk_severity=severity,
        decision=decision,
        criteria=criteria,
        justification=justification,
        conditions=conditions,
        residual_risk=residual_risk,
        approvers=approvers
    )
    
    return assessment

def assess_component_risk_acceptance(component_data: Dict[str, Any]) -> Dict[str, RiskAcceptanceAssessment]:
    """Assess risk acceptance for all threats associated with a component"""
    result = {}
    
    component_type = component_data.get('type', '')
    safety_level = component_data.get('safety_level', '')
    threats = component_data.get('threats', [])
    
    for threat in threats:
        threat_name = threat.get('name', '')
        threat_description = threat.get('description', '')
        impact_scores = threat.get('impact', {})
        likelihood = threat.get('likelihood', 3)
        
        # Estimate implemented controls from component data and threat information
        # This is a placeholder - in a real system you would track actual implemented controls
        implemented_controls = min(3, len(threat.get('mitigations', '').split(',')))
        
        assessment = assess_risk_acceptance(
            component_type,
            safety_level,
            threat_name,
            threat_description,
            impact_scores,
            likelihood,
            implemented_controls
        )
        
        result[threat_name] = assessment
    
    return result

def format_risk_acceptance(assessment: RiskAcceptanceAssessment) -> str:
    """Format risk acceptance assessment for display in reports"""
    result = []
    
    # Decision and severity
    result.append(f"Risk Acceptance Decision: {assessment.decision.value}")
    result.append(f"Risk Severity: {assessment.risk_severity.value}")
    result.append(f"Residual Risk: {assessment.residual_risk:.1%}")
    
    # Justification
    result.append(f"\nJustification: {assessment.justification}")
    
    # Conditions
    if assessment.conditions:
        result.append("\nConditions:")
        for condition in assessment.conditions:
            result.append(f"- {condition}")
    
    # Required approvals
    if assessment.approvers:
        result.append("\nRequired Approvals:")
        for approver in assessment.approvers:
            result.append(f"- {approver.value}")
    
    # Reassessment period
    result.append(f"\nReassessment Period: {assessment.criteria.reassessment_period} months")
    
    return "\n".join(result)
