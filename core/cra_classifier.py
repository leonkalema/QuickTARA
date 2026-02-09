"""
CRA Product Classification Logic

Scores classification questionnaire answers and derives:
  - CRA category (Default / Class I / Class II / Critical)
  - Conformity assessment type
  - Compliance deadline
  - Estimated assessment cost
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


CRA_CLASSIFICATION_QUESTIONS: List[Dict[str, str]] = [
    {
        "id": "q1",
        "text": "Does the product contain a microcontroller or microprocessor?",
        "hint": "Any embedded processor counts.",
    },
    {
        "id": "q2",
        "text": "Does the product perform security-related functions?",
        "hint": "Crypto, authentication, secure boot, access control.",
    },
    {
        "id": "q3",
        "text": "Is the product designed to be tamper-resistant?",
        "hint": "Secure enclosure, tamper detection, RDP protection.",
    },
    {
        "id": "q4",
        "text": "Is the product intended for industrial or automotive use?",
        "hint": "Safety-critical or industrial deployment context.",
    },
    {
        "id": "q5",
        "text": "Does the product contain an HSM or secure cryptoprocessor?",
        "hint": "Dedicated hardware security module for key storage.",
    },
    {
        "id": "q6",
        "text": "Could the product be marketed independently (not only vehicle-integrated)?",
        "hint": "Sold to multiple OEMs or as standalone component.",
    },
]

AUTOMOTIVE_EXCEPTION_QUESTION: Dict[str, str] = {
    "id": "auto_exception",
    "text": "Is this product sold exclusively to one OEM for vehicle type-approval under UN R155?",
    "hint": "If yes, CRA may not apply (lex specialis). Compliance still recommended.",
}


@dataclass(frozen=True)
class ClassificationResult:
    """Output of the CRA classification questionnaire."""
    classification: str
    conformity_assessment: str
    compliance_deadline: str
    cost_estimate_min: int
    cost_estimate_max: int
    automotive_exception: bool
    rationale: str


def classify_product(
    answers: Dict[str, bool],
    automotive_exception: bool = False,
) -> ClassificationResult:
    """
    Score the 6-question questionnaire and return classification.

    Args:
        answers: Dict mapping question id (q1-q6) to True/False
        automotive_exception: Whether the automotive lex specialis applies
    """
    yes_count = sum(
        1 for qid in ["q1", "q2", "q3", "q4", "q5", "q6"]
        if answers.get(qid, False)
    )
    has_hsm = answers.get("q5", False)
    has_tamper = answers.get("q3", False)

    if yes_count >= 6 and has_hsm:
        classification = "critical"
        conformity = "EUCC certification required"
        deadline = "2026-10-30"
        cost_min, cost_max = 50000, 100000
        rationale = "All criteria met including HSM — Critical category"
    elif yes_count >= 4 or (has_tamper and yes_count >= 3):
        classification = "class_ii"
        conformity = "Third-party assessment mandatory"
        deadline = "2026-10-30"
        cost_min, cost_max = 20000, 50000
        rationale = (
            f"{yes_count}/6 criteria met with tamper-resistant design "
            "— Important Class II"
        )
    elif yes_count >= 2:
        classification = "class_i"
        conformity = "Internal assessment + harmonized standards"
        deadline = "2026-08-30"
        cost_min, cost_max = 5000, 20000
        rationale = (
            f"{yes_count}/6 criteria met — Important Class I"
        )
    else:
        classification = "default"
        conformity = "Self-assessment"
        deadline = "2027-12-11"
        cost_min, cost_max = 0, 5000
        rationale = (
            f"Only {yes_count}/6 criteria met — Default category"
        )

    return ClassificationResult(
        classification=classification,
        conformity_assessment=conformity,
        compliance_deadline=deadline,
        cost_estimate_min=cost_min,
        cost_estimate_max=cost_max,
        automotive_exception=automotive_exception,
        rationale=rationale,
    )
