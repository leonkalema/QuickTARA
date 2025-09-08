"""
Assets section builder for reports.
"""
from typing import List, Dict, Any
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch


def build_assets_section(assets: List[Dict[str, Any]], styles) -> List:
    """Build the assets section with ID, Name, and Description."""
    story = []

    if not assets:
        story.append(Paragraph("No assets found.", styles['Normal']))
        return story

    # Section header style: prefer custom heading, fallback to Heading2
    try:
        heading_style = styles['CustomHeading']
    except KeyError:
        heading_style = styles['Heading2']

    story.append(Paragraph("Assets Overview", heading_style))
    story.append(Paragraph(f"Total assets: {len(assets)}", styles['Normal']))
    story.append(Spacer(1, 6))

    # Build table data
    table_data = [['ID', 'Name', 'Description']]

    for a in assets:
        asset_id = a.get('asset_id', 'N/A')
        name = a.get('name', 'N/A')
        desc = a.get('description', '') or ''

        # Truncate for layout
        if name and len(str(name)) > 40:
            name = str(name)[:37] + '...'
        if desc and len(str(desc)) > 70:
            desc = str(desc)[:67] + '...'

        table_data.append([asset_id, name, desc])

    # Create table
    table = Table(table_data, colWidths=[1.5*inch, 2.0*inch, 3.0*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    return story
