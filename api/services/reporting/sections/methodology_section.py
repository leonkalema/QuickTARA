"""
Methodology section — describes the TARA approach per ISO/SAE 21434.
Static content; no DB data needed.
"""
from typing import List
from reportlab.platypus import Paragraph, Spacer


def build_methodology_section(styles) -> List:
    try:
        heading_style = styles["CustomHeading"]
    except KeyError:
        heading_style = styles["Heading2"]

    story: List = [
        Paragraph("Methodology", heading_style),
        Spacer(1, 6),
        Paragraph(
            "This Threat Analysis and Risk Assessment (TARA) was performed in accordance with "
            "<b>ISO/SAE 21434:2021</b> — Road Vehicles: Cybersecurity Engineering. "
            "The assessment follows the work product structure defined in Clause 15 "
            "(threat analysis and risk assessment) and Clause 14 (risk treatment).",
            styles["Normal"],
        ),
        Spacer(1, 8),
        Paragraph("<b>Damage Scenario Identification (§15.3)</b>", styles["Normal"]),
        Spacer(1, 3),
        Paragraph(
            "Assets were identified and their security properties (Confidentiality, Integrity, "
            "Availability) assessed. Damage scenarios were derived by identifying adverse "
            "consequences resulting from a compromise of each security property. Each scenario "
            "was rated using the <b>SFOP</b> impact framework: Safety, Financial, Operational, "
            "and Privacy impact levels (negligible / moderate / major / severe).",
            styles["Normal"],
        ),
        Spacer(1, 8),
        Paragraph("<b>Threat Scenario Identification (§15.4)</b>", styles["Normal"]),
        Spacer(1, 3),
        Paragraph(
            "Threat scenarios were identified by mapping assets to the <b>MITRE ATT&CK ICS</b> "
            "threat catalog, filtered by asset type and CIA dimension using STRIDE categorisation. "
            "Auto-generated candidate scenarios were reviewed and validated by the engineering team "
            "before acceptance. Manually authored scenarios were added where catalog coverage "
            "was insufficient.",
            styles["Normal"],
        ),
        Spacer(1, 8),
        Paragraph("<b>Attack Feasibility Rating (§15.5)</b>", styles["Normal"]),
        Spacer(1, 3),
        Paragraph(
            "Attack feasibility was assessed considering: elapsed time, specialist expertise "
            "required, knowledge of the item, window of opportunity, and equipment needed. "
            "Feasibility levels: <b>Low / Medium / High / Very High</b>.",
            styles["Normal"],
        ),
        Spacer(1, 8),
        Paragraph("<b>Risk Determination (§15.7)</b>", styles["Normal"]),
        Spacer(1, 3),
        Paragraph(
            "Risk was determined by combining the overall impact rating (highest SFOP dimension) "
            "with the attack feasibility rating. Risk levels: "
            "<b>Low / Medium / High / Critical</b>.",
            styles["Normal"],
        ),
        Spacer(1, 8),
        Paragraph("<b>Risk Treatment (§14)</b>", styles["Normal"]),
        Spacer(1, 3),
        Paragraph(
            "For each identified risk, a treatment decision was recorded: "
            "<b>Avoiding</b> (remove the risk source), "
            "<b>Reducing</b> (implement cybersecurity controls), "
            "<b>Sharing</b> (transfer risk to another party), or "
            "<b>Accepting</b> (accept residual risk with justification). "
            "Treatment decisions require engineering sign-off before release.",
            styles["Normal"],
        ),
        Spacer(1, 12),
    ]
    return story
