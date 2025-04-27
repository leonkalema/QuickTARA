"""
Add attack path analysis tables

Revision ID: 004
Revises: 003
Create Date: 2025-04-27 00:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime
import uuid

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create attack steps table
    op.create_table('attack_steps',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('step_id', sa.String(), unique=True, index=True),
        sa.Column('path_id', sa.String(), nullable=False),
        sa.Column('component_id', sa.String(), nullable=False),
        sa.Column('step_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('vulnerability_ids', sa.JSON(), nullable=True),
        sa.Column('threat_ids', sa.JSON(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.now)
    )
    
    # Create attack paths table
    op.create_table('attack_paths',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('path_id', sa.String(), unique=True, index=True),
        sa.Column('analysis_id', sa.String(), nullable=False),
        sa.Column('scope_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('path_type', sa.String(), nullable=False),
        sa.Column('complexity', sa.String(), nullable=False),
        sa.Column('entry_point_id', sa.String(), nullable=False),
        sa.Column('target_id', sa.String(), nullable=False),
        sa.Column('success_likelihood', sa.Float(), nullable=False),
        sa.Column('impact', sa.JSON(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.Column('updated_at', sa.DateTime(), default=datetime.now, onupdate=datetime.now)
    )
    
    # Create attack chains table
    op.create_table('attack_chains',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('chain_id', sa.String(), unique=True, index=True),
        sa.Column('analysis_id', sa.String(), nullable=False),
        sa.Column('scope_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('entry_points', sa.JSON(), nullable=False),
        sa.Column('targets', sa.JSON(), nullable=False),
        sa.Column('attack_goal', sa.String(), nullable=False),
        sa.Column('complexity', sa.String(), nullable=False),
        sa.Column('success_likelihood', sa.Float(), nullable=False),
        sa.Column('impact', sa.JSON(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.now),
        sa.Column('updated_at', sa.DateTime(), default=datetime.now, onupdate=datetime.now)
    )
    
    # Create association table for attack chains and paths
    op.create_table('attack_chain_paths',
        sa.Column('chain_id', sa.String(), sa.ForeignKey('attack_chains.chain_id'), primary_key=True),
        sa.Column('path_id', sa.String(), sa.ForeignKey('attack_paths.path_id'), primary_key=True)
    )
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_attack_steps_path_id',
        'attack_steps', 'attack_paths',
        ['path_id'], ['path_id']
    )
    
    op.create_foreign_key(
        'fk_attack_steps_component_id',
        'attack_steps', 'components',
        ['component_id'], ['component_id']
    )
    
    op.create_foreign_key(
        'fk_attack_paths_analysis_id',
        'attack_paths', 'analyses',
        ['analysis_id'], ['id']
    )
    
    op.create_foreign_key(
        'fk_attack_paths_scope_id',
        'attack_paths', 'system_scopes',
        ['scope_id'], ['scope_id']
    )
    
    op.create_foreign_key(
        'fk_attack_paths_entry_point_id',
        'attack_paths', 'components',
        ['entry_point_id'], ['component_id']
    )
    
    op.create_foreign_key(
        'fk_attack_paths_target_id',
        'attack_paths', 'components',
        ['target_id'], ['component_id']
    )
    
    op.create_foreign_key(
        'fk_attack_chains_analysis_id',
        'attack_chains', 'analyses',
        ['analysis_id'], ['id']
    )
    
    op.create_foreign_key(
        'fk_attack_chains_scope_id',
        'attack_chains', 'system_scopes',
        ['scope_id'], ['scope_id']
    )
    
    # Create indexes for better query performance
    op.create_index('idx_attack_steps_path_id', 'attack_steps', ['path_id'])
    op.create_index('idx_attack_steps_component_id', 'attack_steps', ['component_id'])
    op.create_index('idx_attack_paths_analysis_id', 'attack_paths', ['analysis_id'])
    op.create_index('idx_attack_paths_scope_id', 'attack_paths', ['scope_id'])
    op.create_index('idx_attack_chains_analysis_id', 'attack_chains', ['analysis_id'])
    op.create_index('idx_attack_chains_scope_id', 'attack_chains', ['scope_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_attack_chains_scope_id', table_name='attack_chains')
    op.drop_index('idx_attack_chains_analysis_id', table_name='attack_chains')
    op.drop_index('idx_attack_paths_scope_id', table_name='attack_paths')
    op.drop_index('idx_attack_paths_analysis_id', table_name='attack_paths')
    op.drop_index('idx_attack_steps_component_id', table_name='attack_steps')
    op.drop_index('idx_attack_steps_path_id', table_name='attack_steps')
    
    # Drop foreign keys
    op.drop_constraint('fk_attack_chains_scope_id', 'attack_chains', type_='foreignkey')
    op.drop_constraint('fk_attack_chains_analysis_id', 'attack_chains', type_='foreignkey')
    op.drop_constraint('fk_attack_paths_target_id', 'attack_paths', type_='foreignkey')
    op.drop_constraint('fk_attack_paths_entry_point_id', 'attack_paths', type_='foreignkey')
    op.drop_constraint('fk_attack_paths_scope_id', 'attack_paths', type_='foreignkey')
    op.drop_constraint('fk_attack_paths_analysis_id', 'attack_paths', type_='foreignkey')
    op.drop_constraint('fk_attack_steps_component_id', 'attack_steps', type_='foreignkey')
    op.drop_constraint('fk_attack_steps_path_id', 'attack_steps', type_='foreignkey')
    
    # Drop tables
    op.drop_table('attack_chain_paths')
    op.drop_table('attack_chains')
    op.drop_table('attack_paths')
    op.drop_table('attack_steps')
