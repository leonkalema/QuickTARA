"""fix_damage_scenarios_not_null

The initial migration created damage_scenarios.sfop_rating_auto_generated as
NOT NULL with no default.  The product-centric DamageScenario ORM model does
not include this legacy column in its INSERT statements, so every new damage
scenario creation fails with:

    sqlite3.IntegrityError: NOT NULL constraint failed:
    damage_scenarios.sfop_rating_auto_generated

Fix: use batch_alter (full table rebuild in SQLite) to add a server_default
of True (1) so rows inserted without this column get a safe fallback.

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2025-01-08 02:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if 'damage_scenarios' not in inspector.get_table_names():
        return

    # SQLite cannot ALTER COLUMN in-place; batch mode rewrites the table.
    with op.batch_alter_table('damage_scenarios', schema=None) as batch_op:
        batch_op.alter_column(
            'sfop_rating_auto_generated',
            existing_type=sa.Boolean(),
            nullable=True,
            server_default='1',
        )


def downgrade():
    pass  # intentionally a no-op
