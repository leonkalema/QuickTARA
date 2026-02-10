"""
CRA Compliance report section builder for PDF reports.

Generates a status overview table plus per-gap detail with guidance,
remediation actions, and effort estimates.

Depends on: db.cra_models, core.cra_auto_mapper, core.cra_requirement_guidance
Used by: api/services/reporting/ (main report builder)
"""
from typing import List, Optional
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from sqlalchemy.orm import Session

from db.cra_models import CraAssessment, CraRequirementStatusRecord
from core.cra_auto_mapper import get_requirement_by_id
from core.cra_requirement_guidance import get_guidance
import core.cra_requirement_guidance_part2  # noqa: F401


STATUS_DISPLAY = {
    "not_started": "Not Started",
    "partial": "Partial",
    "compliant": "Compliant",
    "not_applicable": "N/A",
}

STATUS_COLORS = {
    "compliant": colors.Color(0.2, 0.7, 0.3),
    "partial": colors.Color(0.9, 0.7, 0.1),
    "not_started": colors.Color(0.6, 0.6, 0.6),
    "not_applicable": colors.Color(0.5, 0.5, 0.5),
}

CLASSIFICATION_DISPLAY = {
    "default": "Default",
    "class_i": "Important Class I",
    "class_ii": "Important Class II",
    "critical": "Critical",
}

PRIORITY_COLORS = {
    "Critical": colors.Color(0.86, 0.15, 0.15),
    "High": colors.Color(0.96, 0.62, 0.04),
    "Medium": colors.Color(0.3, 0.5, 0.9),
    "Low": colors.Color(0.4, 0.7, 0.4),
}


def _build_status_table(
    req_statuses: List[CraRequirementStatusRecord],
    styles,
) -> List:
    """Build the main requirement status table."""
    story: List = []
    table_data = [["ID", "Requirement", "Status", "Priority", "Effort", "Owner"]]
    for rs in req_statuses:
        req_def = get_requirement_by_id(rs.requirement_id)
        guidance = get_guidance(rs.requirement_id)
        table_data.append([
            rs.requirement_id,
            Paragraph(
                f"<b>{req_def['name'] if req_def else '—'}</b>",
                styles["Normal"],
            ),
            STATUS_DISPLAY.get(rs.status, rs.status),
            guidance.priority if guidance else "—",
            guidance.effort_estimate if guidance else "—",
            rs.owner or "—",
        ])
    req_table = Table(
        table_data,
        colWidths=[0.5 * inch, 2.0 * inch, 0.7 * inch, 0.6 * inch, 1.2 * inch, 0.7 * inch],
    )
    table_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 1), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.96, 0.96, 0.96)]),
    ]
    for row_idx, rs in enumerate(req_statuses, start=1):
        status_color = STATUS_COLORS.get(rs.status, colors.grey)
        table_styles.append(("TEXTCOLOR", (2, row_idx), (2, row_idx), status_color))
        guidance = get_guidance(rs.requirement_id)
        if guidance:
            p_color = PRIORITY_COLORS.get(guidance.priority, colors.grey)
            table_styles.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), p_color))
    req_table.setStyle(TableStyle(table_styles))
    story.append(req_table)
    story.append(Spacer(1, 15))
    return story


def _build_gap_details(
    req_statuses: List[CraRequirementStatusRecord],
    styles,
) -> List:
    """Build per-gap detail paragraphs with guidance and remediation."""
    story: List = []
    gaps = [rs for rs in req_statuses if rs.status not in ("compliant", "not_applicable")]
    if not gaps:
        story.append(Paragraph(
            "<b>No open gaps.</b> All requirements are compliant or not applicable.",
            styles["Normal"],
        ))
        return story
    try:
        sub_heading = styles["Heading3"]
    except KeyError:
        sub_heading = styles["Normal"]
    story.append(Paragraph("Gap Details and Remediation Plan", sub_heading))
    story.append(Spacer(1, 6))
    total_effort = 0
    for rs in gaps:
        req_def = get_requirement_by_id(rs.requirement_id) or {}
        guidance = get_guidance(rs.requirement_id)
        name = req_def.get("name", rs.requirement_id)
        priority_label = guidance.priority if guidance else "—"
        story.append(Paragraph(
            f"<b>{rs.requirement_id} — {name}</b> "
            f"[{STATUS_DISPLAY.get(rs.status, rs.status)}] "
            f"Priority: <b>{priority_label}</b>",
            styles["Normal"],
        ))
        if guidance:
            story.append(Paragraph(
                f"<i>Deadline: {guidance.deadline_note}</i>",
                styles["Normal"],
            ))
            story.append(Spacer(1, 3))
            if guidance.common_gaps:
                gaps_text = " | ".join(guidance.common_gaps[:3])
                story.append(Paragraph(
                    f"<b>Common gaps:</b> {gaps_text}",
                    styles["Normal"],
                ))
            if guidance.remediation_actions:
                actions_text = ""
                for i, a in enumerate(guidance.remediation_actions, 1):
                    actions_text += f"{i}. {a.action} ({a.owner_hint}, {a.effort_days}d)  "
                    total_effort += a.effort_days
                story.append(Paragraph(
                    f"<b>Remediation:</b> {actions_text}",
                    styles["Normal"],
                ))
            if guidance.effort_estimate:
                story.append(Paragraph(
                    f"<b>Effort:</b> {guidance.effort_estimate}",
                    styles["Normal"],
                ))
            if guidance.mapped_standards:
                story.append(Paragraph(
                    f"<b>Standards:</b> {', '.join(guidance.mapped_standards)}",
                    styles["Normal"],
                ))
        story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"<b>Total estimated remediation effort: ~{total_effort} person-days</b>",
        styles["Normal"],
    ))
    story.append(Spacer(1, 15))
    return story


def build_cra_compliance_section(
    db: Session,
    product_id: str,
    styles,
) -> List:
    """Build CRA compliance section for a PDF report."""
    story: List = []
    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]
    assessment: Optional[CraAssessment] = db.query(CraAssessment).filter(
        CraAssessment.product_id == product_id,
    ).first()
    story.append(Paragraph("EU Cyber Resilience Act (CRA) Compliance", heading_style))
    if not assessment:
        story.append(Paragraph(
            "No CRA assessment has been created for this product.",
            styles["Normal"],
        ))
        story.append(Spacer(1, 20))
        return story
    classification_label = CLASSIFICATION_DISPLAY.get(
        assessment.classification or "", "Not classified"
    )
    summary_text = (
        f"Classification: <b>{classification_label}</b> | "
        f"Compliance: <b>{assessment.overall_compliance_pct}%</b> | "
        f"Deadline: <b>{assessment.compliance_deadline or 'TBD'}</b> | "
        f"Status: <b>{assessment.status.replace('_', ' ').title()}</b>"
    )
    story.append(Paragraph(summary_text, styles["Normal"]))
    story.append(Spacer(1, 10))
    req_statuses: List[CraRequirementStatusRecord] = (
        db.query(CraRequirementStatusRecord)
        .filter(CraRequirementStatusRecord.assessment_id == assessment.id)
        .order_by(CraRequirementStatusRecord.requirement_id)
        .all()
    )
    if not req_statuses:
        story.append(Paragraph("No requirement statuses recorded.", styles["Normal"]))
        story.append(Spacer(1, 20))
        return story
    story.extend(_build_status_table(req_statuses, styles))
    story.extend(_build_gap_details(req_statuses, styles))
    return story
