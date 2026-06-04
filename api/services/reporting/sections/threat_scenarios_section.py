"""
Threat Scenarios section (WP-05 — Threat scenario identification, ISO 21434 §15.4).

Lists each threat scenario and the damage scenarios it can lead to. The
damage-name lookup is kept in a pure helper so it can be tested without
reportlab.
"""
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def map_threats_to_damages(
    threat_scenarios: List[Dict[str, Any]],
    damage_scenarios: List[Dict[str, Any]],
    threat_damage_links: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return per-threat rows with their linked damage-scenario names.

    Pure (no reportlab) for testability.
    """
    damage_name_by_id = {
        ds.get("scenario_id"): ds.get("name", "") for ds in damage_scenarios
    }
    damages_per_threat: Dict[str, List[str]] = {}
    for link in threat_damage_links:
        threat_id = link.get("threat_scenario_id")
        damage_name = damage_name_by_id.get(link.get("scenario_id"))
        if threat_id and damage_name:
            damages_per_threat.setdefault(threat_id, []).append(damage_name)

    rows: List[Dict[str, Any]] = []
    for threat in threat_scenarios:
        threat_id = threat.get("threat_scenario_id")
        rows.append({
            "threat_scenario_id": threat_id,
            "name": threat.get("name", ""),
            "description": threat.get("description", ""),
            "damage_names": damages_per_threat.get(threat_id, []),
        })
    return rows


_MAX_DESC_CHARS = 400  # cap MITRE descriptions that can run to 10k+ chars


def _truncate(text: str, limit: int = _MAX_DESC_CHARS) -> str:
    if not text:
        return ""
    return text[:limit].rstrip() + "…" if len(text) > limit else text


def _threats_table(rows: List[Dict[str, Any]], styles) -> Table:
    header = [
        Paragraph("<b>Threat</b>", styles["Normal"]),
        Paragraph("<b>Description</b>", styles["Normal"]),
        Paragraph("<b>Leads to (damage)</b>", styles["Normal"]),
    ]
    table_rows = [header]
    for row in rows:
        damages = "<br/>".join(f"• {name}" for name in row["damage_names"]) or "—"
        table_rows.append([
            Paragraph(row["name"], styles["Normal"]),
            Paragraph(_truncate(row["description"] or ""), styles["Normal"]),
            Paragraph(damages, styles["Normal"]),
        ])
    table = Table(
        table_rows,
        colWidths=[1.8 * inch, 2.7 * inch, 2.0 * inch],
        repeatRows=1,       # repeat header on every page
        splitByRow=True,    # allow rows to split across page breaks
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    return table


def build_threat_scenarios_section(
    threat_scenarios: List[Dict[str, Any]],
    damage_scenarios: List[Dict[str, Any]],
    threat_damage_links: List[Dict[str, Any]],
    styles,
) -> List:
    """Build the threat scenarios flowables."""
    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]

    story: List = [
        Paragraph("Threat Scenarios (WP-05 §15.4)", heading_style),
        Spacer(1, 6),
    ]

    if not threat_scenarios:
        story.append(Paragraph("No threat scenarios defined.", styles["Normal"]))
        story.append(Spacer(1, 12))
        return story

    rows = map_threats_to_damages(
        threat_scenarios, damage_scenarios, threat_damage_links
    )
    story.append(_threats_table(rows, styles))
    story.append(Spacer(1, 20))
    return story
