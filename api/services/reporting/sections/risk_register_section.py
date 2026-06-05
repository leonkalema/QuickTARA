"""
Risk Register section — full risk table linking damage scenario,
impact, feasibility, risk level, treatment decision, and status.
This is the section OEMs care about most.
"""
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

_RISK_COLOURS = {
    "critical": colors.HexColor("#c0392b"),
    "high":     colors.HexColor("#e67e22"),
    "medium":   colors.HexColor("#f1c40f"),
    "low":      colors.HexColor("#27ae60"),
}


def build_risk_register_section(
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
            Paragraph("Risk Register (§15.7)", heading_style),
            Spacer(1, 6),
            Paragraph("No risks have been assessed for this product.", styles["Normal"]),
            Spacer(1, 12),
        ]

    # Build damage scenario lookup
    ds_by_id = {d["scenario_id"]: d for d in damage_scenarios}

    # Sort: Critical → High → Medium → Low
    _order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_risks = sorted(
        risk_treatments,
        key=lambda r: _order.get((r.get("risk_level") or "").lower(), 9),
    )

    header = [
        Paragraph("<b>Risk ID</b>", styles["Normal"]),
        Paragraph("<b>Damage scenario</b>", styles["Normal"]),
        Paragraph("<b>Impact</b>", styles["Normal"]),
        Paragraph("<b>Feasibility</b>", styles["Normal"]),
        Paragraph("<b>Risk level</b>", styles["Normal"]),
        Paragraph("<b>Treatment</b>", styles["Normal"]),
        Paragraph("<b>Status</b>", styles["Normal"]),
    ]
    rows = [header]
    risk_colour_cmds = []

    for i, rt in enumerate(sorted_risks, 1):
        ds = ds_by_id.get(rt.get("damage_scenario_id"), {})
        ds_name = ds.get("name", rt.get("damage_scenario_id", "—"))
        if len(ds_name) > 45:
            ds_name = ds_name[:42] + "…"

        risk_level = (rt.get("risk_level") or "—").capitalize()
        rl_lower = risk_level.lower()
        treatment = (rt.get("selected_treatment") or rt.get("suggested_treatment") or "—").capitalize()
        status = (rt.get("treatment_status") or "Draft").capitalize()

        rows.append([
            f"R-{i:03d}",
            ds_name,
            (rt.get("impact_level") or "—").capitalize(),
            (rt.get("feasibility_level") or "—").capitalize(),
            risk_level,
            treatment,
            status,
        ])

        colour = _RISK_COLOURS.get(rl_lower)
        if colour:
            row_idx = len(rows) - 1
            risk_colour_cmds.append(("TEXTCOLOR", (4, row_idx), (4, row_idx), colour))

    col_widths = [0.7*inch, 1.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.8*inch]
    table = Table(rows, colWidths=col_widths, repeatRows=1, splitByRow=True)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ] + risk_colour_cmds
    table.setStyle(TableStyle(style_cmds))

    story: List = [
        Paragraph("Risk Register (§15.7)", heading_style),
        Spacer(1, 6),
        Paragraph(
            "The risk register lists all assessed risks sorted by severity. "
            "Risk level is determined by combining the SFOP impact rating with "
            "the attack feasibility rating per ISO/SAE 21434 §15.7.",
            styles["Normal"],
        ),
        Spacer(1, 8),
        table,
        Spacer(1, 12),
    ]
    return story
