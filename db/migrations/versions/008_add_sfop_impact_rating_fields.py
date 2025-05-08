"""
Add SFOP impact rating fields to damage scenarios

Revision ID: 008_add_sfop_impact_rating_fields
Revises: 007_add_damage_scenario_tables
Create Date: 2025-05-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic
revision = '008_add_sfop_impact_rating_fields'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    # Add SFOP impact rating fields to damage_scenarios table
    
    # SFOP rating fields
    op.add_column('damage_scenarios', sa.Column('safety_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('financial_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('operational_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('privacy_impact', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('impact_rating_notes', sa.Text(), nullable=True))
    
    # Audit fields for regulatory compliance (UN R155 and ISO 21434)
    op.add_column('damage_scenarios', sa.Column('sfop_rating_auto_generated', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('damage_scenarios', sa.Column('sfop_rating_last_edited_by', sa.String(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('sfop_rating_last_edited_at', sa.DateTime(), nullable=True))
    op.add_column('damage_scenarios', sa.Column('sfop_rating_override_reason', sa.Text(), nullable=True))


def downgrade():
    # Remove SFOP impact rating fields from damage_scenarios table
    
    # Audit fields
    op.drop_column('damage_scenarios', 'sfop_rating_override_reason')
    op.drop_column('damage_scenarios', 'sfop_rating_last_edited_at')
    op.drop_column('damage_scenarios', 'sfop_rating_last_edited_by')
    op.drop_column('damage_scenarios', 'sfop_rating_auto_generated')
    
    # SFOP rating fields
    op.drop_column('damage_scenarios', 'impact_rating_notes')
    op.drop_column('damage_scenarios', 'privacy_impact')
    op.drop_column('damage_scenarios', 'operational_impact')
    op.drop_column('damage_scenarios', 'financial_impact')
    op.drop_column('damage_scenarios', 'safety_impact')
