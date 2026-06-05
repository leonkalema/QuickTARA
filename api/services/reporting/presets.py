"""
Audience presets and built-in templates for report generation.

These produce ready-to-use ``ReportConfig`` objects. The audience matrix here
implements section 4 of docs/report-module-redesign.md.
"""
from typing import Dict, List

from api.models.report_config import (
    ReportAudience,
    ReportClassification,
    ReportConfig,
    ReportDetailLevel,
    SectionKey,
)


# Per-audience section toggles (section 4 of the design doc).
# CRA is enabled here when relevant, but assembly still omits it when no
# CRA assessment exists for the product.
_AUDIENCE_SECTIONS: Dict[ReportAudience, Dict[SectionKey, bool]] = {
    # Internal working report — everything on, full detail
    ReportAudience.INTERNAL: {
        SectionKey.DOCUMENT_CONTROL:      True,
        SectionKey.EXECUTIVE_SUMMARY:     True,
        SectionKey.SCOPE_AND_ASSUMPTIONS: True,
        SectionKey.METHODOLOGY:           True,
        SectionKey.ASSESSMENT_STATUS:     True,
        SectionKey.ISO_COMPLIANCE:        True,
        SectionKey.CRA_COMPLIANCE:        True,
        SectionKey.ASSET_INVENTORY:       True,
        SectionKey.DAMAGE_SCENARIOS:      True,
        SectionKey.THREAT_SCENARIOS:      True,
        SectionKey.ATTACK_PATHS:          True,
        SectionKey.RISK_SUMMARY:          True,
        SectionKey.RISK_REGISTER:         True,
        SectionKey.TREATMENT_SUMMARY:     True,
        SectionKey.CYBERSECURITY_GOALS:   True,
        SectionKey.OPEN_ISSUES:           True,
        SectionKey.TRACEABILITY:          True,
    },
    # External / OEM report — no sensitive technical detail
    ReportAudience.EXTERNAL: {
        SectionKey.DOCUMENT_CONTROL:      True,
        SectionKey.EXECUTIVE_SUMMARY:     True,
        SectionKey.SCOPE_AND_ASSUMPTIONS: True,
        SectionKey.METHODOLOGY:           True,
        SectionKey.ASSESSMENT_STATUS:     True,
        SectionKey.ISO_COMPLIANCE:        True,
        SectionKey.CRA_COMPLIANCE:        False,  # internal regulatory gaps
        SectionKey.ASSET_INVENTORY:       True,
        SectionKey.DAMAGE_SCENARIOS:      False,  # sensitive IP
        SectionKey.THREAT_SCENARIOS:      False,  # attack roadmap
        SectionKey.ATTACK_PATHS:          False,  # attacker guide
        SectionKey.RISK_SUMMARY:          True,
        SectionKey.RISK_REGISTER:         True,   # decisions only, no attack detail
        SectionKey.TREATMENT_SUMMARY:     True,
        SectionKey.CYBERSECURITY_GOALS:   True,
        SectionKey.OPEN_ISSUES:           True,
        SectionKey.TRACEABILITY:          False,  # internal architecture
    },
    # Auditor / ISO 21434 type-approval body
    ReportAudience.AUDITOR: {
        SectionKey.DOCUMENT_CONTROL:      True,
        SectionKey.EXECUTIVE_SUMMARY:     True,
        SectionKey.SCOPE_AND_ASSUMPTIONS: True,
        SectionKey.METHODOLOGY:           True,
        SectionKey.ASSESSMENT_STATUS:     True,
        SectionKey.ISO_COMPLIANCE:        True,
        SectionKey.CRA_COMPLIANCE:        False,  # separate regulatory track
        SectionKey.ASSET_INVENTORY:       True,
        SectionKey.DAMAGE_SCENARIOS:      True,
        SectionKey.THREAT_SCENARIOS:      True,
        SectionKey.ATTACK_PATHS:          False,  # not needed for process audit
        SectionKey.RISK_SUMMARY:          True,
        SectionKey.RISK_REGISTER:         True,
        SectionKey.TREATMENT_SUMMARY:     True,
        SectionKey.CYBERSECURITY_GOALS:   True,
        SectionKey.OPEN_ISSUES:           True,
        SectionKey.TRACEABILITY:          True,   # essential for clause audit
    },
}

_AUDIENCE_DETAIL: Dict[ReportAudience, ReportDetailLevel] = {
    ReportAudience.INTERNAL: ReportDetailLevel.FULL,
    ReportAudience.EXTERNAL: ReportDetailLevel.SUMMARY,
    ReportAudience.AUDITOR: ReportDetailLevel.FULL,
}

_AUDIENCE_CLASSIFICATION: Dict[ReportAudience, ReportClassification] = {
    ReportAudience.INTERNAL: ReportClassification.INTERNAL,
    ReportAudience.EXTERNAL: ReportClassification.CONFIDENTIAL,
    ReportAudience.AUDITOR: ReportClassification.CONFIDENTIAL,
}


def default_config_for_audience(audience: ReportAudience) -> ReportConfig:
    """Build a ``ReportConfig`` pre-filled with the audience's default profile."""
    return ReportConfig(
        audience=audience,
        detail_level=_AUDIENCE_DETAIL[audience],
        classification=_AUDIENCE_CLASSIFICATION[audience],
        sections=dict(_AUDIENCE_SECTIONS[audience]),
    )


# Named, read-only presets surfaced as built-in templates in the UI.
_BUILTIN_PRESET_AUDIENCE: Dict[str, ReportAudience] = {
    "Internal — Full": ReportAudience.INTERNAL,
    "External — Customer/OEM": ReportAudience.EXTERNAL,
    "Auditor / Regulator": ReportAudience.AUDITOR,
}


def builtin_preset_names() -> List[str]:
    """Names of the built-in presets, in display order."""
    return list(_BUILTIN_PRESET_AUDIENCE.keys())


def get_builtin_preset(name: str) -> ReportConfig:
    """Return the ``ReportConfig`` for a named built-in preset."""
    try:
        audience = _BUILTIN_PRESET_AUDIENCE[name]
    except KeyError as exc:
        raise ValueError(f"Unknown built-in preset: {name}") from exc
    return default_config_for_audience(audience)
