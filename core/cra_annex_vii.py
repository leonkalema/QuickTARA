"""CRA Annex VII — Technical documentation builder.

Pure aggregation: takes a SQLAlchemy session + assessment_id and produces
an immutable structured document covering all 7 sections of Annex VII.
Does not render, does not write to disk, does not raise on missing data —
sections with no source data are emitted with `is_action_required=True`.

Annex VII (Regulation (EU) 2024/2847) requires the manufacturer's
technical documentation to contain at least:

  §1  General description of the product
       (intended purpose, software versions, photos, user instructions)
  §2  Description of design, development, production processes and
       evidence-of-process
  §3  Risk assessment per Article 13
  §4  List of harmonised standards / common specifications applied
  §5  Reports of tests carried out to verify conformity
  §6  Copy of the EU declaration of conformity
  §7  Where applicable, software bill of materials
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from core.cra_annex_vii_models import (
    AnnexViiAsset,
    AnnexViiCompensatingControl,
    AnnexViiDamageScenario,
    AnnexViiDocument,
    AnnexViiRequirement,
    AnnexViiSbomEntry,
    AnnexViiSection,
)
from core.cra_annex_vii_sections import (
    section_1_body,
    section_2_body,
    section_3_body,
    section_4_body,
    section_5_body,
    section_6_body,
    section_7_body,
)
from db.cra_models import (
    CraAssessment,
    CraCompensatingControl,
    CraControlRequirementLink,
    CraRequirementStatusRecord,
)
from db.cra_sbom_models import CraSbom
from db.product_asset_models import Asset, DamageScenario, ProductScope, ThreatScenario
from core.cra_auto_mapper import get_requirement_by_id


# ──────────────── Public API ────────────────


def build_annex_vii(db: Session, assessment_id: str) -> Optional[AnnexViiDocument]:
    """Build the document from QuickTARA data.

    Returns ``None`` if the assessment does not exist. Any other missing
    data is captured as ``is_action_required=True`` on the relevant section.
    """
    assessment = (
        db.query(CraAssessment).filter(CraAssessment.id == assessment_id).first()
    )
    if assessment is None:
        return None

    product = (
        db.query(ProductScope).filter(ProductScope.scope_id == assessment.product_id).first()
    )
    product_name = product.name if product else assessment.product_id
    interfaces = tuple(_as_str_list(getattr(product, "interfaces", None)))
    access_points = tuple(_as_str_list(getattr(product, "access_points", None)))

    assets = _load_assets(db, assessment.product_id)
    scenarios = _load_damage_scenarios(db, assessment.product_id)
    requirements = _load_requirements(db, assessment_id)
    controls = _load_compensating_controls(db, assessment_id)
    sboms = _load_sboms(db, assessment_id)

    sections = _build_sections(
        product_name=product_name,
        product=product,
        assessment=assessment,
        assets=assets,
        scenarios=scenarios,
        requirements=requirements,
        controls=controls,
        sboms=sboms,
    )

    return AnnexViiDocument(
        assessment_id=assessment_id,
        product_name=product_name,
        product_id=assessment.product_id,
        classification=assessment.classification,
        conformity_assessment=assessment.compliance_path,
        support_period_years=assessment.support_period_years,
        support_period_justification=assessment.support_period_justification,
        compliance_deadline=assessment.compliance_deadline,
        generated_at=datetime.now(timezone.utc),
        intended_purpose=getattr(product, "description", None) if product else None,
        product_description=getattr(product, "description", None) if product else None,
        safety_level=getattr(product, "safety_level", None) if product else None,
        interfaces=interfaces,
        access_points=access_points,
        assets=assets,
        damage_scenarios=scenarios,
        requirements=requirements,
        compensating_controls=controls,
        sboms=sboms,
        sections=sections,
        completeness_pct=_completeness_pct(sections),
    )


# ──────────────── Loaders ────────────────


def _as_str_list(raw) -> List[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw]
    return [str(raw)]


def _load_assets(db: Session, product_id: str) -> Tuple[AnnexViiAsset, ...]:
    rows = (
        db.query(Asset)
        .filter(Asset.scope_id == product_id, Asset.is_current.is_(True))
        .all()
    )
    return tuple(
        AnnexViiAsset(
            asset_id=str(a.asset_id),
            name=str(a.name),
            asset_type=str(a.asset_type),
            confidentiality=str(a.confidentiality),
            integrity=str(a.integrity),
            availability=str(a.availability),
        )
        for a in rows
    )


def _load_damage_scenarios(
    db: Session, product_id: str
) -> Tuple[AnnexViiDamageScenario, ...]:
    rows = (
        db.query(DamageScenario)
        .filter(
            DamageScenario.scope_id == product_id,
            DamageScenario.is_current.is_(True),
        )
        .all()
    )
    out: List[AnnexViiDamageScenario] = []
    for ds in rows:
        threat_count = (
            db.query(ThreatScenario)
            .filter(ThreatScenario.damage_scenario_id == ds.scenario_id)
            .count()
        )
        out.append(
            AnnexViiDamageScenario(
                scenario_id=str(ds.scenario_id),
                name=str(ds.name),
                description=str(ds.description or ""),
                severity=str(ds.severity or "unknown"),
                safety_impact=str(ds.safety_impact or "negligible"),
                financial_impact=str(ds.financial_impact or "negligible"),
                operational_impact=str(ds.operational_impact or "negligible"),
                privacy_impact=str(ds.privacy_impact or "negligible"),
                threat_count=threat_count,
            )
        )
    return tuple(out)


def _load_requirements(
    db: Session, assessment_id: str
) -> Tuple[AnnexViiRequirement, ...]:
    rows = (
        db.query(CraRequirementStatusRecord)
        .filter(CraRequirementStatusRecord.assessment_id == assessment_id)
        .all()
    )
    def _meta(req_id: str, field: str, default: str) -> str:
        defn = get_requirement_by_id(req_id)
        return defn.get(field, default) if defn else default

    return tuple(
        AnnexViiRequirement(
            requirement_id=str(r.requirement_id),
            name=_meta(r.requirement_id, "name", r.requirement_id),
            category=_meta(r.requirement_id, "category", "uncategorised"),
            annex_part=_meta(r.requirement_id, "annex_part", ""),
            status=str(r.status or "not_started"),
            auto_mapped=bool(r.auto_mapped),
            evidence_notes=r.evidence_notes,
        )
        for r in rows
    )


def _load_compensating_controls(
    db: Session, assessment_id: str
) -> Tuple[AnnexViiCompensatingControl, ...]:
    rows = (
        db.query(CraCompensatingControl)
        .filter(CraCompensatingControl.assessment_id == assessment_id)
        .all()
    )
    result = []
    for c in rows:
        # Resolve requirement_id via junction table → requirement status record
        first_link = (
            db.query(CraControlRequirementLink)
            .filter(CraControlRequirementLink.control_id == c.id)
            .first()
        )
        req_id: Optional[str] = None
        if first_link:
            req_status = db.query(CraRequirementStatusRecord).filter(
                CraRequirementStatusRecord.id == first_link.requirement_status_id
            ).first()
            if req_status:
                req_id = str(req_status.requirement_id)
        result.append(AnnexViiCompensatingControl(
            control_id=str(c.id),
            name=str(c.name),
            description=str(c.description or ""),
            status=str(c.implementation_status or "planned"),
            requirement_id=req_id,
        ))
    return tuple(result)


def _load_sboms(db: Session, assessment_id: str) -> Tuple[AnnexViiSbomEntry, ...]:
    rows = (
        db.query(CraSbom)
        .filter(CraSbom.assessment_id == assessment_id)
        .order_by(CraSbom.uploaded_at.desc())
        .all()
    )
    return tuple(
        AnnexViiSbomEntry(
            sbom_id=str(s.id),
            sbom_format=str(s.sbom_format),
            spec_version=str(s.spec_version),
            component_count=int(s.component_count or 0),
            primary_component_name=s.primary_component_name,
            primary_component_version=s.primary_component_version,
            uploaded_at=s.uploaded_at,
        )
        for s in rows
    )


# ──────────────── Section assembly ────────────────


def _build_sections(
    *,
    product_name: str,
    product,
    assessment: CraAssessment,
    assets: Tuple[AnnexViiAsset, ...],
    scenarios: Tuple[AnnexViiDamageScenario, ...],
    requirements: Tuple[AnnexViiRequirement, ...],
    controls: Tuple[AnnexViiCompensatingControl, ...],
    sboms: Tuple[AnnexViiSbomEntry, ...],
) -> Tuple[AnnexViiSection, ...]:
    has_product = product is not None
    has_classification = assessment.classification is not None
    has_support_period = assessment.support_period_years is not None
    has_assets_or_scenarios = bool(assets) or bool(scenarios)
    has_part_i = any(
        r.status in {"compliant", "partial"}
        and r.annex_part.lower().startswith("part i")
        for r in requirements
    )
    has_part_ii = any(
        r.status in {"compliant", "partial"}
        and r.annex_part.lower().startswith("part ii")
        for r in requirements
    )

    return (
        AnnexViiSection(
            number="1",
            title="General description of the product",
            article_ref="Annex VII §1",
            body=section_1_body(product_name, product, assessment),
            is_action_required=not (has_product and has_classification and has_support_period),
        ),
        AnnexViiSection(
            number="2",
            title="Description of design, development and production",
            article_ref="Annex VII §2 (read with Annex II)",
            body=section_2_body(requirements, controls),
            is_action_required=not has_part_ii,
        ),
        AnnexViiSection(
            number="3",
            title="Risk assessment",
            article_ref="Annex VII §3 / Article 13",
            body=section_3_body(assets, scenarios),
            is_action_required=not has_assets_or_scenarios,
        ),
        AnnexViiSection(
            number="4",
            title="List of harmonised standards / common specifications applied",
            article_ref="Annex VII §4",
            body=section_4_body(),
            is_action_required=True,
        ),
        AnnexViiSection(
            number="5",
            title="Reports of tests carried out to verify conformity",
            article_ref="Annex VII §5",
            body=section_5_body(requirements),
            is_action_required=not (has_part_i and has_part_ii),
        ),
        AnnexViiSection(
            number="6",
            title="EU Declaration of Conformity",
            article_ref="Annex VII §6 / Article 28",
            body=section_6_body(),
            is_action_required=True,
        ),
        AnnexViiSection(
            number="7",
            title="Software Bill of Materials",
            article_ref="Annex VII §7 / Article 13(6)",
            body=section_7_body(sboms),
            is_action_required=not bool(sboms),
        ),
    )


def _completeness_pct(sections: Tuple[AnnexViiSection, ...]) -> int:
    if not sections:
        return 0
    done = sum(1 for s in sections if not s.is_action_required)
    return int((done / len(sections)) * 100)
