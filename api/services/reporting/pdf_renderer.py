"""
Clean PDF renderer for TARA reports.
"""
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def create_styles():
    """Create consistent styles for the report."""
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        'CustomTitle', 
        parent=styles['Heading1'], 
        fontSize=20, 
        spaceAfter=30, 
        alignment=1,  # Center
        textColor=colors.darkblue
    ))
    
    styles.add(ParagraphStyle(
        'CustomHeading', 
        parent=styles['Heading2'], 
        fontSize=14, 
        spaceAfter=12,
        textColor=colors.darkblue
    ))
    
    styles.add(ParagraphStyle(
        'ProductInfo',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        textColor=colors.black
    ))
    
    return styles


def build_document_header(scope_info: Dict[str, Any], styles) -> List:
    """Build the document header with product information."""
    story = []
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    version = f"v{scope_info.get('version', '1.0')}"
    
    # Title
    story.append(Paragraph("Threat Analysis and Risk Assessment (TARA)", styles['CustomTitle']))
    story.append(Spacer(1, 10))
    
    # Product information
    story.append(Paragraph(f"<b>Product:</b> {scope_info.get('name', 'Unknown Product')}", styles['ProductInfo']))
    story.append(Paragraph(f"<b>Document Version:</b> {version} | <b>Generated:</b> {current_date}", styles['ProductInfo']))
    story.append(Paragraph(f"<b>Product Type:</b> {scope_info.get('product_type', 'N/A')} | <b>Safety Level:</b> {scope_info.get('safety_level', 'N/A')}", styles['ProductInfo']))
    
    if scope_info.get('description'):
        story.append(Paragraph(f"<b>Description:</b> {scope_info['description']}", styles['ProductInfo']))
    
    story.append(Spacer(1, 20))
    
    # Compliance statement
    story.append(Paragraph(
        "This document satisfies ISO/SAE 21434:2021 TARA documentation requirements for regulatory submission.",
        styles['Normal']
    ))
    story.append(Spacer(1, 30))
    
    return story


def render_pdf(
    scope_info: Dict[str, Any],
    sections: List[List]  # List of section story elements
) -> bytes:
    """Render the complete PDF report."""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=72, 
        leftMargin=72, 
        topMargin=72, 
        bottomMargin=72
    )
    
    styles = create_styles()
    story = []
    
    # Document header
    story.extend(build_document_header(scope_info, styles))
    
    # Add all sections
    for section in sections:
        story.extend(section)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer.getvalue()
