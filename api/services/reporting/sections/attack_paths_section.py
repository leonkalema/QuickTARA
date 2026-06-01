"""
Attack Paths section (WP-06/07 — Attack path analysis + feasibility,
ISO 21434 §15.5–15.6).

Lists attack paths grouped by their threat scenario, with a qualitative
feasibility label derived from the overall rating. The feasibility-label
mapping is a pure helper for testability.

``detail_level=summary`` drops the per-step detail and shows ratings only.
"""
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def feasibility_label(overall_rating: Optional[float]) -> str:
    """Map an attack-potential score to a qualitative feasibility label.

    Lower attack potential means the attack is easier, i.e. higher feasibility.
    Thresholds follow the common ISO 18045 attack-potential bands.
    """
    if overall_rating is None:
        return "Unknown"
    if overall_rating < 10:
        return "High"
    if overall_rating < 14:
        return "Medium"
    if overall_rating < 20:
        return "Low"
    return "Very Low"


def _paths_table(paths: List[Dict[str, Any]], include_steps: bool, styles) -> Table:
    if include_steps:
        header = [
            Paragraph("<b>Attack Path</b>", styles["Normal"]),
            Paragraph("<b>Steps</b>", styles["Normal"]),
            Paragraph("<b>Rating</b>", styles["Normal"]),
            Paragraph("<b>Feasibility</b>", styles["Normal"]),
        ]
        widths = [1.8 * inch, 2.7 * inch, 0.9 * inch, 1.1 * inch]
    else:
        header = [
            Paragraph("<b>Attack Path</b>", styles["Normal"]),
            Paragraph("<b>Rating</b>", styles["Normal"]),
            Paragraph("<b>Feasibility</b>", styles["Normal"]),
        ]
        widths = [3.5 * inch, 1.5 * inch, 1.5 * inch]

    table_rows = [header]
    for path in paths:
        rating = path.get("overall_rating")
        rating_text = "—" if rating is None else str(rating)
        label = feasibility_label(rating)
        if include_steps:
            steps = (path.get("attack_steps") or "").replace("\n", "<br/>")
            table_rows.append([
                Paragraph(path.get("name", ""), styles["Normal"]),
                Paragraph(steps, styles["Normal"]),
                Paragraph(rating_text, styles["Normal"]),
                Paragraph(label, styles["Normal"]),
            ])
        else:
            table_rows.append([
                Paragraph(path.get("name", ""), styles["Normal"]),
                Paragraph(rating_text, styles["Normal"]),
                Paragraph(label, styles["Normal"]),
            ])

    table = Table(table_rows, colWidths=widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    return table


def build_attack_paths_section(
    attack_paths: List[Dict[str, Any]],
    styles,
    include_steps: bool = True,
) -> List:
    """Build the attack paths flowables.

    When ``include_steps`` is False (summary detail level) the per-step text is
    omitted and only ratings/feasibility are shown.
    """
    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]

    story: List = [
        Paragraph("Attack Paths (WP-06/07 §15.5–15.6)", heading_style),
        Spacer(1, 6),
    ]

    if not attack_paths:
        story.append(Paragraph("No attack paths defined.", styles["Normal"]))
        story.append(Spacer(1, 12))
        return story

    story.append(_paths_table(attack_paths, include_steps, styles))
    story.append(Spacer(1, 20))
    return story
