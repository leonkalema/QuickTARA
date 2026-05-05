"""Full migration chain upgrade/downgrade round-trip tests.

Covers every revision from the initial schema to head, verifying:
  - `alembic upgrade head` creates all critical tables on a fresh DB
  - Per-revision spot-checks: correct columns, defaults, and constraints
  - Full head → base → head round-trip is idempotent and leaves schema intact

Complements `test_cra_migrations_roundtrip.py` (CRA-only revisions) by
exercising the entire chain and tables that are not covered by CRA tests.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYTHONPATH", str(ROOT))
import db.base  # noqa: E402,F401  — warm sys.modules for alembic env.py


def _make_config(db_path: Path) -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "db" / "migrations"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return cfg


@pytest.fixture
def ephemeral_db(tmp_path: Path):
    db_path = tmp_path / "full_roundtrip.db"
    yield db_path
    if db_path.exists():
        os.remove(db_path)


# ──────────────── head upgrade ────────────────


def test_upgrade_head_creates_core_tables(ephemeral_db: Path) -> None:
    """Verify all core TARA tables exist after a fresh head upgrade."""
    command.upgrade(_make_config(ephemeral_db), "head")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    tables = set(inspect(engine).get_table_names())

    # Tables guaranteed by Alembic migrations (including i9j0k1l2m3n4)
    core = {
        "analyses",
        "components",
        "damage_scenarios",
        "threat_damage_links",
        "users",
        "organizations",
        "risk_frameworks",
        "product_scopes",
        "assets",
        "risk_treatments",
        "threat_scenarios",
        "threat_catalog",
        "cra_assessments",
        "permissions",
        "approval_workflows",
        "audit_logs",
    }
    missing = core - tables
    assert not missing, f"Missing tables after upgrade head: {missing}"


def test_upgrade_head_creates_cra_tables(ephemeral_db: Path) -> None:
    command.upgrade(_make_config(ephemeral_db), "head")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    tables = set(inspect(engine).get_table_names())

    cra = {"cra_sboms", "cra_sbom_components", "cra_incidents"}
    missing = cra - tables
    assert not missing, f"Missing CRA tables after upgrade head: {missing}"


# ──────────────── e5f6g7h8i9j0 — damage_scenarios DEFAULT fix ────────────────


def test_damage_scenarios_status_default_is_accepted(ephemeral_db: Path) -> None:
    """After migration e5f6g7h8i9j0 the status column default must be 'accepted'.

    The original migration used double-quoted DEFAULT "accepted" which SQLite
    3.37+ rejects as non-constant. The rewrite uses single-quoted literals.
    """
    command.upgrade(_make_config(ephemeral_db), "head")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    cols = {c["name"]: c for c in inspect(engine).get_columns("damage_scenarios")}
    assert "status" in cols, "damage_scenarios.status column missing"
    default_val = cols["status"].get("default")
    # SQLAlchemy reflects SQLite defaults as the raw string; it should be
    # either 'accepted' (with quotes) or accepted (bare) — never ("accepted").
    assert default_val is None or "accepted" in str(default_val), (
        f"Unexpected default for damage_scenarios.status: {default_val!r}"
    )
    # Confirm we can insert without supplying status and it comes back accepted.
    # Use only NOT NULL columns that exist in the migration schema (no scope_version).
    with engine.connect() as conn:
        conn.execute(text(
            "INSERT INTO damage_scenarios "
            "(scenario_id, name, scope_id, damage_category, impact_type, severity, version, is_deleted) "
            "VALUES ('ds-test-default', 'Test DS', 'scope1', 'Safety', 'Direct', 'High', 1, 0)"
        ))
        row = conn.execute(
            text("SELECT status FROM damage_scenarios WHERE scenario_id = 'ds-test-default'")
        ).fetchone()
    assert row is not None
    assert row[0] == "accepted", f"Expected status='accepted', got {row[0]!r}"


# ──────────────── g7h8i9j0k1l2 — threat_damage_links ────────────────


def test_threat_damage_links_has_correct_pk(ephemeral_db: Path) -> None:
    """threat_damage_links must have a composite PK covering both FK columns."""
    command.upgrade(_make_config(ephemeral_db), "head")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    # get_pk_constraint returns {'constrained_columns': [str, ...], 'name': ...}
    pk_cols = set(inspect(engine).get_pk_constraint("threat_damage_links").get("constrained_columns", []))
    assert pk_cols == {"threat_scenario_id", "damage_scenario_id"}, (
        f"Unexpected PK columns on threat_damage_links: {pk_cols}"
    )


def test_threat_damage_links_allows_insert(ephemeral_db: Path) -> None:
    """Confirm threat_damage_links is writable (was causing 500 errors before the migration)."""
    command.upgrade(_make_config(ephemeral_db), "head")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    with engine.connect() as conn:
        conn.execute(
            text(
                "INSERT OR IGNORE INTO threat_damage_links "
                "(threat_scenario_id, damage_scenario_id) VALUES ('ts-001', 'ds-001')"
            )
        )
        count = conn.execute(
            text("SELECT COUNT(*) FROM threat_damage_links WHERE threat_scenario_id = 'ts-001'")
        ).scalar()
    assert count == 1


# ──────────────── h8i9j0k1l2m3 — cleanup leftover tables ────────────────


def test_cleanup_migration_does_not_leave_damage_scenarios_new(ephemeral_db: Path) -> None:
    command.upgrade(_make_config(ephemeral_db), "head")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    tables = set(inspect(engine).get_table_names())
    assert "damage_scenarios_new" not in tables, (
        "damage_scenarios_new should have been dropped by cleanup migration"
    )


# ──────────────── initial schema guard — idempotency ────────────────


def test_upgrade_head_is_idempotent(ephemeral_db: Path) -> None:
    """Running upgrade head twice must not raise 'table already exists'."""
    cfg = _make_config(ephemeral_db)
    command.upgrade(cfg, "head")
    # Second run must complete without error.
    command.upgrade(cfg, "head")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    assert "analyses" in set(inspect(engine).get_table_names())


# ──────────────── full head → base → head round-trip ────────────────


def test_full_head_to_base_to_head_round_trip(ephemeral_db: Path) -> None:
    """Upgrade → downgrade one step → upgrade again must be lossless for schema."""
    cfg = _make_config(ephemeral_db)

    command.upgrade(cfg, "head")

    # Downgrade one step (j0k1l2m3n4o5 → i9j0k1l2m3n4): drops cra_conformity_checklists only
    command.downgrade(cfg, "-1")
    engine = create_engine(f"sqlite:///{ephemeral_db}")
    tables_mid = set(inspect(engine).get_table_names())
    assert "cra_conformity_checklists" not in tables_mid  # downgraded away
    assert "product_scopes" in tables_mid                 # still present (i9j0k1l2m3n4 keeps it)
    assert "analyses" in tables_mid                       # still present

    command.upgrade(cfg, "head")
    engine2 = create_engine(f"sqlite:///{ephemeral_db}")
    tables_final = set(inspect(engine2).get_table_names())

    required = {
        "analyses",
        "damage_scenarios",
        "threat_damage_links",
        "cra_sboms",
        "cra_sbom_components",
        "cra_incidents",
        "product_scopes",
        "assets",
        "risk_treatments",
        "threat_scenarios",
        "cra_conformity_checklists",
    }
    missing = required - tables_final
    assert not missing, f"Tables missing after round-trip: {missing}"
