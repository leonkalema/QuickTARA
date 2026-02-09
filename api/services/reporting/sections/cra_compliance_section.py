"""
CRA Compliance report section builder for PDF reports.

Generates a table showing CRA requirement statuses for a product assessment.

Depends on: db.cra_models, core.cra_auto_mapper
Used by: api/services/reporting/ (main report builder)
"""
from typing import List, Optional
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from sqlalchemy.orm import Session

from db.cra_models import CraAssessment, CraRequirementStatusRecord
from core.cra_auto_mapper import get_requirement_by_id


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

    # Summary paragraph
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

    # Requirements table
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

    table_data = [["ID", "Requirement", "Article", "Status", "Owner", "Auto"]]
    for rs in req_statuses:
        req_def = get_requirement_by_id(rs.requirement_id)
        table_data.append([
            rs.requirement_id,
            req_def["name"] if req_def else "—",
            req_def["article"] if req_def else "—",
            STATUS_DISPLAY.get(rs.status, rs.status),
            rs.owner or "—",
            "Yes" if rs.auto_mapped else "—",
        ])

    req_table = Table(
        table_data,
        colWidths=[0.6 * inch, 2.2 * inch, 0.7 * inch, 0.8 * inch, 0.9 * inch, 0.4 * inch],
    )

    # Build row-level styles for status coloring
    table_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 1), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
    ]

    for row_idx, rs in enumerate(req_statuses, start=1):
        status_color = STATUS_COLORS.get(rs.status, colors.grey)
        table_styles.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), status_color))

    req_table.setStyle(TableStyle(table_styles))
    story.append(req_table)
    story.append(Spacer(1, 20))

    return story
