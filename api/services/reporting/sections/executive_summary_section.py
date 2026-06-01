"""
Executive Summary section.

A short, audience-agnostic overview placed at the top of the report body:
scope counts, risk-level distribution, the highest risk present, and treatment
coverage. The numeric aggregation is kept in a pure helper so it can be tested
without reportlab.
"""
from collections import Counter
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


# Severity/risk ordering from most to least severe for "highest risk" lookup.
_RISK_ORDER: List[str] = ["Critical", "High", "Medium", "Low"]


def compute_executive_stats(
    assets: List[Dict[str, Any]],
    damage_scenarios: List[Dict[str, Any]],
    threat_scenarios: List[Dict[str, Any]],
    risk_treatments: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate headline numbers for the executive summary.

    Pure (no reportlab) for testability.
    """
    risk_distribution = Counter(
        (rt.get("risk_level") or "Unknown") for rt in risk_treatments
    )
    highest_risk = next(
        (level for level in _RISK_ORDER if risk_distribution.get(level)),
        "None",
    )
    approved = sum(
        1
        for rt in risk_treatments
        if (rt.get("treatment_status") or "").strip().lower() == "approved"
    )
    treated = sum(1 for rt in risk_treatments if rt.get("selected_treatment"))
    total_treatments = len(risk_treatments)
    coverage_pct = round(100 * treated / total_treatments) if total_treatments else 0

    return {
        "asset_count": len(assets),
        "damage_scenario_count": len(damage_scenarios),
        "threat_scenario_count": len(threat_scenarios),
        "risk_count": total_treatments,
        "risk_distribution": dict(risk_distribution),
        "highest_risk": highest_risk,
        "approved_treatments": approved,
        "treatment_coverage_pct": coverage_pct,
    }


def _counts_table(stats: Dict[str, Any]) -> Table:
    rows = [
        ["Assets", str(stats["asset_count"])],
        ["Damage scenarios", str(stats["damage_scenario_count"])],
        ["Threat scenarios", str(stats["threat_scenario_count"])],
        ["Assessed risks", str(stats["risk_count"])],
        ["Highest risk", stats["highest_risk"]],
        ["Treatment coverage", f"{stats['treatment_coverage_pct']}%"],
        ["Approved treatments", str(stats["approved_treatments"])],
    ]
    table = Table(rows, colWidths=[2.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    return table


def build_executive_summary_section(
    assets: List[Dict[str, Any]],
    damage_scenarios: List[Dict[str, Any]],
    threat_scenarios: List[Dict[str, Any]],
    risk_treatments: List[Dict[str, Any]],
    styles,
) -> List:
    """Build the executive summary flowables."""
    stats = compute_executive_stats(
        assets, damage_scenarios, threat_scenarios, risk_treatments
    )

    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]

    story: List = [Paragraph("Executive Summary", heading_style), Spacer(1, 6)]

    narrative = (
        f"This assessment covers {stats['asset_count']} asset(s) across "
        f"{stats['damage_scenario_count']} damage scenario(s) and "
        f"{stats['threat_scenario_count']} threat scenario(s). "
        f"{stats['risk_count']} risk(s) were determined, with a highest "
        f"residual rating of {stats['highest_risk']}. "
        f"{stats['treatment_coverage_pct']}% of risks have a treatment decision, "
        f"of which {stats['approved_treatments']} are approved."
    )
    story.append(Paragraph(narrative, styles["Normal"]))
    story.append(Spacer(1, 8))
    story.append(_counts_table(stats))
    story.append(Spacer(1, 20))
    return story
