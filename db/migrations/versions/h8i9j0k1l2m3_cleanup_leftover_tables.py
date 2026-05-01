"""cleanup_leftover_tables

Drop damage_scenarios_new which was left behind by a previous failed or manual
migration attempt. It is not referenced by any code.

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2025-01-11 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'h8i9j0k1l2m3'
down_revision = 'g7h8i9j0k1l2'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if 'damage_scenarios_new' in inspector.get_table_names():
        op.drop_table('damage_scenarios_new')


def downgrade():
    pass
