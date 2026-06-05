"""
Assessment Status section — shows workflow governance counts.
Makes the report honest about what is draft vs approved.
"""
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def build_assessment_status_section(
    damage_scenarios: List[Dict[str, Any]],
    threat_scenarios: List[Dict[str, Any]],
    risk_treatments: List[Dict[str, Any]],
    styles,
) -> List:
    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]

    # Damage counts
    ds_total = len(damage_scenarios)
    ds_accepted = sum(1 for d in damage_scenarios if (d.get("status") or "").lower() == "accepted")
    ds_draft = ds_total - ds_accepted

    # Threat counts
    ts_total = len(threat_scenarios)
    ts_auto = sum(1 for t in threat_scenarios
                  if str(t.get("threat_scenario_id", "")).startswith("TS-AUTO-"))
    ts_reviewed = sum(1 for t in threat_scenarios
                      if (t.get("status") or "").lower() == "accepted")
    ts_draft = ts_total - ts_reviewed

    # Risk treatment counts
    rt_total = len(risk_treatments)
    rt_approved = sum(1 for r in risk_treatments
                      if (r.get("treatment_status") or "").lower() == "approved")
    rt_draft = rt_total - rt_approved
    rt_decided = sum(1 for r in risk_treatments if r.get("selected_treatment"))

    # Risk level counts
    critical = sum(1 for r in risk_treatments
                   if (r.get("risk_level") or "").lower() == "critical")
    high = sum(1 for r in risk_treatments
               if (r.get("risk_level") or "").lower() == "high")
    medium = sum(1 for r in risk_treatments
                 if (r.get("risk_level") or "").lower() == "medium")
    low = sum(1 for r in risk_treatments
              if (r.get("risk_level") or "").lower() == "low")

    def _row(label, value, note=""):
        return [
            Paragraph(str(label), styles["Normal"]),
            Paragraph(str(value), styles["Normal"]),
            Paragraph(str(note), styles["Normal"]),
        ]

    status_data = [
        [Paragraph("<b>Item</b>", styles["Normal"]),
         Paragraph("<b>Count</b>", styles["Normal"]),
         Paragraph("<b>Note</b>", styles["Normal"])],
        _row("Damage scenarios — total", ds_total),
        _row("Damage scenarios — accepted", ds_accepted),
        _row("Damage scenarios — draft / pending review", ds_draft,
             "Requires engineering review" if ds_draft else ""),
        _row("Threat scenarios — total", ts_total),
        _row("Threat scenarios — auto-generated (candidate)", ts_auto,
             "From MITRE ATT&CK ICS catalog — requires validation"),
        _row("Threat scenarios — engineer-reviewed / accepted", ts_reviewed),
        _row("Threat scenarios — draft / pending review", ts_draft,
             "Requires engineering review" if ts_draft else ""),
        _row("Risks identified", rt_total),
        _row("  Critical", critical),
        _row("  High", high),
        _row("  Medium", medium),
        _row("  Low", low),
        _row("Risks with treatment decision", rt_decided),
        _row("Approved treatment decisions", rt_approved),
        _row("Draft / pending treatment decisions", rt_draft,
             "Action required" if rt_draft else ""),
    ]

    table = Table(status_data, colWidths=[3.0 * inch, 1.0 * inch, 2.5 * inch],
                  repeatRows=1, splitByRow=True)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        # Highlight draft rows
        *[("TEXTCOLOR", (2, i), (2, i), colors.HexColor("#c0392b"))
          for i, row in enumerate(status_data[1:], 1)
          if "Action required" in str(row[2]) or "Requires engineering" in str(row[2])],
    ]))

    story: List = [
        Paragraph("Assessment Status", heading_style),
        Spacer(1, 6),
        Paragraph(
            "The table below shows the current workflow status of all TARA artifacts. "
            "Draft items have not yet been validated by the engineering team and should "
            "not be used as the basis for release decisions.",
            styles["Normal"],
        ),
        Spacer(1, 8),
        table,
        Spacer(1, 12),
    ]
    return story
