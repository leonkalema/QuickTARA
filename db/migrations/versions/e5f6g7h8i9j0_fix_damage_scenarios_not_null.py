"""fix_damage_scenarios_not_null

The initial migration created damage_scenarios.sfop_rating_auto_generated as
NOT NULL with no default.  The product-centric DamageScenario ORM model does
not include this legacy column in its INSERT statements, so every new damage
scenario creation fails with:

    sqlite3.IntegrityError: NOT NULL constraint failed:
    damage_scenarios.sfop_rating_auto_generated

Additionally, the status column was stored with a double-quoted DEFAULT
("accepted") which SQLite 3.37+ rejects during table rebuilds (non-constant
expression).  We fix both issues here with a raw-SQL table rebuild so we can
emit exactly the DEFAULT syntax SQLite requires.

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2025-01-08 02:00:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None

# Target schema — all columns with SQLite-safe single-quoted string defaults.
_CREATE_NEW = """
CREATE TABLE _damage_scenarios_new (
    id INTEGER PRIMARY KEY,
    scenario_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    damage_category TEXT NOT NULL DEFAULT 'unknown',
    impact_type TEXT NOT NULL DEFAULT 'Direct',
    confidentiality_impact BOOLEAN DEFAULT 0,
    integrity_impact BOOLEAN DEFAULT 0,
    availability_impact BOOLEAN DEFAULT 0,
    severity TEXT NOT NULL DEFAULT 'Medium',
    impact_details JSON,
    version INTEGER DEFAULT 1,
    revision_notes TEXT,
    is_deleted BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scope_id TEXT NOT NULL DEFAULT '',
    primary_component_id TEXT,
    safety_impact TEXT,
    financial_impact TEXT,
    operational_impact TEXT,
    privacy_impact TEXT,
    impact_rating_notes TEXT,
    sfop_rating_auto_generated BOOLEAN DEFAULT 1,
    sfop_rating_last_edited_by TEXT,
    sfop_rating_last_edited_at TIMESTAMP,
    sfop_rating_override_reason TEXT,
    violated_properties JSON DEFAULT '[]',
    category TEXT,
    is_current BOOLEAN DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'accepted'
)
"""

_NEW_COLS = [
    'id', 'scenario_id', 'name', 'description', 'damage_category',
    'impact_type', 'confidentiality_impact', 'integrity_impact',
    'availability_impact', 'severity', 'impact_details', 'version',
    'revision_notes', 'is_deleted', 'created_at', 'updated_at', 'scope_id',
    'primary_component_id', 'safety_impact', 'financial_impact',
    'operational_impact', 'privacy_impact', 'impact_rating_notes',
    'sfop_rating_auto_generated', 'sfop_rating_last_edited_by',
    'sfop_rating_last_edited_at', 'sfop_rating_override_reason',
    'violated_properties', 'category', 'is_current', 'status',
]


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'damage_scenarios' not in inspector.get_table_names():
        return

    existing = {c['name'] for c in inspector.get_columns('damage_scenarios')}
    # Only copy columns present in both old and new table
    common = [c for c in _NEW_COLS if c in existing]
    cols = ', '.join(common)

    conn.execute(sa.text("PRAGMA foreign_keys=OFF"))
    conn.execute(sa.text(_CREATE_NEW))
    conn.execute(sa.text(f"INSERT INTO _damage_scenarios_new ({cols}) SELECT {cols} FROM damage_scenarios"))
    conn.execute(sa.text("DROP TABLE damage_scenarios"))
    conn.execute(sa.text("ALTER TABLE _damage_scenarios_new RENAME TO damage_scenarios"))
    conn.execute(sa.text("PRAGMA foreign_keys=ON"))


def downgrade():
    pass  # intentionally a no-op
