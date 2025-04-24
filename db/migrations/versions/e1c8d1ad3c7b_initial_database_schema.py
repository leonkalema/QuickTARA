"""Initial database schema

Revision ID: e1c8d1ad3c7b
Revises: 
Create Date: 2023-04-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import JSON


# revision identifiers, used by Alembic.
revision = 'e1c8d1ad3c7b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create component_connections table
    op.create_table('component_connections',
        sa.Column('component_id', sa.String(), nullable=False),
        sa.Column('connected_to_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['component_id'], ['components.component_id'], ),
        sa.ForeignKeyConstraint(['connected_to_id'], ['components.component_id'], ),
        sa.PrimaryKeyConstraint('component_id', 'connected_to_id')
    )
    
    # Create components table
    op.create_table('components',
        sa.Column('component_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('safety_level', sa.String(), nullable=False),
        sa.Column('interfaces', JSON(), nullable=True),
        sa.Column('access_points', JSON(), nullable=True),
        sa.Column('data_types', JSON(), nullable=True),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('trust_zone', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('component_id')
    )
    op.create_index(op.f('ix_components_component_id'), 'components', ['component_id'], unique=False)
    
    # Create analyses table
    op.create_table('analyses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('total_components', sa.Integer(), nullable=True),
        sa.Column('total_threats', sa.Integer(), nullable=True),
        sa.Column('critical_components', sa.Integer(), nullable=True),
        sa.Column('high_risk_threats', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analyses_id'), 'analyses', ['id'], unique=False)
    
    # Create component_analyses table
    op.create_table('component_analyses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('analysis_id', sa.String(), nullable=True),
        sa.Column('component_id', sa.String(), nullable=True),
        sa.Column('threats', JSON(), nullable=True),
        sa.Column('stride_analysis', JSON(), nullable=True),
        sa.Column('compliance', JSON(), nullable=True),
        sa.Column('feasibility_assessments', JSON(), nullable=True),
        sa.Column('risk_acceptance', JSON(), nullable=True),
        sa.Column('attack_paths', JSON(), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.ForeignKeyConstraint(['component_id'], ['components.component_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_component_analyses_analysis_id'), 'component_analyses', ['analysis_id'], unique=False)
    op.create_index(op.f('ix_component_analyses_component_id'), 'component_analyses', ['component_id'], unique=False)
    op.create_index(op.f('ix_component_analyses_id'), 'component_analyses', ['id'], unique=False)
    
    # Create reports table
    op.create_table('reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('analysis_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('format', sa.String(), nullable=False),
        sa.Column('report_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('configuration', JSON(), nullable=True),
        sa.Column('error_info', JSON(), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_analysis_id'), 'reports', ['analysis_id'], unique=False)
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_reports_id'), table_name='reports')
    op.drop_index(op.f('ix_reports_analysis_id'), table_name='reports')
    op.drop_table('reports')
    
    op.drop_index(op.f('ix_component_analyses_id'), table_name='component_analyses')
    op.drop_index(op.f('ix_component_analyses_component_id'), table_name='component_analyses')
    op.drop_index(op.f('ix_component_analyses_analysis_id'), table_name='component_analyses')
    op.drop_table('component_analyses')
    
    op.drop_index(op.f('ix_analyses_id'), table_name='analyses')
    op.drop_table('analyses')
    
    op.drop_index(op.f('ix_components_component_id'), table_name='components')
    op.drop_table('components')
    
    op.drop_table('component_connections')
