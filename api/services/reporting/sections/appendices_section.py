"""
Appendices placeholder — lists what detail is available in the full technical report.
"""
from typing import List
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def build_appendices_section(styles) -> List:
    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]

    appendices = [
        ("Appendix A", "Detailed Threat Scenario List",     "Full threat scenario table with MITRE technique IDs, attack vectors, and damage linkage. Available in the Internal Technical Report."),
        ("Appendix B", "Detailed Attack Path Analysis",     "Full attack path steps, preconditions, and feasibility scoring. Available in the Internal Technical Report."),
        ("Appendix C", "Complete Risk Register",            "Full risk register including all feasibility scoring details and treatment rationale. Available in the Internal Technical Report."),
        ("Appendix D", "Feasibility Scoring Method",        "Detailed description of the attack feasibility rating method per ISO/SAE 21434 §15.5: elapsed time, expertise, knowledge, window, equipment."),
        ("Appendix E", "Definitions and Abbreviations",     "ASIL — Automotive Safety Integrity Level | CIA — Confidentiality, Integrity, Availability | SFOP — Safety, Financial, Operational, Privacy | STRIDE — Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege | TARA — Threat Analysis and Risk Assessment | UDS — Unified Diagnostic Services"),
    ]

    header = [
        Paragraph("<b>Appendix</b>", styles["Normal"]),
        Paragraph("<b>Title</b>", styles["Normal"]),
        Paragraph("<b>Contents / Availability</b>", styles["Normal"]),
    ]
    rows = [header]
    for ref, title, desc in appendices:
        rows.append([
            Paragraph(ref, styles["Normal"]),
            Paragraph(title, styles["Normal"]),
            Paragraph(desc, styles["Normal"]),
        ])

    table = Table(rows, colWidths=[0.9*inch, 1.8*inch, 3.8*inch], repeatRows=1, splitByRow=True)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    story: List = [
        Paragraph("Appendices", heading_style),
        Spacer(1, 6),
        Paragraph(
            "The following appendices contain supplementary detail. "
            "Appendices A–C are available in the Internal Technical Report; "
            "they are excluded from this customer/auditor summary to protect "
            "sensitive design and security information.",
            styles["Normal"],
        ),
        Spacer(1, 8),
        table,
        Spacer(1, 12),
    ]
    return story
