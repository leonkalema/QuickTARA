"""
CRA Annex II — User Information Requirements

Manufacturers must supply the following information to users alongside the
product (Art. 13(20) and Annex II of Regulation EU 2024/2847).

Each item is checked against the assessment's stored data where possible;
items with no stored data are flagged as action required.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class AnnexIIItem:
    """One mandatory user-information item from Annex II."""
    key: str
    title: str
    description: str
    article_ref: str
    auto_checkable: bool  # can we derive status from assessment data?
    assessment_field: Optional[str]  # field name in CraAssessment to check


ANNEX_II_ITEMS: List[AnnexIIItem] = [
    AnnexIIItem(
        key="manufacturer_contact",
        title="Manufacturer name, registered trade name, and contact address",
        description=(
            "Full legal name of the manufacturer, any registered trade name or trademark, "
            "and a postal or email address where the manufacturer can be reached."
        ),
        article_ref="Annex II §1",
        auto_checkable=False,
        assessment_field=None,
    ),
    AnnexIIItem(
        key="product_identification",
        title="Product name, type, batch or serial number",
        description=(
            "Clear identification of the product: name, type designation, and a "
            "batch or serial number that allows individual units to be identified."
        ),
        article_ref="Annex II §2",
        auto_checkable=False,
        assessment_field=None,
    ),
    AnnexIIItem(
        key="intended_purpose",
        title="Intended purpose of the product",
        description=(
            "A plain-language description of what the product is designed to do, "
            "including the environment it is intended for and any foreseeable misuse "
            "the manufacturer has considered."
        ),
        article_ref="Annex II §3",
        auto_checkable=False,
        assessment_field=None,
    ),
    AnnexIIItem(
        key="security_properties",
        title="Essential cybersecurity properties and how to use them securely",
        description=(
            "Instructions for secure use: default credentials to change, "
            "network hardening steps, secure configuration guidance, and any "
            "known security properties that require user action to activate."
        ),
        article_ref="Annex II §4",
        auto_checkable=False,
        assessment_field=None,
    ),
    AnnexIIItem(
        key="support_period",
        title="Support period — end-of-support date",
        description=(
            "The date until which the manufacturer will provide security updates. "
            "Minimum 5 years from market placement. Must be communicated clearly, "
            "e.g. on the product page, in the manual, and on the manufacturer's website."
        ),
        article_ref="Annex II §5 / Art. 14(2)",
        auto_checkable=True,
        assessment_field="eoss_date",
    ),
    AnnexIIItem(
        key="vulnerability_reporting",
        title="How to report vulnerabilities",
        description=(
            "Contact details for reporting security vulnerabilities — typically a "
            "dedicated security email address (security@…), a web form, or a bug bounty "
            "platform. Must be easily findable and must include instructions on what "
            "information to provide."
        ),
        article_ref="Annex II §6",
        auto_checkable=False,
        assessment_field=None,
    ),
    AnnexIIItem(
        key="update_instructions",
        title="How to install security updates",
        description=(
            "Step-by-step instructions for applying security updates: OTA update "
            "procedure, manual firmware update steps, or the URL of the update portal. "
            "Includes notification mechanism so users know when an update is available."
        ),
        article_ref="Annex II §7",
        auto_checkable=False,
        assessment_field=None,
    ),
    AnnexIIItem(
        key="known_vulnerabilities",
        title="Known vulnerabilities at time of placing on market",
        description=(
            "Disclosure of any known security vulnerabilities at the time the product "
            "is placed on the market. Per Annex I Part I §1, products must be delivered "
            "without EXPLOITABLE vulnerabilities; where non-exploitable issues are "
            "known, they must be disclosed here along with any planned remediation."
        ),
        article_ref="Annex II §8 / Annex I Part I §1",
        auto_checkable=False,
        assessment_field=None,
    ),
    AnnexIIItem(
        key="eu_declaration_reference",
        title="Reference to the EU Declaration of Conformity",
        description=(
            "A statement referring users to the EU Declaration of Conformity (DoC), "
            "either the full DoC or an abbreviated form per Annex VI, including the "
            "internet address where the full DoC can be accessed."
        ),
        article_ref="Annex II §9 / Annex VI",
        auto_checkable=False,
        assessment_field=None,
    ),
]


@dataclass
class AnnexIICheckResult:
    """Status of one Annex II item for a given assessment."""
    key: str
    title: str
    article_ref: str
    description: str
    status: str  # "done" | "action_required" | "not_checked"
    auto_derived: bool
    derived_value: Optional[str]


def evaluate_annex_ii(assessment_data: dict) -> List[AnnexIICheckResult]:
    """
    Evaluate which Annex II items can be auto-confirmed from assessment data.

    assessment_data keys checked:
      - eoss_date: str (YYYY-MM-DD) → confirms support_period item if non-empty
    """
    results: List[AnnexIICheckResult] = []
    for item in ANNEX_II_ITEMS:
        if item.auto_checkable and item.assessment_field:
            value = assessment_data.get(item.assessment_field)
            if value:
                results.append(AnnexIICheckResult(
                    key=item.key,
                    title=item.title,
                    article_ref=item.article_ref,
                    description=item.description,
                    status="done",
                    auto_derived=True,
                    derived_value=str(value),
                ))
            else:
                results.append(AnnexIICheckResult(
                    key=item.key,
                    title=item.title,
                    article_ref=item.article_ref,
                    description=item.description,
                    status="action_required",
                    auto_derived=True,
                    derived_value=None,
                ))
        else:
            results.append(AnnexIICheckResult(
                key=item.key,
                title=item.title,
                article_ref=item.article_ref,
                description=item.description,
                status="not_checked",
                auto_derived=False,
                derived_value=None,
            ))
    return results


def get_annex_ii_items() -> List[dict]:
    """Return the static Annex II checklist items as serialisable dicts."""
    return [
        {
            "key": item.key,
            "title": item.title,
            "description": item.description,
            "article_ref": item.article_ref,
            "auto_checkable": item.auto_checkable,
        }
        for item in ANNEX_II_ITEMS
    ]
