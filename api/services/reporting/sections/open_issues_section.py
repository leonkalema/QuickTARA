"""
Open Issues and Customer Actions section.
Shows what remains unresolved, draft, or requires external input.
"""
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def build_open_issues_section(
    damage_scenarios: List[Dict[str, Any]],
    threat_scenarios: List[Dict[str, Any]],
    risk_treatments: List[Dict[str, Any]],
    styles,
) -> List:
    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]

    issues: List[Dict[str, str]] = []

    # Draft threat scenarios
    draft_ts = [t for t in threat_scenarios
                if (t.get("status") or "").lower() != "accepted"]
    if draft_ts:
        issues.append({
            "category": "Threat scenarios",
            "issue": f"{len(draft_ts)} candidate threat scenario(s) require engineering validation before acceptance.",
            "action": "Internal — engineering team",
            "priority": "High",
        })

    # Draft damage scenarios
    draft_ds = [d for d in damage_scenarios
                if (d.get("status") or "").lower() not in ("accepted", "approved")]
    if draft_ds:
        issues.append({
            "category": "Damage scenarios",
            "issue": f"{len(draft_ds)} damage scenario(s) are in draft status.",
            "action": "Internal — engineering team",
            "priority": "High",
        })

    # Risks without treatment decisions
    no_treatment = [r for r in risk_treatments if not r.get("selected_treatment")]
    if no_treatment:
        issues.append({
            "category": "Risk treatment",
            "issue": f"{len(no_treatment)} risk(s) have no treatment decision recorded.",
            "action": "Internal — risk owner",
            "priority": "High",
        })

    # Draft treatment decisions
    draft_treatments = [r for r in risk_treatments
                        if r.get("selected_treatment") and
                        (r.get("treatment_status") or "").lower() != "approved"]
    if draft_treatments:
        issues.append({
            "category": "Treatment approval",
            "issue": f"{len(draft_treatments)} treatment decision(s) pending engineering approval.",
            "action": "Internal — engineering sign-off required",
            "priority": "Medium",
        })

    # Critical risks
    critical = [r for r in risk_treatments
                if (r.get("risk_level") or "").lower() == "critical"]
    if critical:
        issues.append({
            "category": "Residual risk",
            "issue": f"{len(critical)} Critical risk(s) identified. Confirm residual risk acceptance or treatment before release.",
            "action": "Internal — management sign-off / customer confirmation",
            "priority": "Critical",
        })

    # Standard standing items for customer-facing reports
    issues += [
        {
            "category": "Architecture assumptions",
            "issue": "OEM to confirm gateway filtering and network segmentation assumptions used in this assessment.",
            "action": "Customer — OEM/Tier-1",
            "priority": "Medium",
        },
        {
            "category": "Diagnostic access policy",
            "issue": "OEM to confirm physical diagnostic connector access control policy (e.g. workshop authentication, access restrictions).",
            "action": "Customer — OEM/Tier-1",
            "priority": "Medium",
        },
    ]

    _priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    issues.sort(key=lambda x: _priority_order.get(x["priority"].lower(), 9))

    header = [
        Paragraph("<b>Category</b>", styles["Normal"]),
        Paragraph("<b>Issue / Action required</b>", styles["Normal"]),
        Paragraph("<b>Owner</b>", styles["Normal"]),
        Paragraph("<b>Priority</b>", styles["Normal"]),
    ]
    rows = [header]
    P = lambda t: Paragraph(str(t), styles["Normal"])
    for issue in issues:
        rows.append([
            P(issue["category"]),
            P(issue["issue"]),
            P(issue["action"]),
            P(issue["priority"]),
        ])

    col_widths = [1.3*inch, 3.2*inch, 1.5*inch, 0.8*inch]
    table = Table(rows, colWidths=col_widths, repeatRows=1, splitByRow=True)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    story: List = [
        Paragraph("Open Issues and Customer Actions", heading_style),
        Spacer(1, 6),
        Paragraph(
            "The following items require resolution before this assessment can be considered "
            "complete. Items marked 'Customer' require confirmation or input from the OEM or "
            "customer organisation.",
            styles["Normal"],
        ),
        Spacer(1, 8),
    ]

    if not issues:
        story.append(Paragraph("No open issues identified.", styles["Normal"]))
    else:
        story.append(table)

    story.append(Spacer(1, 12))
    return story
