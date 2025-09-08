"""
Risk Assessment Summary section (WP-09 9.4)
Summarizes impacts, feasibility/risk distribution, and treatment status.
"""
from typing import List, Dict, Any
from collections import Counter
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch


def _badge_table(data: Dict[str, int], styles, title: str, col1: str, col2: str, widths=None):
    rows = [[col1, col2]] + [[k, str(v)] for k, v in data.items()]
    widths = widths or [2.5*inch, 1.0*inch]
    t = Table(rows, colWidths=widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    return [Paragraph(f"<b>{title}</b>", styles['Normal']), t, Spacer(1, 8)]


def build_risk_summary_section(damage_scenarios: List[Dict[str, Any]], risk_treatments: List[Dict[str, Any]], styles) -> List:
    story = []

    # Header
    try:
        heading_style = styles['CustomHeading']
    except KeyError:
        heading_style = styles['Heading2']
    story.append(Paragraph("Risk Assessment Summary (WP-09 9.4)", heading_style))
    story.append(Spacer(1, 6))

    # 1) Damage severity distribution (SFOP overall label is in ds.severity; also individual SFOP fields exist)
    severity_counts = Counter((ds.get('severity') or 'Unknown') for ds in damage_scenarios)

    # 2) Risk distribution by risk_level from treatments
    risk_counts = Counter((rt.get('risk_level') or 'Unknown') for rt in risk_treatments)

    # 3) Treatment status distribution
    status_counts = Counter((rt.get('treatment_status') or 'draft') for rt in risk_treatments)

    # 4) Approved goals count
    approved_goals = sum(1 for rt in risk_treatments if (rt.get('treatment_status') or '').lower() == 'approved')

    # Render small summary paragraph
    story.append(Paragraph(
        f"This section summarizes the assessed damages and risk treatment decisions.", styles['Normal']
    ))
    story.append(Spacer(1, 6))

    # Render tables
    story += _badge_table(dict(severity_counts), styles, "Damage Severity (count)", "Severity", "Count")
    story += _badge_table(dict(risk_counts), styles, "Risk Levels (count)", "Risk Level", "Count")
    story += _badge_table(dict(status_counts), styles, "Treatment Status (count)", "Status", "Count")

    # Approved total
    story.append(Paragraph(f"<b>Approved Treatments:</b> {approved_goals}", styles['Normal']))
    story.append(Spacer(1, 20))

    return story
