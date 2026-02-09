"""
SFOP-Aware Risk Calculator for QuickTARA

Implements ISO/SAE 21434 §9.4 impact rating using the four SFOP dimensions
(Safety, Financial, Operational, Privacy) and combines with attack feasibility
to produce a risk level.

The overall impact is derived as the worst-case (maximum) across all four
dimensions, consistent with ISO 21434 §9.7 risk value determination.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple


class ImpactLevel(str, Enum):
    """ISO 21434 §9.4 impact rating levels (4-point scale)."""
    NEGLIGIBLE = "negligible"
    MODERATE = "moderate"
    MAJOR = "major"
    SEVERE = "severe"


class FeasibilityLevel(str, Enum):
    """ISO 21434 §9.6 attack feasibility levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RiskLevel(str, Enum):
    """ISO 21434 §9.7 risk value levels."""
    NEGLIGIBLE = "Negligible"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


# ── Numeric mappings ──────────────────────────────────────────────────────

IMPACT_NUMERIC: Dict[ImpactLevel, int] = {
    ImpactLevel.NEGLIGIBLE: 0,
    ImpactLevel.MODERATE: 1,
    ImpactLevel.MAJOR: 2,
    ImpactLevel.SEVERE: 3,
}

FEASIBILITY_NUMERIC: Dict[FeasibilityLevel, int] = {
    FeasibilityLevel.VERY_LOW: 0,
    FeasibilityLevel.LOW: 1,
    FeasibilityLevel.MEDIUM: 2,
    FeasibilityLevel.HIGH: 3,
    FeasibilityLevel.VERY_HIGH: 4,
}

# ── ISO 21434 §9.7-style risk matrix ─────────────────────────────────────
# Rows = overall impact (0-3), Columns = feasibility (0-4)
# Each cell maps to a RiskLevel
RISK_MATRIX: list[list[RiskLevel]] = [
    #  VLow        Low          Med          High         VHigh       ← feasibility
    [RiskLevel.NEGLIGIBLE, RiskLevel.NEGLIGIBLE, RiskLevel.NEGLIGIBLE, RiskLevel.LOW,    RiskLevel.LOW],      # negligible impact
    [RiskLevel.NEGLIGIBLE, RiskLevel.LOW,        RiskLevel.LOW,        RiskLevel.MEDIUM,  RiskLevel.MEDIUM],   # moderate impact
    [RiskLevel.LOW,        RiskLevel.LOW,        RiskLevel.MEDIUM,     RiskLevel.HIGH,    RiskLevel.HIGH],     # major impact
    [RiskLevel.LOW,        RiskLevel.MEDIUM,     RiskLevel.HIGH,       RiskLevel.CRITICAL, RiskLevel.CRITICAL], # severe impact
]


@dataclass(frozen=True)
class SfopRating:
    """SFOP impact ratings for a damage scenario."""
    safety: ImpactLevel = ImpactLevel.NEGLIGIBLE
    financial: ImpactLevel = ImpactLevel.NEGLIGIBLE
    operational: ImpactLevel = ImpactLevel.NEGLIGIBLE
    privacy: ImpactLevel = ImpactLevel.NEGLIGIBLE


@dataclass(frozen=True)
class RiskResult:
    """Full risk calculation result."""
    sfop: SfopRating
    overall_impact: ImpactLevel
    feasibility: FeasibilityLevel
    risk_level: RiskLevel
    impact_numeric: int
    feasibility_numeric: int
    dominant_dimension: str  # which SFOP dimension drove the overall impact


def _parse_impact(value: Optional[str]) -> ImpactLevel:
    """Safely parse a string to ImpactLevel, defaulting to NEGLIGIBLE."""
    if value is None:
        return ImpactLevel.NEGLIGIBLE
    normalized = value.strip().lower()
    try:
        return ImpactLevel(normalized)
    except ValueError:
        # Handle legacy values like "low", "medium", "high", "critical"
        legacy_map = {
            "low": ImpactLevel.NEGLIGIBLE,
            "medium": ImpactLevel.MODERATE,
            "high": ImpactLevel.MAJOR,
            "critical": ImpactLevel.SEVERE,
        }
        return legacy_map.get(normalized, ImpactLevel.NEGLIGIBLE)


