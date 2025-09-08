"""
Cybersecurity Goals section builder for reports.
"""
from typing import List, Dict, Any, Tuple
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch


def select_approved_goals(
    damage_scenarios: List[Dict[str, Any]], 
    risk_treatments: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Select approved Medium/High/Critical treatments as individual goals.

    One goal per approved treatment row (not per scenario). This matches UI where each
    approved treatment may carry its own goal text.
    """
    # Map scenario_id -> scenario for fallbacks
    scenario_by_id: Dict[str, Dict[str, Any]] = {
        s.get('scenario_id'): s for s in damage_scenarios if s.get('scenario_id')
    }

    qualifying_levels = {'critical', 'high', 'severe', 'major', 'medium'}
    approved_goals: List[Dict[str, Any]] = []

    for rt in risk_treatments:
        scenario_id = rt.get('damage_scenario_id')
        if not scenario_id:
            continue
        status = (rt.get('treatment_status') or '').strip().lower()
        risk_level = (rt.get('risk_level') or '').strip().lower()
        if status == 'approved' and risk_level in qualifying_levels:
            scenario = scenario_by_id.get(scenario_id, {})
            goal_text = generate_goal_text(scenario, rt)
            approved_goals.append({
                'scenario_id': scenario_id,
                'scenario_name': scenario.get('name', 'N/A'),
                'risk_level': risk_level,
                'goal_text': goal_text
            })

    return approved_goals


def generate_goal_text(scenario: Dict[str, Any], risk_treatment: Dict[str, Any]) -> str:
    """Generate cybersecurity goal text from scenario and treatment data."""
    
    # Prefer user-provided treatment_goal if present
    goal = (risk_treatment.get('treatment_goal') or '').strip()
    if goal:
        return goal
    
    # Fallback: generate from scenario name
    scenario_name = scenario.get('name', '')
    name_lower = str(scenario_name).lower()
    
    if 'data' in name_lower or 'information' in name_lower:
        return "Ensure data confidentiality and integrity through approved controls"
    elif 'access' in name_lower or 'authentication' in name_lower:
        return "Prevent unauthorized system access with approved mitigations"
    elif any(word in name_lower for word in ['communication', 'comms', 'can', 'network']):
        return "Secure communication channels with approved safeguards"
    elif 'boot' in name_lower or 'firmware' in name_lower:
        return "Ensure secure boot process and firmware integrity"
    elif 'diagnostic' in name_lower:
        return "Protect diagnostic interfaces from unauthorized access"
    else:
        return f"Mitigate {str(scenario_name)[:40]} risks with approved controls"


def build_goals_section(approved_goals: List[Dict[str, Any]], styles) -> List:
    """Build the cybersecurity goals section with Goal ID and Goal only."""
    story = []
    
    if not approved_goals:
        story.append(Paragraph("No approved cybersecurity goals found.", styles['Normal']))
        return story
    
    # Section header
    try:
        heading_style = styles['CustomHeading']
    except KeyError:
        heading_style = styles['Heading2']
    story.append(Paragraph("Cybersecurity Goals (WP-10)", heading_style))
    story.append(Paragraph(
        "ISO 21434 requires cybersecurity goals for Medium, High and Critical risks that have been approved for acceptance:", 
        styles['Normal']
    ))
    story.append(Spacer(1, 6))
    
    # Build table data - only Goal ID and Goal (wrapped)
    table_data = [['Goal ID', 'Cybersecurity Goal']]
    
    for i, goal in enumerate(approved_goals):
        goal_id = f"CG{i+1:03d}"
        goal_text = goal.get('goal_text', 'No goal specified')
        goal_para = Paragraph(str(goal_text), styles['Normal'])
        
        table_data.append([goal_id, goal_para])
    
    # Create and style table
    table = Table(table_data, colWidths=[1.0*inch, 4.2*inch])
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
