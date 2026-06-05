"""
Treatment Decision Summary — shows what is being done about each risk.
"""
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def build_treatment_summary_section(
    damage_scenarios: List[Dict[str, Any]],
    risk_treatments: List[Dict[str, Any]],
    styles,
) -> List:
    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]

    if not risk_treatments:
        return [
            Paragraph("Risk Treatment Summary (§14)", heading_style),
            Spacer(1, 6),
            Paragraph("No treatment decisions have been recorded.", styles["Normal"]),
            Spacer(1, 12),
        ]

    ds_by_id = {d["scenario_id"]: d for d in damage_scenarios}

    header = [
        Paragraph("<b>Risk ID</b>", styles["Normal"]),
        Paragraph("<b>Risk level</b>", styles["Normal"]),
        Paragraph("<b>Treatment decision</b>", styles["Normal"]),
        Paragraph("<b>Rationale / Goal</b>", styles["Normal"]),
        Paragraph("<b>Status</b>", styles["Normal"]),
    ]
    rows = [header]

    _order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_risks = sorted(
        risk_treatments,
        key=lambda r: _order.get((r.get("risk_level") or "").lower(), 9),
    )

    for i, rt in enumerate(sorted_risks, 1):
        treatment = rt.get("selected_treatment") or rt.get("suggested_treatment") or "—"
        goal = rt.get("treatment_goal") or "—"
        if len(goal) > 80:
            goal = goal[:77] + "…"
        status = (rt.get("treatment_status") or "Draft").capitalize()
        risk_level = (rt.get("risk_level") or "—").capitalize()

        rows.append([
            f"R-{i:03d}",
            risk_level,
            treatment.capitalize(),
            goal,
            status,
        ])

    col_widths = [0.65*inch, 0.85*inch, 1.2*inch, 3.0*inch, 0.8*inch]
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
        Paragraph("Risk Treatment Summary (§14)", heading_style),
        Spacer(1, 6),
        Paragraph(
            "The following table summarises the treatment decision for each identified risk. "
            "Treatment decisions must be approved by the responsible engineering owner before "
            "the product can be considered ready for release.",
            styles["Normal"],
        ),
        Spacer(1, 8),
        table,
        Spacer(1, 12),
    ]
    return story
