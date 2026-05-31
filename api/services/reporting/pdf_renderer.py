"""
Clean PDF renderer for TARA reports.
"""
from datetime import datetime
from io import BytesIO
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os

from api.models.report_config import ReportConfig


def build_document_control_lines(config: Optional[ReportConfig]) -> List[str]:
    """Build the document-control label lines from a report config.

    Pure (no reportlab) so it is straightforward to unit test. Only includes
    metadata fields that are present, but always includes the classification.
    """
    if config is None:
        return []
    lines: List[str] = [f"Classification: {config.classification.value.title()}"]
    meta = config.metadata
    if meta.author:
        lines.append(f"Author: {meta.author}")
    if meta.approver:
        lines.append(f"Approver: {meta.approver}")
    if meta.reference:
        lines.append(f"Reference: {meta.reference}")
    return lines


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


def build_document_header(
    scope_info: Dict[str, Any],
    styles,
    config: Optional[ReportConfig] = None,
) -> List:
    """Build the document header with product information."""
    story = []
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    version = f"v{scope_info.get('version', '1.0')}"
    # Prefer org from DB via scope_info; fallback to env; else Unknown
    org_name = scope_info.get('organization_name') or os.environ.get("QUICKTARA_ORG_NAME", "Unknown Organization")
    tool_name = "QuickTARA"
    generated_by = scope_info.get('created_by') or os.environ.get("QUICKTARA_GENERATED_BY")
    
    # Title
    story.append(Paragraph("Threat Analysis and Risk Assessment (TARA)", styles['CustomTitle']))
    story.append(Spacer(1, 10))
    
    # Product information
    story.append(Paragraph(f"<b>Product:</b> {scope_info.get('name', 'Unknown Product')}", styles['ProductInfo']))
    story.append(Paragraph(f"<b>Organization:</b> {org_name} | <b>Tool:</b> {tool_name}", styles['ProductInfo']))
    story.append(Paragraph(f"<b>Generated:</b> {current_date}{f' | <b>By:</b> {generated_by}' if generated_by else ''}", styles['ProductInfo']))
    story.append(Paragraph(f"<b>Document Version:</b> {version}", styles['ProductInfo']))
    story.append(Paragraph(f"<b>Product Type:</b> {scope_info.get('product_type', 'N/A')} | <b>Safety Level:</b> {scope_info.get('safety_level', 'N/A')}", styles['ProductInfo']))
    
    if scope_info.get('description'):
        story.append(Paragraph(f"<b>Description:</b> {scope_info['description']}", styles['ProductInfo']))

    # Document-control block (classification, author, approver, reference)
    for line in build_document_control_lines(config):
        label, _, value = line.partition(": ")
        story.append(Paragraph(f"<b>{label}:</b> {value}", styles['ProductInfo']))

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
    sections: List[List],  # List of section story elements
    config: Optional[ReportConfig] = None,
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
    story.extend(build_document_header(scope_info, styles, config))
    
    # Add all sections
    for section in sections:
        story.extend(section)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer.getvalue()
