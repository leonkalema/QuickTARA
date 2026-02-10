"""
CRA Data Classification Engine

Maps product data characteristics to CRA requirement applicability.
When a characteristic is absent, linked requirements become N/A by design.

Source: EU 2024/2847 Annex I — interpreted through product data profile.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class DataQuestion:
    """One yes/no question about the product's data characteristics."""
    key: str
    label: str
    help_text: str
    category: str


@dataclass(frozen=True)
class ApplicabilityResult:
    """Result for a single requirement after data classification."""
    requirement_id: str
    applicable: bool
    justification: str


DATA_QUESTIONS: List[DataQuestion] = [
    DataQuestion(
        key="stores_data_at_rest",
        label="Does the product store data on device?",
        help_text="Firmware config, user settings, logs, credentials, any persistent storage.",
        category="Storage",
    ),
    DataQuestion(
        key="stores_personal_data",
        label="Does the product collect or process personal data?",
        help_text="Names, emails, IP addresses, location, biometrics, usage patterns.",
        category="Privacy",
    ),
    DataQuestion(
        key="collects_telemetry",
        label="Does the product send telemetry or usage analytics?",
        help_text="Any data sent to manufacturer servers, cloud dashboards, or third parties.",
        category="Privacy",
    ),
    DataQuestion(
        key="has_network_interfaces",
        label="Does the product connect to a network?",
        help_text="Wi-Fi, Ethernet, Bluetooth, cellular, CAN bus, any IP-based interface.",
        category="Connectivity",
    ),
    DataQuestion(
        key="has_user_authentication",
        label="Does the product authenticate users or systems?",
        help_text="Passwords, tokens, certificates, API keys, biometric login.",
        category="Access",
    ),
    DataQuestion(
        key="has_physical_interfaces",
        label="Does the product have physical debug/data interfaces?",
        help_text="USB, serial, JTAG, SD card slot, diagnostic port.",
        category="Access",
    ),
    DataQuestion(
        key="has_updateable_software",
        label="Can the product's software or firmware be updated?",
        help_text="OTA updates, USB firmware flash, SD card update.",
        category="Lifecycle",
    ),
    DataQuestion(
        key="uses_third_party_components",
        label="Does the product include third-party or open-source software?",
        help_text="Linux kernel, OpenSSL, FreeRTOS, any library not written in-house.",
        category="Supply Chain",
    ),
    DataQuestion(
        key="has_crypto_keys",
        label="Does the product generate, store, or use cryptographic keys?",
        help_text="TLS certificates, signing keys, symmetric keys, secure boot keys.",
        category="Cryptography",
    ),
]

# ── Requirement applicability rules ──────────────────────────────
# Each entry: requirement_id → list of profile keys that make it applicable.
# If ALL listed keys are False, the requirement is N/A with the given justification.
# If ANY listed key is True, the requirement applies.

_APPLICABILITY_RULES: Dict[str, Dict] = {
    "CRA-02": {
        "triggers": ["has_user_authentication", "has_network_interfaces", "has_physical_interfaces"],
        "na_justification": "Product has no user-accessible or network interfaces — access control met by design.",
    },
    "CRA-03": {
        "triggers": ["stores_data_at_rest", "has_network_interfaces", "has_crypto_keys"],
        "na_justification": "Product does not store, transmit, or process sensitive data — confidentiality met by design.",
    },
    "CRA-05": {
        "triggers": ["stores_personal_data", "collects_telemetry"],
        "na_justification": "Product collects no personal data and sends no telemetry — data minimization met by design.",
    },
    "CRA-06": {
        "triggers": ["has_network_interfaces"],
        "na_justification": "Product has no network connectivity — availability/DoS resilience met by design.",
    },
    "CRA-08": {
        "triggers": ["has_network_interfaces", "has_user_authentication"],
        "na_justification": "Product has no network or authentication interfaces — security monitoring not applicable.",
    },
}

# Requirements that ALWAYS apply regardless of data profile
ALWAYS_APPLICABLE = {
    "CRA-01", "CRA-04", "CRA-07", "CRA-09",
    "CRA-10", "CRA-11", "CRA-12", "CRA-13", "CRA-14",
    "CRA-15", "CRA-16", "CRA-17", "CRA-18",
}

ALL_REQUIREMENT_IDS = [f"CRA-{i:02d}" for i in range(1, 19)]


def compute_applicability(
    profile: Dict[str, bool],
) -> List[ApplicabilityResult]:
    """Given a data profile, return applicability for all 18 requirements."""
    results: List[ApplicabilityResult] = []
    for req_id in ALL_REQUIREMENT_IDS:
        if req_id in ALWAYS_APPLICABLE:
            results.append(ApplicabilityResult(
                requirement_id=req_id,
                applicable=True,
                justification="Always applicable under CRA Annex I.",
            ))
            continue
        rule = _APPLICABILITY_RULES.get(req_id)
        if not rule:
            results.append(ApplicabilityResult(
                requirement_id=req_id,
                applicable=True,
                justification="Applicable by default.",
            ))
            continue
        triggered = any(profile.get(key, False) for key in rule["triggers"])
        if triggered:
            active_triggers = [k for k in rule["triggers"] if profile.get(k, False)]
            results.append(ApplicabilityResult(
                requirement_id=req_id,
                applicable=True,
                justification=f"Applicable — product has: {', '.join(active_triggers)}.",
            ))
        else:
            results.append(ApplicabilityResult(
                requirement_id=req_id,
                applicable=False,
                justification=rule["na_justification"],
            ))
    return results


def get_questions() -> List[Dict[str, str]]:
    """Return serializable list of data classification questions."""
    return [
        {
            "key": q.key,
            "label": q.label,
            "help_text": q.help_text,
            "category": q.category,
        }
        for q in DATA_QUESTIONS
    ]
