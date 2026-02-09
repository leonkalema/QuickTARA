"""
ISO 21434 Compliance section builder for reports.
Uses dynamic clause mappings from core.iso21434_mapping.
"""
from typing import List
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from core.iso21434_mapping import get_all_mappings


def build_compliance_section(styles) -> List:
    """Build ISO 21434 compliance statement section."""
    story = []
    try:
        heading_style = styles['CustomHeading']
    except KeyError:
        heading_style = styles['Heading2']
    story.append(Paragraph("ISO/SAE 21434:2021 Compliance Statement", heading_style))
    story.append(Paragraph(
        "This TARA report fulfills the following ISO/SAE 21434:2021 requirements:",
        styles['Normal'],
    ))
    story.append(Spacer(1, 6))
    compliance_data = [['Work Product', 'Clause', 'Requirement', 'Artifact Type']]
    seen: set[str] = set()
    for artifact_type, clauses in get_all_mappings().items():
        label = artifact_type.replace("_", " ").title()
        for c in clauses:
            key = f"{c['work_product']}:{c['clause_id']}"
            if key in seen:
                continue
            seen.add(key)
            compliance_data.append([
                c["work_product"],
                f"§{c['clause_id']}",
                c["clause_title"],
                label,
            ])
    compliance_table = Table(
        compliance_data,
        colWidths=[0.8 * inch, 0.7 * inch, 2.0 * inch, 2.5 * inch],
    )
    compliance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    story.append(compliance_table)
    story.append(Spacer(1, 20))
    return story
