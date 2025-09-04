"""Make primary_component_id nullable in damage_scenarios

Revision ID: 008_make_primary_component_id_nullable
Revises: 007_add_damage_scenario_tables
Create Date: 2025-09-04 10:06:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008_make_primary_component_id_nullable'
down_revision = '007_add_damage_scenario_tables'
branch_labels = None
depends_on = None

def upgrade():
    """Make primary_component_id nullable to allow damage scenarios without asset links"""
    # SQLite doesn't support ALTER COLUMN directly, so we need to recreate the table
    with op.batch_alter_table('damage_scenarios', schema=None) as batch_op:
        batch_op.alter_column('primary_component_id',
                            existing_type=sa.String(),
                            nullable=True)

def downgrade():
    """Revert primary_component_id to NOT NULL"""
    with op.batch_alter_table('damage_scenarios', schema=None) as batch_op:
        batch_op.alter_column('primary_component_id',
                            existing_type=sa.String(),
                            nullable=False)
