"""
Add attack path analyses table

Revision ID: 005
Revises: 004
Create Date: 2025-05-01 18:06:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Create attack_path_analyses table to store analysis metadata
    op.create_table('attack_path_analyses',
        sa.Column('analysis_id', sa.String(), primary_key=True, index=True),
        sa.Column('component_count', sa.Integer(), nullable=False),
        sa.Column('total_paths', sa.Integer(), nullable=False),
        sa.Column('high_risk_paths', sa.Integer(), nullable=False),
        sa.Column('total_chains', sa.Integer(), nullable=False),
        sa.Column('high_risk_chains', sa.Integer(), nullable=False),
        sa.Column('entry_points', sa.JSON(), nullable=True),
        sa.Column('critical_targets', sa.JSON(), nullable=True),
        sa.Column('scope_id', sa.String(), nullable=True),
        sa.Column('primary_component_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=datetime.now)
    )
    
    # Create foreign key constraints
    op.create_foreign_key(
        'fk_attack_path_analyses_scope_id',
        'attack_path_analyses', 'system_scopes',
        ['scope_id'], ['scope_id'],
        ondelete='SET NULL'
    )
    
    op.create_foreign_key(
        'fk_attack_path_analyses_primary_component_id',
        'attack_path_analyses', 'components',
        ['primary_component_id'], ['component_id'],
        ondelete='SET NULL'
    )
    
    # Create indexes for better query performance
    op.create_index('idx_attack_path_analyses_scope_id', 'attack_path_analyses', ['scope_id'])
    op.create_index('idx_attack_path_analyses_primary_component_id', 'attack_path_analyses', ['primary_component_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_attack_path_analyses_primary_component_id', table_name='attack_path_analyses')
    op.drop_index('idx_attack_path_analyses_scope_id', table_name='attack_path_analyses')
    
    # Drop foreign keys
    op.drop_constraint('fk_attack_path_analyses_primary_component_id', 'attack_path_analyses', type_='foreignkey')
    op.drop_constraint('fk_attack_path_analyses_scope_id', 'attack_path_analyses', type_='foreignkey')
    
    # Drop the table
    op.drop_table('attack_path_analyses')
