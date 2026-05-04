"""Full ISO 21434 TARA workflow smoke test.

Exercises the happy-path API flow end-to-end:
  Products → Assets → Damage Scenarios → Threat Scenarios
  → Attack Paths (read) → Risk Treatment (read)

These were the routes that were returning 500 before the missing-table fixes
(attack_paths, risk_treatments, threat_damage_links). A regression here means
a table is no longer being created in conftest.py or _create_all_tables().
"""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


# ──────────────── helpers ────────────────


def _create_product(client: TestClient, scope_id: str = "tara-ecu-001") -> dict:
    body = {
        "scope_id": scope_id,
        "name": "Brake Control ECU",
        "product_type": "ECU",
        "description": "Controls brake actuation",
        "safety_level": "ASIL B",
        "location": "in-vehicle",
        "trust_zone": "Critical",
    }
    r = client.post("/api/products", json=body)
    assert r.status_code == 201, f"create product failed: {r.text}"
    return r.json()


def _create_asset(client: TestClient, scope_id: str, asset_id: str = "asset-fw-001") -> dict:
    body = {
        "asset_id": asset_id,
        "name": "Brake Firmware",
        "asset_type": "Firmware",
        "scope_id": scope_id,
        "confidentiality": "High",
        "integrity": "High",
        "availability": "High",
    }
    r = client.post("/api/assets", json=body)
    assert r.status_code == 201, f"create asset failed: {r.text}"
    return r.json()


def _create_damage_scenario(
    client: TestClient, scope_id: str, ds_id: str = "ds-001"
) -> dict:
    body = {
        "damage_scenario_id": ds_id,
        "name": "Unintended braking",
        "description": "Attacker causes unintended brake actuation via spoofed CAN messages",
        "damage_category": "Safety",
        "impact_type": "Direct",
        "severity": "Critical",
        "scope_id": scope_id,
        "confidentiality_impact": False,
        "integrity_impact": True,
        "availability_impact": True,
    }
    r = client.post("/api/damage-scenarios", json=body)
    assert r.status_code == 201, f"create damage scenario failed: {r.text}"
    return r.json()


def _create_threat_scenario(
    client: TestClient,
    scope_id: str,
    damage_scenario_id: str,
    ts_id: str = "ts-001",
) -> dict:
    body = {
        "threat_scenario_id": ts_id,
        "name": "Spoofed CAN message triggers braking",
        "description": "Attacker injects forged CAN frames via OBD-II port",
        "attack_vector": "physical",
        "scope_id": scope_id,
        "scope_version": 1,
        "damage_scenario_id": damage_scenario_id,
        "damage_scenario_ids": [damage_scenario_id],
    }
    r = client.post("/api/threat-scenarios", json=body)
    assert r.status_code == 201, f"create threat scenario failed: {r.text}"
    return r.json()


# ──────────────── tests ────────────────


class TestTaraWorkflow:
    """Full TARA workflow tests using a fully-migrated Alembic DB (mirrors production)."""

    def test_create_product(self, alembic_client: TestClient) -> None:
        product = _create_product(alembic_client)
        assert product["name"] == "Brake Control ECU"
        assert product["scope_id"] == "tara-ecu-001"

    def test_list_products_returns_created(self, alembic_client: TestClient) -> None:
        _create_product(alembic_client)
        r = alembic_client.get("/api/products")
        assert r.status_code == 200
        payload = r.json()
        # Response shape: {"scopes": [...], "total": N}
        names = [p["name"] for p in payload.get("scopes", payload)]
        assert "Brake Control ECU" in names

    def test_create_asset(self, alembic_client: TestClient) -> None:
        _create_product(alembic_client)
        asset = _create_asset(alembic_client, "tara-ecu-001")
        assert asset["name"] == "Brake Firmware"
        assert asset["scope_id"] == "tara-ecu-001"

    def test_create_damage_scenario(self, alembic_client: TestClient) -> None:
        _create_product(alembic_client)
        ds = _create_damage_scenario(alembic_client, "tara-ecu-001")
        assert ds["name"] == "Unintended braking"

    def test_list_damage_scenarios_not_empty(self, alembic_client: TestClient) -> None:
        _create_product(alembic_client)
        _create_damage_scenario(alembic_client, "tara-ecu-001")
        r = alembic_client.get("/api/damage-scenarios", params={"scope_id": "tara-ecu-001"})
        assert r.status_code == 200, f"GET damage-scenarios: {r.text}"
        payload = r.json()
        items = payload.get("scenarios", payload.get("damage_scenarios", payload))
        assert len(items) >= 1

    def test_create_threat_scenario(self, alembic_client: TestClient) -> None:
        _create_product(alembic_client)
        _create_damage_scenario(alembic_client, "tara-ecu-001")
        ts = _create_threat_scenario(alembic_client, "tara-ecu-001", "ds-001")
        assert ts["name"] == "Spoofed CAN message triggers braking"

    def test_list_threat_scenarios_not_empty(self, alembic_client: TestClient) -> None:
        _create_product(alembic_client)
        _create_damage_scenario(alembic_client, "tara-ecu-001")
        _create_threat_scenario(alembic_client, "tara-ecu-001", "ds-001")
        r = alembic_client.get("/api/threat-scenarios", params={"scope_id": "tara-ecu-001"})
        assert r.status_code == 200, f"GET threat-scenarios: {r.text}"
        payload = r.json()
        items = payload.get("threat_scenarios", payload.get("scenarios", payload))
        assert len(items) >= 1

    def test_get_attack_paths_by_product_returns_200(
        self, alembic_client: TestClient
    ) -> None:
        """This was returning 500 before attack_paths table was created."""
        _create_product(alembic_client)
        r = alembic_client.get("/api/attack-paths/product/tara-ecu-001")
        # 200 with an empty list is the expected happy path on a fresh DB.
        assert r.status_code == 200, f"GET attack-paths returned {r.status_code}: {r.text}"

    def test_get_risk_treatment_returns_200(self, alembic_client: TestClient) -> None:
        """This was returning 500 before risk_treatments table was created."""
        _create_product(alembic_client)
        r = alembic_client.get("/api/risk-treatment", params={"scope_id": "tara-ecu-001"})
        assert r.status_code == 200, f"GET risk-treatment returned {r.status_code}: {r.text}"

    def test_threat_damage_link_is_stored(
        self, alembic_client: TestClient, alembic_db_session: Session
    ) -> None:
        """Threat→damage link must be persisted in threat_damage_links table."""
        from sqlalchemy import text

        _create_product(alembic_client)
        _create_damage_scenario(alembic_client, "tara-ecu-001")
        _create_threat_scenario(alembic_client, "tara-ecu-001", "ds-001")

        rows = alembic_db_session.execute(
            text(
                "SELECT * FROM threat_damage_links "
                "WHERE threat_scenario_id = 'ts-001' AND damage_scenario_id = 'ds-001'"
            )
        ).fetchall()
        assert len(rows) == 1, "Expected one row in threat_damage_links after threat scenario creation"
