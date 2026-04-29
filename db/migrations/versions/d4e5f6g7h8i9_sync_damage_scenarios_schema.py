"""sync_damage_scenarios_schema

Safety-net migration: ensures every column declared in
db.product_asset_models.DamageScenario exists in the damage_scenarios table.

Different installs can end up with different subsets of columns depending on
whether the table was created by Alembic (legacy schema), by
ProductBase.metadata.create_all() from a historical model snapshot, or by a
combination of the two.  This migration adds any column that is still absent,
making the result idempotent regardless of starting state.

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2025-01-08 01:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'd4e5f6g7h8i9'
down_revision = 'c3d4e5f6g7h8'
branch_labels = None
depends_on = None

# Every column declared in db.product_asset_models.DamageScenario, with its
# SQLAlchemy type and a safe server_default for existing rows.
_REQUIRED_COLUMNS = [
    ('name',                  sa.String(),   None),
    ('description',           sa.Text(),     None),
    ('scope_id',              sa.String(),   None),
    ('violated_properties',   sa.JSON(),     '[]'),
    ('category',              sa.String(),   None),
    ('damage_category',       sa.String(),   "'unknown'"),
    ('impact_type',           sa.String(),   "'Direct'"),
    ('severity',              sa.String(),   "'Medium'"),
    ('confidentiality_impact',sa.Boolean(),  '0'),
    ('integrity_impact',      sa.Boolean(),  '0'),
    ('availability_impact',   sa.Boolean(),  '0'),
    ('primary_component_id',  sa.String(),   None),
    ('safety_impact',         sa.String(),   "'negligible'"),
    ('financial_impact',      sa.String(),   "'negligible'"),
    ('operational_impact',    sa.String(),   "'negligible'"),
    ('privacy_impact',        sa.String(),   "'negligible'"),
    ('status',                sa.String(),   "'accepted'"),
    ('version',               sa.Integer(),  '1'),
    ('is_current',            sa.Boolean(),  '1'),
    ('revision_notes',        sa.Text(),     None),
    ('created_at',            sa.DateTime(), None),
    ('updated_at',            sa.DateTime(), None),
]


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if 'damage_scenarios' not in inspector.get_table_names():
        return

    existing = {c['name'] for c in inspector.get_columns('damage_scenarios')}

    with op.batch_alter_table('damage_scenarios', schema=None) as batch_op:
        for col_name, col_type, server_default in _REQUIRED_COLUMNS:
            if col_name not in existing:
                batch_op.add_column(
                    sa.Column(col_name, col_type, nullable=True,
                              server_default=server_default)
                )


def downgrade():
    pass  # intentionally a no-op — we don't want to drop data on rollback
