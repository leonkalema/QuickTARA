"""
Add threat scenarios table

Revision ID: add_threat_scenarios
Revises: 
Create Date: 2025-09-04 00:16:21.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = 'add_threat_scenarios'
down_revision = None
depends_on = None


def upgrade():
    """Create threat_scenarios table"""
    op.create_table(
        'threat_scenarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('threat_scenario_id', sa.String(length=50), nullable=False),
        sa.Column('damage_scenario_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('attack_vector', sa.String(length=100), nullable=False),
        sa.Column('scope_id', sa.String(length=50), nullable=False),
        sa.Column('scope_version', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('revision_notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_threat_scenarios_threat_scenario_id', 'threat_scenario_id'),
        sa.Index('ix_threat_scenarios_damage_scenario_id', 'damage_scenario_id'),
        sa.Index('ix_threat_scenarios_scope_id', 'scope_id'),
    )
    
    # Create unique constraint on threat_scenario_id
    op.create_unique_constraint(
        'uq_threat_scenarios_threat_scenario_id',
        'threat_scenarios',
        ['threat_scenario_id']
    )


def downgrade():
    """Drop threat_scenarios table"""
    op.drop_table('threat_scenarios')
