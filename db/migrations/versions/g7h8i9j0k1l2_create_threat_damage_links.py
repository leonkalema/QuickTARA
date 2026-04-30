"""create_threat_damage_links

threat_damage_links is used everywhere via raw SQL (INSERT OR IGNORE, SELECT,
DELETE) but was never created by any migration or ORM create_all call, so every
threat scenario creation fails with 'no such table: threat_damage_links'.

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2025-01-10 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'g7h8i9j0k1l2'
down_revision = 'f6g7h8i9j0k1'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if 'threat_damage_links' in inspector.get_table_names():
        return

    op.create_table(
        'threat_damage_links',
        sa.Column('threat_scenario_id', sa.String(), nullable=False),
        sa.Column('damage_scenario_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('threat_scenario_id', 'damage_scenario_id'),
    )


def downgrade():
    op.drop_table('threat_damage_links')
