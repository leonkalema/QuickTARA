"""
Damage Scenarios section builder for reports.
"""
from typing import List, Dict, Any
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch


def calculate_overall_sfop(scenario: Dict[str, Any]) -> str:
    """Calculate overall SFOP rating from individual impact levels."""
    impact_levels = {'negligible': 0, 'moderate': 1, 'major': 2, 'severe': 3}
    
    safety = (scenario.get('safety_impact') or 'negligible').lower()
    financial = (scenario.get('financial_impact') or 'negligible').lower()
    operational = (scenario.get('operational_impact') or 'negligible').lower()
    privacy = (scenario.get('privacy_impact') or 'negligible').lower()
    
    max_impact = max(
        impact_levels.get(safety, 0),
        impact_levels.get(financial, 0),
        impact_levels.get(operational, 0),
        impact_levels.get(privacy, 0)
    )
    
    return ['Negligible', 'Moderate', 'Major', 'Severe'][max_impact]


def build_damage_scenarios_section(damage_scenarios: List[Dict[str, Any]], styles) -> List:
    """Build the damage scenarios section with ID, Name, and SFOP Rating."""
    story = []
    
    if not damage_scenarios:
        story.append(Paragraph("No damage scenarios found.", styles['Normal']))
        return story
    
    # Section header style: prefer custom heading, fallback to Heading2
    try:
        heading_style = styles['CustomHeading']
    except KeyError:
        heading_style = styles['Heading2']
    story.append(Paragraph("Damage Scenarios Analysis", heading_style))
    story.append(Paragraph(f"Total damage scenarios identified: {len(damage_scenarios)}", styles['Normal']))
    story.append(Spacer(1, 6))
    
    # Build table data
    table_data = [['ID', 'Name', 'SFOP Rating']]
    
    for scenario in damage_scenarios:
        scenario_id = scenario.get('scenario_id', 'N/A')
        name = scenario.get('name', 'N/A')
        overall_sfop = calculate_overall_sfop(scenario)
        
        # Truncate long text
        if name and len(str(name)) > 35:
            name = str(name)[:32] + "..."
        if scenario_id and len(str(scenario_id)) > 12:
            scenario_id = str(scenario_id)[:9] + "..."
        
        table_data.append([scenario_id, name, overall_sfop])
    
    # Create and style table
    table = Table(table_data, colWidths=[1.5*inch, 3.5*inch, 1.5*inch])
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
