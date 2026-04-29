"""add_product_damage_scenario_columns

Adds columns required by db.product_asset_models.DamageScenario that were
missing from the table created by the initial legacy migration:

  - violated_properties  (JSON)   — selected by ProductDamageScenario ORM
  - category             (String) — optional free-text category tag
  - is_current           (Boolean, default True) — used by Annex-VII query filter

Revision ID: c3d4e5f6g7h8
Revises: b2d3e4f5g6h7
Create Date: 2025-01-08 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'c3d4e5f6g7h8'
down_revision = 'b2d3e4f5g6h7'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())

    # Only touch damage_scenarios if the table exists
    if 'damage_scenarios' not in inspector.get_table_names():
        return

    existing_cols = {c['name'] for c in inspector.get_columns('damage_scenarios')}

    with op.batch_alter_table('damage_scenarios', schema=None) as batch_op:
        if 'violated_properties' not in existing_cols:
            # nullable=True so existing rows don't need a value; server_default
            # gives new-enough SQLite a safe fallback for bulk backfills.
            batch_op.add_column(
                sa.Column('violated_properties', sa.JSON(), nullable=True,
                          server_default='[]')
            )
        if 'category' not in existing_cols:
            batch_op.add_column(
                sa.Column('category', sa.String(), nullable=True)
            )
        if 'is_current' not in existing_cols:
            batch_op.add_column(
                sa.Column('is_current', sa.Boolean(), nullable=True,
                          server_default='1')
            )


def downgrade():
    inspector = sa.inspect(op.get_bind())
    if 'damage_scenarios' not in inspector.get_table_names():
        return

    existing_cols = {c['name'] for c in inspector.get_columns('damage_scenarios')}

    with op.batch_alter_table('damage_scenarios', schema=None) as batch_op:
        if 'is_current' in existing_cols:
            batch_op.drop_column('is_current')
        if 'category' in existing_cols:
            batch_op.drop_column('category')
        if 'violated_properties' in existing_cols:
            batch_op.drop_column('violated_properties')
