"""End-to-end integration tests for the CRA feature routes.

Exercises the live FastAPI app (via TestClient) against an ephemeral SQLite
database with schema migrated to head. Covers:

  - SBOM upload, list, detail, delete (CRA Art. 13(6))
  - Incident create, list, get, submit-phase, ENISA export (CRA Art. 14)
  - Annex VII JSON + Markdown endpoints (Annex VII)

Each test seeds minimum data directly via SQLAlchemy so it does not depend
on other routes; this keeps failures localised.
"""
from __future__ import annotations

import io
import json
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


# ──────────────── Seeding helpers ────────────────


def _seed_product_and_assessment(db: Session, *, product_id: str, assessment_id: str) -> None:
    from db.product_asset_models import ProductScope
    from db.cra_models import CraAssessment

    product = ProductScope(
        scope_id=product_id,
        name="Test-ECU",
        product_type="ECU",
        safety_level="ASIL-B",
        location="in-vehicle",
        trust_zone="trusted",
        description="Integration-test product",
    )
    assessment = CraAssessment(
        id=assessment_id,
        product_id=product_id,
        classification="class_i",
        compliance_path="Module B+C",
        support_period_years=7,
    )
    db.add_all([product, assessment])
    db.commit()


def _minimal_cyclonedx() -> bytes:
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "type": "firmware",
                "name": "Test-ECU",
                "version": "1.0.0",
            }
        },
        "components": [
            {
                "type": "library",
                "name": "openssl",
                "version": "3.0.0",
                "purl": "pkg:generic/openssl@3.0.0",
            }
        ],
    }
    return json.dumps(payload).encode("utf-8")


# ──────────────── SBOM ────────────────


class TestSbomRoutes:
    def test_upload_list_detail_delete_cycle(
        self, client: TestClient, db_session: Session
    ) -> None:
        _seed_product_and_assessment(db_session, product_id="p1", assessment_id="a1")

        files = {"file": ("sbom.json", io.BytesIO(_minimal_cyclonedx()), "application/json")}
        upload = client.post("/api/cra/assessments/a1/sboms", files=files)
        assert upload.status_code == 201, upload.text
        sbom_id = upload.json()["sbom"]["id"]

        listing = client.get("/api/cra/assessments/a1/sboms")
        assert listing.status_code == 200
        assert any(s["id"] == sbom_id for s in listing.json())

        detail = client.get(f"/api/cra/sboms/{sbom_id}")
        assert detail.status_code == 200
        body: dict[str, Any] = detail.json()
        assert body["sbom_format"] == "cyclonedx"
        assert body["component_count"] == 1

        deleted = client.delete(f"/api/cra/sboms/{sbom_id}")
        assert deleted.status_code == 204

        listing_after = client.get("/api/cra/assessments/a1/sboms")
        assert listing_after.json() == []

    def test_upload_rejects_invalid_sbom(
        self, client: TestClient, db_session: Session
    ) -> None:
        _seed_product_and_assessment(db_session, product_id="p2", assessment_id="a2")
        files = {"file": ("bad.json", io.BytesIO(b"{}"), "application/json")}
        res = client.post("/api/cra/assessments/a2/sboms", files=files)
        assert res.status_code == 400

    def test_upload_unknown_assessment_returns_404(self, client: TestClient) -> None:
        files = {"file": ("sbom.json", io.BytesIO(_minimal_cyclonedx()), "application/json")}
        res = client.post("/api/cra/assessments/nope/sboms", files=files)
        assert res.status_code == 404


# ──────────────── Incidents ────────────────


class TestIncidentRoutes:
    def test_create_list_get_submit_and_export(
        self, client: TestClient, db_session: Session
    ) -> None:
        _seed_product_and_assessment(db_session, product_id="pI", assessment_id="aI")

        create_body = {
            "title": "CAN bus compromise",
            "incident_type": "actively_exploited_vulnerability",
            "discovered_at": "2026-04-25T10:00:00+00:00",
            "assessment_id": "aI",
            "severity": "high",
            "actively_exploited": True,
            "member_states_affected": ["DE"],
            "product_description": "Brake ECU",
        }
        created = client.post("/api/cra/incidents", json=create_body)
        assert created.status_code == 201, created.text
        incident = created.json()
        incident_id = incident["id"]
        assert len(incident["deadlines"]) == 3

        listing = client.get("/api/cra/incidents", params={"assessment_id": "aI"})
        assert listing.status_code == 200
        assert listing.json()["total"] == 1

        fetched = client.get(f"/api/cra/incidents/{incident_id}")
        assert fetched.status_code == 200

        submit = client.post(
            f"/api/cra/incidents/{incident_id}/submit",
            json={"phase": "early_warning"},
        )
        assert submit.status_code == 200
        submitted_deadlines = {
            d["phase"]: d["status"] for d in submit.json()["deadlines"]
        }
        assert submitted_deadlines["early_warning"] == "submitted"

        export = client.get(
            f"/api/cra/incidents/{incident_id}/enisa-export",
            params={"phase": "early_warning"},
        )
        assert export.status_code == 200
        assert export.json()["phase"] == "early_warning"
        assert "payload" in export.json()

    def test_get_unknown_incident_returns_404(self, client: TestClient) -> None:
        res = client.get("/api/cra/incidents/does-not-exist")
        assert res.status_code == 404


# ──────────────── Annex VII ────────────────


class TestAnnexViiRoutes:
    def test_json_endpoint_returns_seven_sections(
        self, client: TestClient, db_session: Session
    ) -> None:
        _seed_product_and_assessment(db_session, product_id="pV", assessment_id="aV")

        res = client.get("/api/cra/assessments/aV/annex-vii")
        assert res.status_code == 200
        doc = res.json()
        assert doc["product_name"] == "Test-ECU"
        assert doc["classification"] == "class_i"
        assert len(doc["sections"]) == 7
        # §4 (standards) and §6 (DoC) are always action-required in v1.
        by_number = {s["number"]: s for s in doc["sections"]}
        assert by_number["4"]["is_action_required"] is True
        assert by_number["6"]["is_action_required"] is True

    def test_markdown_endpoint_downloads_attachment(
        self, client: TestClient, db_session: Session
    ) -> None:
        _seed_product_and_assessment(db_session, product_id="pM", assessment_id="aM")

        res = client.get("/api/cra/assessments/aM/annex-vii/markdown")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/markdown")
        assert "attachment" in res.headers.get("content-disposition", "")
        assert "# CRA Annex VII — Technical Documentation: Test-ECU" in res.text
        assert "Completeness:" in res.text

    def test_annex_vii_unknown_assessment_returns_404(self, client: TestClient) -> None:
        res = client.get("/api/cra/assessments/nope/annex-vii")
        assert res.status_code == 404
