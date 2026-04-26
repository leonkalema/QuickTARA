"""Tests for `core.cra_sbom_parser` — CRA Art. 13(6) SBOM ingestion."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.cra_sbom_parser import SbomFormat, parse_sbom

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


# ──────────────── CycloneDX ────────────────


def test_parse_cyclonedx_minimal_succeeds() -> None:
    """Happy path — valid CycloneDX 1.5 with three components."""
    result = parse_sbom(_load("cyclonedx_minimal.json"))

    assert result.errors == ()
    assert result.document is not None
    doc = result.document
    assert doc.sbom_format == SbomFormat.CYCLONEDX
    assert doc.spec_version == "1.5"
    assert doc.serial_number == "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79"
    assert doc.primary_component_name == "ECU-Brake-Controller"
    assert doc.primary_component_version == "2.4.1"
    assert len(doc.components) == 3


def test_parse_cyclonedx_extracts_purl_supplier_license_hash() -> None:
    """Component fields needed for CVE matching and Annex VII docs."""
    result = parse_sbom(_load("cyclonedx_minimal.json"))
    assert result.document is not None

    by_name = {c.name: c for c in result.document.components}
    openssl = by_name["openssl"]
    assert openssl.version == "3.0.12"
    assert openssl.purl == "pkg:generic/openssl@3.0.12"
    assert openssl.supplier == "OpenSSL Software Foundation"
    assert openssl.licenses == ("Apache-2.0",)
    assert openssl.hashes == (
        ("SHA-256", "1a2b3c4d5e6f70811223344556677889900aabbccddeeff00112233445566778"),
    )


def test_parse_cyclonedx_handles_component_without_version() -> None:
    """Components without a version are kept (CRA-10 only mandates name)."""
    result = parse_sbom(_load("cyclonedx_minimal.json"))
    assert result.document is not None
    no_version = next(c for c in result.document.components if c.name == "embedded-tls")
    assert no_version.version is None
    assert no_version.bom_ref == "no-version"


def test_parse_cyclonedx_skips_component_without_name_and_warns() -> None:
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "components": [{"type": "library", "version": "1.0"}],
    }
    result = parse_sbom(json.dumps(payload).encode("utf-8"))
    assert result.document is not None
    assert len(result.document.components) == 0
    assert any("missing name" in w for w in result.warnings)


def test_parse_cyclonedx_unsupported_spec_version_warns_but_parses() -> None:
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": "0.9",
        "components": [{"type": "library", "name": "x", "version": "1"}],
    }
    result = parse_sbom(json.dumps(payload).encode("utf-8"))
    assert result.document is not None
    assert any("0.9" in w for w in result.warnings)


def test_parse_cyclonedx_missing_required_top_level_returns_error() -> None:
    payload = {"components": [{"name": "x"}]}
    result = parse_sbom(json.dumps(payload).encode("utf-8"))
    # No bomFormat means it routes to SPDX detection, falls through to "unrecognised"
    assert result.document is None


# ──────────────── SPDX ────────────────


def test_parse_spdx_minimal_extracts_packages() -> None:
    payload = {
        "spdxVersion": "SPDX-2.3",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "test-doc",
        "documentNamespace": "https://example.com/doc",
        "packages": [
            {
                "SPDXID": "SPDXRef-Package-openssl",
                "name": "openssl",
                "versionInfo": "3.0.12",
                "supplier": "Organization: OpenSSL",
                "licenseDeclared": "Apache-2.0",
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": "pkg:generic/openssl@3.0.12",
                    }
                ],
            }
        ],
    }
    result = parse_sbom(json.dumps(payload).encode("utf-8"))
    assert result.errors == ()
    assert result.document is not None
    assert result.document.sbom_format == SbomFormat.SPDX
    assert result.document.spec_version == "2.3"
    assert len(result.document.components) == 1
    comp = result.document.components[0]
    assert comp.name == "openssl"
    assert comp.version == "3.0.12"
    assert comp.supplier == "OpenSSL"
    assert comp.licenses == ("Apache-2.0",)
    assert comp.purl == "pkg:generic/openssl@3.0.12"


# ──────────────── Failure modes ────────────────


def test_parse_empty_payload_returns_error() -> None:
    result = parse_sbom(b"")
    assert result.document is None
    assert "empty payload" in result.errors[0]


def test_parse_invalid_json_returns_error() -> None:
    result = parse_sbom(b"{not json")
    assert result.document is None
    assert "invalid JSON" in result.errors[0]


def test_parse_unknown_format_returns_error() -> None:
    result = parse_sbom(json.dumps({"foo": "bar"}).encode("utf-8"))
    assert result.document is None
    assert "unrecognised" in result.errors[0]


def test_parse_non_object_root_returns_error() -> None:
    result = parse_sbom(b"[]")
    assert result.document is None
    assert "must be a JSON object" in result.errors[0]
