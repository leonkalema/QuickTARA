"""
CRA Product Classification Logic

Classifies products based on CORE FUNCTIONALITY matching official
categories from CRA Annexes III/IV and Implementing Regulation (EU)
2025/2392. Also derives conformity assessment module per CRA Article 32.

Per EU Commission FAQs v1.2 (Section 3):
- Classification depends on core functionality, not a scoring quiz.
- Integrating an important/critical component does NOT automatically
  make the host product important/critical.
- Multi-function products classified by core functionality only.

Timeline (CRA Article 71):
- 11 Sep 2026: Reporting obligations (Article 14) apply.
- 11 Dec 2027: All essential requirements apply.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

from core.cra_product_categories import (
    get_category_by_id,
    get_all_categories,
    ProductCategory,
)


# ── Conformity assessment module rules (CRA Art. 32) ──────────────

CONFORMITY_MODULES: Dict[str, Dict[str, str]] = {
    "module_a": {
        "id": "module_a",
        "name": "Module A — Self-assessment",
        "description": (
            "Manufacturer verifies compliance on sole responsibility. "
            "No notified body required."
        ),
    },
    "module_bc": {
        "id": "module_bc",
        "name": "Module B+C — EU-type examination",
        "description": (
            "Notified body examines design and development. "
            "Manufacturer declares compliance. Periodic audits required."
        ),
    },
    "module_h": {
        "id": "module_h",
        "name": "Module H — Full quality assurance",
        "description": (
            "Manufacturer implements full QC system assessed by notified "
            "body. Good for manufacturers with many product types."
        ),
    },
}


CRA_CLASSIFICATION_QUESTIONS: List[Dict[str, str]] = [
    {
        "id": "q_category",
        "text": "Select the core functionality that best matches your product.",
        "hint": (
            "Choose the category that describes the PRIMARY function of "
            "your product, not ancillary features or integrated components."
        ),
    },
    {
        "id": "q_harmonised_standard",
        "text": "Will you apply a harmonised standard for CRA compliance?",
        "hint": (
            "If a harmonised standard exists and you apply it, Class I "
            "products can use self-assessment (Module A) instead of "
            "third-party assessment."
        ),
    },
    {
        "id": "q_open_source",
        "text": "Is this a free and open-source product with public technical documentation?",
        "hint": (
            "Class I/II open-source products with public tech docs can "
            "use Module A per CRA Article 32(5)."
        ),
    },
]

AUTOMOTIVE_EXCEPTION_QUESTION: Dict[str, str] = {
    "id": "auto_exception",
    "text": (
        "Is this product sold exclusively to one OEM for vehicle "
        "type-approval under UN R155?"
    ),
    "hint": (
        "If yes, CRA may not apply (lex specialis). Compliance still "
        "recommended."
    ),
}


@dataclass(frozen=True)
class ConformityModule:
    """Recommended conformity assessment module with rationale."""
    module_id: str
    name: str
    description: str
    mandatory: bool
    alternatives: List[str]
    rationale: str


@dataclass(frozen=True)
class ClassificationResult:
    """Output of the CRA product classification."""
    classification: str
    category_id: Optional[str]
    category_name: str
    conformity_assessment: str
    conformity_module: ConformityModule
    compliance_deadline: str
    reporting_deadline: str
    cost_estimate_min: int
    cost_estimate_max: int
    automotive_exception: bool
    rationale: str


def _build_conformity_module(
    classification: str,
    uses_harmonised_standard: bool,
    is_open_source_public: bool,
) -> ConformityModule:
    """Determine the correct conformity assessment module per Art. 32."""
    if classification == "default":
        return ConformityModule(
            module_id="module_a",
            name="Module A — Self-assessment",
            description=CONFORMITY_MODULES["module_a"]["description"],
            mandatory=False,
            alternatives=["module_bc", "module_h"],
            rationale=(
                "Default category products can always use Module A "
                "(self-assessment). Third-party assessment is optional."
            ),
        )
    if classification == "class_i":
        if is_open_source_public:
            return ConformityModule(
                module_id="module_a",
                name="Module A — Self-assessment (open-source exception)",
                description=CONFORMITY_MODULES["module_a"]["description"],
                mandatory=False,
                alternatives=["module_bc", "module_h"],
                rationale=(
                    "Class I free/open-source products with public technical "
                    "documentation can use Module A per Article 32(5)."
                ),
            )
        if uses_harmonised_standard:
            return ConformityModule(
                module_id="module_a",
                name="Module A — Self-assessment (with harmonised standard)",
                description=CONFORMITY_MODULES["module_a"]["description"],
                mandatory=False,
                alternatives=["module_bc", "module_h"],
                rationale=(
                    "Class I products applying a harmonised standard can "
                    "use Module A per Article 32(2)."
                ),
            )
        return ConformityModule(
            module_id="module_bc",
            name="Module B+C — EU-type examination (mandatory)",
            description=CONFORMITY_MODULES["module_bc"]["description"],
            mandatory=True,
            alternatives=["module_h"],
            rationale=(
                "Class I products WITHOUT a harmonised standard must use "
                "Module B+C or Module H (notified body required)."
            ),
        )
    if classification == "class_ii":
        if is_open_source_public:
            return ConformityModule(
                module_id="module_a",
                name="Module A — Self-assessment (open-source exception)",
                description=CONFORMITY_MODULES["module_a"]["description"],
                mandatory=False,
                alternatives=["module_bc", "module_h"],
                rationale=(
                    "Class II free/open-source products with public technical "
                    "documentation can use Module A per Article 32(5)."
                ),
            )
        return ConformityModule(
            module_id="module_bc",
            name="Module B+C or H — Third-party assessment (mandatory)",
            description=CONFORMITY_MODULES["module_bc"]["description"],
            mandatory=True,
            alternatives=["module_h"],
            rationale=(
                "Class II products require Module B+C or Module H "
                "(notified body mandatory)."
            ),
        )
    # critical
    return ConformityModule(
        module_id="module_bc",
        name="Module B+C or H — Third-party assessment (mandatory)",
        description=CONFORMITY_MODULES["module_bc"]["description"],
        mandatory=True,
        alternatives=["module_h"],
        rationale=(
            "Critical products require Module B+C or Module H "
            "(notified body mandatory). EUCC certification may become "
            "mandatory in future per Article 8(1)."
        ),
    )


COST_RANGES: Dict[str, tuple] = {
    "default": (0, 5_000),
    "class_i": (5_000, 20_000),
    "class_ii": (20_000, 50_000),
    "critical": (50_000, 150_000),
}

FULL_COMPLIANCE_DEADLINE = "2027-12-11"
REPORTING_DEADLINE = "2026-09-11"


def classify_product(
    answers: Dict[str, bool],
    automotive_exception: bool = False,
    category_id: Optional[str] = None,
    uses_harmonised_standard: bool = False,
    is_open_source_public: bool = False,
) -> ClassificationResult:
    """
    Classify a product based on core functionality category selection.

    Args:
        answers: Legacy dict (kept for backward compatibility).
        automotive_exception: Whether automotive lex specialis applies.
        category_id: Selected product category ID from the catalog.
        uses_harmonised_standard: Whether a harmonised standard is applied.
        is_open_source_public: Whether product is FOSS with public docs.
    """
    if category_id:
        category = get_category_by_id(category_id)
        if category:
            classification = category.classification
            category_name = category.name
            rationale = (
                f"Product core functionality matches '{category.name}' "
                f"({category.annex_ref}) — {classification.replace('_', ' ').title()}"
            )
        else:
            classification = "default"
            category_name = "Default (no matching category)"
            rationale = f"Category ID '{category_id}' not found — classified as Default."
    else:
        classification = "default"
        category_name = "Default (not listed in Annexes III/IV)"
        category_id = None
        rationale = (
            "Product core functionality does not match any important or "
            "critical product category — Default category."
        )
    conformity_module = _build_conformity_module(
        classification, uses_harmonised_standard, is_open_source_public,
    )
    cost_min, cost_max = COST_RANGES.get(classification, (0, 5_000))
    return ClassificationResult(
        classification=classification,
        category_id=category_id,
        category_name=category_name,
        conformity_assessment=conformity_module.name,
        conformity_module=conformity_module,
        compliance_deadline=FULL_COMPLIANCE_DEADLINE,
        reporting_deadline=REPORTING_DEADLINE,
        cost_estimate_min=cost_min,
        cost_estimate_max=cost_max,
        automotive_exception=automotive_exception,
        rationale=rationale,
    )