def _parse_feasibility(value: Optional[str]) -> FeasibilityLevel:
    """Safely parse a string to FeasibilityLevel."""
    if value is None:
        return FeasibilityLevel.MEDIUM
    normalized = value.strip().lower().replace(" ", "_")
    try:
        return FeasibilityLevel(normalized)
    except ValueError:
        return FeasibilityLevel.MEDIUM


def compute_overall_impact(sfop: SfopRating) -> Tuple[ImpactLevel, str]:
    """Derive the overall impact as worst-case across SFOP dimensions.

    Returns (overall_impact_level, dominant_dimension_name).
    Per ISO 21434 §9.4, the overall impact is the maximum across all four
    dimensions because a single severe impact in any dimension is sufficient
    to classify the overall impact as severe.
    """
    dimensions = {
        "safety": sfop.safety,
        "financial": sfop.financial,
        "operational": sfop.operational,
        "privacy": sfop.privacy,
    }
    worst_dim = max(dimensions, key=lambda d: IMPACT_NUMERIC[dimensions[d]])
    return dimensions[worst_dim], worst_dim


def calculate_risk(
    safety: Optional[str] = None,
    financial: Optional[str] = None,
    operational: Optional[str] = None,
    privacy: Optional[str] = None,
    feasibility: Optional[str] = None,
) -> RiskResult:
    """Calculate the risk level from SFOP impact ratings and feasibility.

    Args:
        safety: Safety impact level string (negligible/moderate/major/severe)
        financial: Financial impact level string
        operational: Operational impact level string
        privacy: Privacy impact level string
        feasibility: Attack feasibility level string (very_low..very_high)

    Returns:
        RiskResult with full breakdown.
    """
    sfop = SfopRating(
        safety=_parse_impact(safety),
        financial=_parse_impact(financial),
        operational=_parse_impact(operational),
        privacy=_parse_impact(privacy),
    )
    overall_impact, dominant = compute_overall_impact(sfop)
    feas = _parse_feasibility(feasibility)
    impact_idx = IMPACT_NUMERIC[overall_impact]
    feas_idx = FEASIBILITY_NUMERIC[feas]
    risk_level = RISK_MATRIX[impact_idx][feas_idx]
    return RiskResult(
        sfop=sfop,
        overall_impact=overall_impact,
        feasibility=feas,
        risk_level=risk_level,
        impact_numeric=impact_idx,
        feasibility_numeric=feas_idx,
        dominant_dimension=dominant,
    )


def calculate_risk_from_damage_scenario(
    damage_scenario: dict,
    feasibility: Optional[str] = None,
) -> RiskResult:
    """Calculate risk from a damage scenario dict (as stored in DB).

    Reads safety_impact, financial_impact, operational_impact, privacy_impact
    fields directly from the scenario dict.
    """
    return calculate_risk(
        safety=damage_scenario.get("safety_impact"),
        financial=damage_scenario.get("financial_impact"),
        operational=damage_scenario.get("operational_impact"),
        privacy=damage_scenario.get("privacy_impact"),
        feasibility=feasibility,
    )


def risk_result_to_dict(result: RiskResult) -> Dict[str, str]:
    """Serialize a RiskResult to a plain dict for API responses."""
    return {
        "safety_impact": result.sfop.safety.value,
        "financial_impact": result.sfop.financial.value,
        "operational_impact": result.sfop.operational.value,
        "privacy_impact": result.sfop.privacy.value,
        "overall_impact": result.overall_impact.value,
        "dominant_dimension": result.dominant_dimension,
        "feasibility": result.feasibility.value,
        "risk_level": result.risk_level.value,
        "impact_numeric": str(result.impact_numeric),
        "feasibility_numeric": str(result.feasibility_numeric),
    }
