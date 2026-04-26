"""CRA Art. 13(6) and Annex I, Part II §1 — Software Bill of Materials.

Pure parser for SBOM documents. No I/O, no DB, no FastAPI. Returns
immutable value objects suitable for persistence by `db/cra_sbom_models.py`
and serialisation by `api/models/cra_sbom.py`.

Supported formats:
  - CycloneDX 1.4 / 1.5 / 1.6 (JSON)
  - SPDX 2.3 (JSON) — minimal subset (name, version, supplier, licenseDeclared)

Source spec references:
  - CycloneDX 1.5: https://cyclonedx.org/docs/1.5/json/
  - SPDX 2.3:      https://spdx.github.io/spdx-spec/v2.3/
  - CRA Art. 13(6) / Annex I, Part II §1: manufacturers must identify and
    document vulnerabilities in components, including by drawing up an SBOM
    in a commonly used and machine-readable format.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class SbomFormat(str, Enum):
    """SBOM document formats accepted by the parser."""

    CYCLONEDX = "cyclonedx"
    SPDX = "spdx"


@dataclass(frozen=True)
class SbomComponent:
    """One component entry within an SBOM. Immutable.

    Field choices reflect what the CRA evidence trail needs:
      - `name`, `version`            → identification
      - `purl` / `cpe`               → CVE matching (NVD, OSV)
      - `supplier`                   → CRA Art. 13 supplier disclosure
      - `licenses`                   → Annex VII technical documentation
      - `hashes`                     → integrity verification (CRA-04)
      - `bom_ref`                    → stable reference for control linkage
    """

    bom_ref: str
    name: str
    version: Optional[str]
    component_type: Optional[str]
    purl: Optional[str]
    cpe: Optional[str]
    supplier: Optional[str]
    licenses: Tuple[str, ...] = field(default_factory=tuple)
    hashes: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class SbomDocument:
    """Top-level SBOM metadata + components."""

    sbom_format: SbomFormat
    spec_version: str
    serial_number: Optional[str]
    document_name: Optional[str]
    primary_component_name: Optional[str]
    primary_component_version: Optional[str]
    components: Tuple[SbomComponent, ...]
    raw_size_bytes: int


@dataclass(frozen=True)
class SbomParseResult:
    """Result of parsing. `errors` is non-empty when `document` is None."""

    document: Optional[SbomDocument]
    errors: Tuple[str, ...]
    warnings: Tuple[str, ...]


def parse_sbom(raw: bytes) -> SbomParseResult:
    """Parse an SBOM payload of unknown format. Detects CycloneDX vs SPDX.

    Returns a result object — never raises. Callers should inspect
    `result.document is None` to detect failure.
    """
    if not raw:
        return SbomParseResult(None, ("empty payload",), ())

    try:
        decoded: Dict[str, Any] = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return SbomParseResult(None, (f"invalid JSON: {exc}",), ())

    if not isinstance(decoded, dict):
        return SbomParseResult(None, ("SBOM root must be a JSON object",), ())

    if decoded.get("bomFormat") == "CycloneDX" or "components" in decoded:
        return _parse_cyclonedx(decoded, len(raw))

    if decoded.get("spdxVersion") or "SPDXID" in decoded:
        return _parse_spdx(decoded, len(raw))

    return SbomParseResult(
        None,
        ("unrecognised SBOM format — expected CycloneDX or SPDX",),
        (),
    )


# ──────────────── CycloneDX ────────────────


_CDX_REQUIRED_TOP_LEVEL: Tuple[str, ...] = ("bomFormat", "specVersion")
_CDX_SUPPORTED_VERSIONS: Tuple[str, ...] = ("1.4", "1.5", "1.6")


def _parse_cyclonedx(doc: Dict[str, Any], raw_size: int) -> SbomParseResult:
    errors: List[str] = []
    warnings: List[str] = []

    for required in _CDX_REQUIRED_TOP_LEVEL:
        if required not in doc:
            errors.append(f"CycloneDX: missing required field '{required}'")

    spec_version = str(doc.get("specVersion", ""))
    if spec_version and spec_version not in _CDX_SUPPORTED_VERSIONS:
        warnings.append(
            f"CycloneDX specVersion {spec_version} not officially supported; "
            f"parsing as best-effort."
        )

    if errors:
        return SbomParseResult(None, tuple(errors), tuple(warnings))

    metadata: Dict[str, Any] = doc.get("metadata") or {}
    primary: Dict[str, Any] = metadata.get("component") or {}

    raw_components: List[Dict[str, Any]] = doc.get("components") or []
    components: List[SbomComponent] = []
    for idx, raw_comp in enumerate(raw_components):
        parsed = _parse_cyclonedx_component(raw_comp, idx)
        if parsed is not None:
            components.append(parsed)
        else:
            warnings.append(f"CycloneDX: component[{idx}] skipped (missing name)")

    document = SbomDocument(
        sbom_format=SbomFormat.CYCLONEDX,
        spec_version=spec_version,
        serial_number=doc.get("serialNumber"),
        document_name=primary.get("name") or metadata.get("manufacture", {}).get("name"),
        primary_component_name=primary.get("name"),
        primary_component_version=primary.get("version"),
        components=tuple(components),
        raw_size_bytes=raw_size,
    )
    return SbomParseResult(document, (), tuple(warnings))


def _parse_cyclonedx_component(raw: Dict[str, Any], idx: int) -> Optional[SbomComponent]:
    name = raw.get("name")
    if not name:
        return None

    bom_ref = str(raw.get("bom-ref") or raw.get("bomRef") or f"component-{idx}")
    version = raw.get("version")
    component_type = raw.get("type")
    purl = raw.get("purl")
    cpe = raw.get("cpe")

    supplier_obj = raw.get("supplier") or {}
    supplier = supplier_obj.get("name") if isinstance(supplier_obj, dict) else None

    licenses_raw = raw.get("licenses") or []
    licenses: List[str] = []
    for entry in licenses_raw:
        if not isinstance(entry, dict):
            continue
        lic = entry.get("license") or {}
        ident = lic.get("id") or lic.get("name") or entry.get("expression")
        if ident:
            licenses.append(str(ident))

    hashes_raw = raw.get("hashes") or []
    hashes: List[Tuple[str, str]] = []
    for entry in hashes_raw:
        if not isinstance(entry, dict):
            continue
        alg = entry.get("alg")
        content = entry.get("content")
        if alg and content:
            hashes.append((str(alg), str(content)))

    return SbomComponent(
        bom_ref=bom_ref,
        name=str(name),
        version=str(version) if version else None,
        component_type=str(component_type) if component_type else None,
        purl=str(purl) if purl else None,
        cpe=str(cpe) if cpe else None,
        supplier=str(supplier) if supplier else None,
        licenses=tuple(licenses),
        hashes=tuple(hashes),
    )


# ──────────────── SPDX (minimal) ────────────────


def _parse_spdx(doc: Dict[str, Any], raw_size: int) -> SbomParseResult:
    errors: List[str] = []
    warnings: List[str] = []

    spec_version = str(doc.get("spdxVersion", "")).replace("SPDX-", "")
    if not spec_version:
        errors.append("SPDX: missing 'spdxVersion'")

    if errors:
        return SbomParseResult(None, tuple(errors), tuple(warnings))

    raw_packages: List[Dict[str, Any]] = doc.get("packages") or []
    components: List[SbomComponent] = []
    for idx, pkg in enumerate(raw_packages):
        parsed = _parse_spdx_package(pkg, idx)
        if parsed is not None:
            components.append(parsed)
        else:
            warnings.append(f"SPDX: package[{idx}] skipped (missing name)")

    document = SbomDocument(
        sbom_format=SbomFormat.SPDX,
        spec_version=spec_version,
        serial_number=doc.get("documentNamespace"),
        document_name=doc.get("name"),
        primary_component_name=None,
        primary_component_version=None,
        components=tuple(components),
        raw_size_bytes=raw_size,
    )
    return SbomParseResult(document, (), tuple(warnings))


def _parse_spdx_package(raw: Dict[str, Any], idx: int) -> Optional[SbomComponent]:
    name = raw.get("name")
    if not name:
        return None

    bom_ref = str(raw.get("SPDXID") or f"spdx-package-{idx}")
    version = raw.get("versionInfo")
    supplier_raw = raw.get("supplier")
    supplier: Optional[str] = None
    if isinstance(supplier_raw, str) and supplier_raw.startswith(("Organization:", "Person:")):
        supplier = supplier_raw.split(":", 1)[1].strip() or None

    license_declared = raw.get("licenseDeclared")
    licenses: Tuple[str, ...] = (
        (str(license_declared),) if license_declared and license_declared != "NOASSERTION" else ()
    )

    purl: Optional[str] = None
    for ref in raw.get("externalRefs", []) or []:
        if (
            isinstance(ref, dict)
            and ref.get("referenceCategory") == "PACKAGE-MANAGER"
            and ref.get("referenceType") == "purl"
        ):
            purl = str(ref.get("referenceLocator", "")) or None
            break

    return SbomComponent(
        bom_ref=bom_ref,
        name=str(name),
        version=str(version) if version else None,
        component_type=None,
        purl=purl,
        cpe=None,
        supplier=supplier,
        licenses=licenses,
        hashes=(),
    )
