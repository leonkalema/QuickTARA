"""
Scope and Assumptions section — §8.3 Item Definition.
Describes product boundary, operational context, interfaces, and assumptions.
"""
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def build_scope_section(scope_info: Dict[str, Any], assets: List[Dict[str, Any]], styles) -> List:
    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]

    story: List = [
        Paragraph("Scope, Item Boundary and Assumptions (§8.3)", heading_style),
        Spacer(1, 6),
    ]

    # Product description
    desc = scope_info.get("description") or "No description provided."
    story.append(Paragraph("<b>Product Description</b>", styles["Normal"]))
    story.append(Spacer(1, 3))
    story.append(Paragraph(desc, styles["Normal"]))
    story.append(Spacer(1, 10))

    # Operational context table
    ctx_data = [
        [Paragraph("<b>Attribute</b>", styles["Normal"]), Paragraph("<b>Value</b>", styles["Normal"])],
        ["Product name", scope_info.get("name", "—")],
        ["Product type", scope_info.get("product_type", "—")],
        ["Safety level", scope_info.get("safety_level", "—")],
        ["Document version", str(scope_info.get("version", "—"))],
        ["Trust zone", scope_info.get("trust_zone", "—")],
    ]
    ctx_table = Table(ctx_data, colWidths=[2.2 * inch, 4.3 * inch])
    ctx_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    story.append(ctx_table)
    story.append(Spacer(1, 10))

    # In-scope assets
    story.append(Paragraph("<b>In-Scope Assets</b>", styles["Normal"]))
    story.append(Spacer(1, 3))
    if assets:
        asset_data = [
            [Paragraph("<b>Asset</b>", styles["Normal"]),
             Paragraph("<b>Type</b>", styles["Normal"]),
             Paragraph("<b>Security relevance</b>", styles["Normal"])],
        ]
        for a in assets:
            asset_data.append([
                a.get("name", "—"),
                a.get("asset_type", "—"),
                _security_relevance(a),
            ])
        asset_table = Table(asset_data, colWidths=[2.0 * inch, 1.5 * inch, 3.0 * inch],
                            repeatRows=1, splitByRow=True)
        asset_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(asset_table)
    else:
        story.append(Paragraph("No assets defined.", styles["Normal"]))

    story.append(Spacer(1, 10))

    # Assumptions
    story.append(Paragraph("<b>Key Assumptions</b>", styles["Normal"]))
    story.append(Spacer(1, 3))
    assumptions = [
        "This TARA covers the item boundary as described above. Components outside the boundary are considered environmental.",
        "Network and vehicle-level architecture outside the defined trust zone is assumed to provide no additional protection unless explicitly stated.",
        "Physical access to the diagnostic connector is considered a credible attack scenario unless access controls are confirmed.",
        "The assessment is based on the product specification at the time of assessment. Changes to hardware, firmware, or interfaces require reassessment.",
    ]
    for i, a in enumerate(assumptions, 1):
        story.append(Paragraph(f"{i}. {a}", styles["Normal"]))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 12))
    return story


def _security_relevance(asset: Dict[str, Any]) -> str:
    t = (asset.get("asset_type") or "").lower()
    c = asset.get("confidentiality", "")
    i = asset.get("integrity", "")
    a = asset.get("availability", "")
    parts = []
    if i in ("High",):
        parts.append("Integrity-critical")
    if c in ("High",):
        parts.append("Confidentiality-sensitive")
    if a in ("High",):
        parts.append("Availability-critical")
    if "firmware" in t or "software" in t:
        parts.append("Controls ECU behaviour")
    if "calibration" in t or "configuration" in t:
        parts.append("Safety/performance parameters")
    if "communication" in t:
        parts.append("Safety-critical input signal")
    return "; ".join(parts) if parts else "Defined in asset inventory"
