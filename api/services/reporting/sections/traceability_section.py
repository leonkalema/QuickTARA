"""
Traceability presentation optimized for narrow pages.
Renders per-damage-scenario blocks rather than one very wide matrix.
Each block shows:
  - Assets linked to the scenario
  - Threats linked to the scenario
  - Risk Treatments (status and risk level)
  - Cybersecurity Goals (from treatments)
"""
from typing import List, Dict, Any
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch


def _join_bullets(items: List[str], styles) -> Paragraph:
    if not items:
        return Paragraph("", styles['Normal'])
    text = "<br/>".join([f"• {str(i)}" for i in items if str(i)])
    return Paragraph(text, styles['Normal'])


def build_traceability_section(
    assets: List[Dict[str, Any]],
    damage_scenarios: List[Dict[str, Any]],
    threat_scenarios: List[Dict[str, Any]],
    asset_damage_links: List[Dict[str, Any]],
    threat_damage_links: List[Dict[str, Any]],
    risk_treatments: List[Dict[str, Any]],
    styles,
) -> List:
    story = []

    # Section header style: prefer custom heading, fallback to Heading2
    try:
        heading_style = styles['CustomHeading']
    except KeyError:
        heading_style = styles['Heading2']

    story.append(Paragraph("Traceability (by Damage Scenario)", heading_style))
    story.append(Paragraph("Asset → Damage → Threat → Risk → Treatment → Goal", styles['Normal']))
    story.append(Spacer(1, 8))

    # Lookups
    asset_by_id = {a.get('asset_id'): a for a in assets}
    threat_by_id = {t.get('threat_scenario_id'): t for t in threat_scenarios}

    # scenario_id -> list
    assets_per_ds: Dict[str, List[str]] = {}
    for link in asset_damage_links:
        assets_per_ds.setdefault(link['scenario_id'], []).append(link['asset_id'])

    threats_per_ds: Dict[str, List[str]] = {}
    for link in threat_damage_links:
        threats_per_ds.setdefault(link['scenario_id'], []).append(link['threat_scenario_id'])

    treatments_per_ds: Dict[str, List[Dict[str, Any]]] = {}
    for rt in risk_treatments:
        sid = rt.get('damage_scenario_id')
        if sid:
            treatments_per_ds.setdefault(sid, []).append(rt)

    # Per-scenario blocks
    for ds in damage_scenarios:
        ds_id = ds.get('scenario_id')
        ds_name = ds.get('name', '')

        # Collect lists
        asset_names = [asset_by_id.get(aid, {}).get('name') for aid in assets_per_ds.get(ds_id, [])]
        asset_names = [a for a in asset_names if a]

        threat_names = [threat_by_id.get(tid, {}).get('name') for tid in threats_per_ds.get(ds_id, [])]
        threat_names = [t for t in threat_names if t]

        treatments = treatments_per_ds.get(ds_id, [])
        approved = [rt for rt in treatments if (rt.get('treatment_status') or '').strip().lower() == 'approved']
        chosen = approved or treatments

        risk_lines = []
        treat_lines = []
        goal_lines = []
        for tr in chosen:
            risk_lines.append(str(tr.get('risk_level') or ''))
            treat_lines.append(str(tr.get('selected_treatment') or ''))
            goal_lines.append(str(tr.get('treatment_goal') or ''))

        # Build a compact two-column table for this DS
        header_p = Paragraph(f"<b>{ds_id}</b>: {ds_name}", styles['Normal'])

        rows = [
            [Paragraph('<b>Assets</b>', styles['Normal']), _join_bullets(asset_names, styles)],
            [Paragraph('<b>Threats</b>', styles['Normal']), _join_bullets(threat_names, styles)],
            [Paragraph('<b>Risk Level</b>', styles['Normal']), _join_bullets(risk_lines, styles)],
            [Paragraph('<b>Treatment</b>', styles['Normal']), _join_bullets(treat_lines, styles)],
            [Paragraph('<b>Goal</b>', styles['Normal']), _join_bullets(goal_lines, styles)],
        ]

        # Title row (single row spanning two columns)
        t = Table([[header_p]], colWidths=[6.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t)

        block = Table(rows, colWidths=[1.2*inch, 5.3*inch])
        block.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(block)
        story.append(Spacer(1, 12))

    return story
