"""
Main report builder that orchestrates all sections.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any

from .data_access import (
    get_scope_info, 
    get_damage_scenarios, 
    get_risk_treatments, 
    get_threat_scenarios,
    get_assets
)
from .sections.damage_section import build_damage_scenarios_section
from .sections.assets_section import build_assets_section
from .sections.goals_section import select_approved_goals, build_goals_section
from .sections.compliance_section import build_compliance_section
from .pdf_renderer import render_pdf, create_styles


def build_complete_report(scope_id: str, db: Session) -> bytes:
    """Build complete TARA report with all sections."""
    
    # Fetch all data
    scope_info = get_scope_info(scope_id, db)
    if not scope_info:
        raise ValueError(f"Scope {scope_id} not found")
    
    damage_scenarios = get_damage_scenarios(scope_id, db)
    risk_treatments = get_risk_treatments(scope_id, db)
    threat_scenarios = get_threat_scenarios(scope_id, db)
    assets = get_assets(scope_id, db)
    
    # Create styles
    styles = create_styles()
    
    # Build sections
    sections = []
    
    # Compliance section
    sections.append(build_compliance_section(styles))

    # Assets section (ID, Name, Description)
    sections.append(build_assets_section(assets, styles))
    
    # Damage scenarios section
    sections.append(build_damage_scenarios_section(damage_scenarios, styles))
    
    # Cybersecurity goals section
    approved_goals = select_approved_goals(damage_scenarios, risk_treatments)
    sections.append(build_goals_section(approved_goals, styles))
    
    # Render PDF
    return render_pdf(scope_info, sections)


def get_goals_data(scope_id: str, db: Session) -> Dict[str, Any]:
    """Get cybersecurity goals data for JSON API."""
    
    damage_scenarios = get_damage_scenarios(scope_id, db)
    risk_treatments = get_risk_treatments(scope_id, db)
    
    approved_goals = select_approved_goals(damage_scenarios, risk_treatments)
    
    goals_list = []
    for i, goal in enumerate(approved_goals):
        goals_list.append({
            "goal_id": f"CG{i+1:03d}",
            "goal": goal.get('goal_text', 'No goal specified'),
            "scenario_id": goal.get('scenario_id'),
            "scenario_name": goal.get('scenario_name'),
            "risk_level": goal.get('risk_level')
        })
    
    return {
        "goals": goals_list,
        "total_count": len(goals_list),
        "scope_id": scope_id
    }


def get_damage_scenarios_data(scope_id: str, db: Session) -> Dict[str, Any]:
    """Get damage scenarios data for JSON API."""
    
    damage_scenarios = get_damage_scenarios(scope_id, db)
    
    from .sections.damage_section import calculate_overall_sfop
    
    scenarios_list = []
    for scenario in damage_scenarios:
        scenarios_list.append({
            "scenario_id": scenario.get('scenario_id'),
            "name": scenario.get('name'),
            "description": scenario.get('description'),
            "overall_sfop": calculate_overall_sfop(scenario),
            "severity": scenario.get('severity'),
            "safety_impact": scenario.get('safety_impact'),
            "financial_impact": scenario.get('financial_impact'),
            "operational_impact": scenario.get('operational_impact'),
            "privacy_impact": scenario.get('privacy_impact')
        })
    
    return {
        "damage_scenarios": scenarios_list,
        "total_count": len(scenarios_list),
        "scope_id": scope_id
    }
