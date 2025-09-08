"""
ISO 21434 Compliance section builder for reports.
"""
from typing import List
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch


def build_compliance_section(styles) -> List:
    """Build ISO 21434 compliance statement section."""
    story = []
    
    # Prefer our custom heading if available, otherwise fall back to Heading2
    try:
        heading_style = styles['CustomHeading']
    except KeyError:
        heading_style = styles['Heading2']
    story.append(Paragraph("ISO/SAE 21434:2021 Compliance Statement", heading_style))
    story.append(Paragraph("This TARA report fulfills the following ISO/SAE 21434:2021 requirements:", styles['Normal']))
    story.append(Spacer(1, 6))
    
    compliance_data = [
        ['Work Product', 'Clause', 'Requirement', 'Report Section'],
        ['WP-09', '9.4', 'Risk Assessment Report', 'Risk Assessment Summary'],
        ['WP-10', '10.4', 'Cybersecurity Goals', 'Cybersecurity Goals'],
        ['WP-09', '9.3', 'Risk Treatment Decisions', 'Risk Treatment Decisions'],
        ['WP-09', '9.2', 'Risk Determination', 'Risk Assessment Matrix'],
        ['WP-08', '8.4', 'Threat Scenarios', 'Threat Scenarios'],
        ['WP-07', '7.4', 'Damage Scenarios', 'Damage Scenarios'],
        ['WP-06', '6.4', 'Asset Identification', 'Traceability Matrix']
    ]
    
    compliance_table = Table(compliance_data, colWidths=[0.8*inch, 0.6*inch, 2.2*inch, 2.4*inch])
    compliance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(compliance_table)
    story.append(Spacer(1, 20))
    
    return story
