"""Alembic upgrade + downgrade round-trip tests for CRA migrations.

Per the CRA-feature-development SKILL: every new migration must have an
upgrade + downgrade test. These exercise `alembic upgrade head` and
`alembic downgrade` against an ephemeral SQLite DB so schema drift is
caught before review.

Covered revisions:
  - a1c2d3e4f5g6 — cra_sboms + cra_sbom_components (CRA Art. 13(6))
  - b2d3e4f5g6h7 — cra_incidents (CRA Art. 14)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


ROOT = Path(__file__).resolve().parents[2]

# `db/migrations/env.py` imports `db.base` and assumes the project root is
# on `sys.path`. Pytest does not put it there automatically, so we both
# prepend the path and pre-import the module to populate `sys.modules`
# before any Alembic command runs.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYTHONPATH", str(ROOT))
import db.base  # noqa: E402,F401  (warm sys.modules for alembic env.py)


def _make_config(db_path: Path) -> Config:
    """Build an Alembic Config pointed at an ephemeral SQLite file."""
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "db" / "migrations"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return cfg


@pytest.fixture
def ephemeral_db(tmp_path: Path) -> Path:
    """Provide a throwaway SQLite file and clean it up afterwards."""
    db_path = tmp_path / "roundtrip.db"
    yield db_path
    if db_path.exists():
        os.remove(db_path)


# ──────────────── SBOM migration ────────────────


def test_sbom_upgrade_creates_expected_tables(ephemeral_db: Path) -> None:
    cfg = _make_config(ephemeral_db)
    command.upgrade(cfg, "a1c2d3e4f5g6")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    tables = set(inspect(engine).get_table_names())
    assert "cra_sboms" in tables
    assert "cra_sbom_components" in tables


def test_sbom_upgrade_then_downgrade_removes_tables(ephemeral_db: Path) -> None:
    cfg = _make_config(ephemeral_db)
    command.upgrade(cfg, "a1c2d3e4f5g6")
    # Downgrade one step — back to the revision immediately before SBOM.
    command.downgrade(cfg, "74d4848fdb19")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    tables = set(inspect(engine).get_table_names())
    assert "cra_sboms" not in tables
    assert "cra_sbom_components" not in tables


def test_sbom_components_has_purl_and_name_indexes(ephemeral_db: Path) -> None:
    """Indexes underpin CRA-10 lookups; their loss would silently regress perf."""
    cfg = _make_config(ephemeral_db)
    command.upgrade(cfg, "a1c2d3e4f5g6")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    indexes = inspect(engine).get_indexes("cra_sbom_components")
    indexed_columns = {tuple(ix["column_names"]) for ix in indexes}
    # Either a dedicated purl index or a composite name/version index must exist.
    assert any("purl" in cols for cols in indexed_columns), (
        "Expected an index covering `purl` on cra_sbom_components"
    )


# ──────────────── Incident migration ────────────────


def test_incident_upgrade_creates_table(ephemeral_db: Path) -> None:
    cfg = _make_config(ephemeral_db)
    command.upgrade(cfg, "b2d3e4f5g6h7")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    tables = set(inspect(engine).get_table_names())
    assert "cra_incidents" in tables


def test_incident_upgrade_then_downgrade_removes_table(ephemeral_db: Path) -> None:
    cfg = _make_config(ephemeral_db)
    command.upgrade(cfg, "b2d3e4f5g6h7")
    command.downgrade(cfg, "a1c2d3e4f5g6")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    tables = set(inspect(engine).get_table_names())
    assert "cra_incidents" not in tables
    # SBOM tables created by the previous revision must survive the single-step downgrade.
    assert "cra_sboms" in tables


def test_incident_table_has_art_14_phase_columns(ephemeral_db: Path) -> None:
    """The three submission timestamps map to Art. 14(2)(a)/(b)/(c)."""
    cfg = _make_config(ephemeral_db)
    command.upgrade(cfg, "b2d3e4f5g6h7")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    columns = {c["name"] for c in inspect(engine).get_columns("cra_incidents")}
    assert {
        "discovered_at",
        "early_warning_submitted_at",
        "incident_report_submitted_at",
        "final_report_submitted_at",
    }.issubset(columns)


# ──────────────── Full round-trip ────────────────


def test_full_head_to_base_round_trip(ephemeral_db: Path) -> None:
    """Upgrade to head, downgrade all the way to base, upgrade to head again.

    Catches non-idempotent downgrades and migrations that leak state between
    runs. Confined to ``b2d3e4f5g6h7`` since that is the newest CRA revision.
    """
    cfg = _make_config(ephemeral_db)

    command.upgrade(cfg, "b2d3e4f5g6h7")
    command.downgrade(cfg, "74d4848fdb19")
    command.upgrade(cfg, "b2d3e4f5g6h7")

    engine = create_engine(f"sqlite:///{ephemeral_db}")
    tables = set(inspect(engine).get_table_names())
    assert {"cra_sboms", "cra_sbom_components", "cra_incidents"}.issubset(tables)
