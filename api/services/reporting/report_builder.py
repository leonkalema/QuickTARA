"""
Main report builder that orchestrates all sections.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from api.models.report_config import (
    ReportAudience,
    ReportConfig,
    ReportDetailLevel,
    SectionKey,
)
from .presets import default_config_for_audience
from .data_access import (
    get_scope_info, 
    get_damage_scenarios, 
    get_risk_treatments, 
    get_threat_scenarios,
    get_assets,
    get_asset_damage_links,
    get_threat_damage_links,
    get_attack_paths,
    has_cra_assessment,
)
from .sections.damage_section import build_damage_scenarios_section
from .sections.assets_section import build_assets_section
from .sections.goals_section import select_approved_goals, build_goals_section
from .sections.compliance_section import build_compliance_section
from .sections.cra_compliance_section import build_cra_compliance_section
from .sections.risk_summary_section import build_risk_summary_section
from .sections.traceability_section import build_traceability_section
from .sections.executive_summary_section import build_executive_summary_section
from .sections.threat_scenarios_section import build_threat_scenarios_section
from .sections.attack_paths_section import build_attack_paths_section
from .pdf_renderer import render_pdf, create_styles


def resolve_sections(
    config: ReportConfig,
    scope_id: str,
    db: Session,
) -> List[SectionKey]:
    """Resolve which body sections actually render for this config.

    Applies the CRA rule: the CRA section is omitted entirely when no CRA
    assessment exists for the product, even if the config enabled it.
    """
    enabled = config.enabled_sections()
    if SectionKey.CRA_COMPLIANCE in enabled and not has_cra_assessment(scope_id, db):
        enabled = [key for key in enabled if key != SectionKey.CRA_COMPLIANCE]
    return enabled


def _build_section(
    key: SectionKey,
    scope_id: str,
    db: Session,
    styles,
    config: ReportConfig,
) -> List:
    """Build a single body section's story for the given key."""
    if key == SectionKey.EXECUTIVE_SUMMARY:
        return build_executive_summary_section(
            get_assets(scope_id, db),
            get_damage_scenarios(scope_id, db),
            get_threat_scenarios(scope_id, db),
            get_risk_treatments(scope_id, db),
            styles,
        )
    if key == SectionKey.ISO_COMPLIANCE:
        return build_compliance_section(styles)
    if key == SectionKey.CRA_COMPLIANCE:
        return build_cra_compliance_section(db, scope_id, styles)
    if key == SectionKey.RISK_SUMMARY:
        return build_risk_summary_section(
            get_damage_scenarios(scope_id, db),
            get_risk_treatments(scope_id, db),
            styles,
        )
    if key == SectionKey.ASSET_INVENTORY:
        return build_assets_section(get_assets(scope_id, db), styles)
    if key == SectionKey.DAMAGE_SCENARIOS:
        return build_damage_scenarios_section(get_damage_scenarios(scope_id, db), styles)
    if key == SectionKey.THREAT_SCENARIOS:
        return build_threat_scenarios_section(
            get_threat_scenarios(scope_id, db),
            get_damage_scenarios(scope_id, db),
            get_threat_damage_links(scope_id, db),
            styles,
        )
    if key == SectionKey.ATTACK_PATHS:
        include_steps = config.detail_level == ReportDetailLevel.FULL
        return build_attack_paths_section(
            get_attack_paths(scope_id, db),
            styles,
            include_steps=include_steps,
        )
    if key == SectionKey.CYBERSECURITY_GOALS:
        approved_goals = select_approved_goals(
            get_damage_scenarios(scope_id, db),
            get_risk_treatments(scope_id, db),
        )
        return build_goals_section(approved_goals, styles)
    if key == SectionKey.TRACEABILITY:
        return build_traceability_section(
            get_assets(scope_id, db),
            get_damage_scenarios(scope_id, db),
            get_threat_scenarios(scope_id, db),
            get_asset_damage_links(scope_id, db),
            get_threat_damage_links(scope_id, db),
            get_risk_treatments(scope_id, db),
            styles,
        )
    # DOCUMENT_CONTROL is rendered in the PDF header, not as a body section.
    return []


def build_complete_report(
    scope_id: str,
    db: Session,
    config: Optional[ReportConfig] = None,
) -> bytes:
    """Build a TARA report.

    When no config is supplied, defaults to the Internal/Full profile to
    preserve the previous behaviour of this function.
    """
    scope_info = get_scope_info(scope_id, db)
    if not scope_info:
        raise ValueError(f"Scope {scope_id} not found")

    if config is None:
        config = default_config_for_audience(ReportAudience.INTERNAL)

    styles = create_styles()

    sections: List[List] = []
    for key in resolve_sections(config, scope_id, db):
        story = _build_section(key, scope_id, db, styles, config)
        if story:
            sections.append(story)

    return render_pdf(scope_info, sections, config)


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
