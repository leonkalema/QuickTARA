"""
Add risk framework table for risk calculation framework

Revision ID: b1e9c3d7a2f5
Revises: add_scope_id_to_components
Create Date: 2025-04-26 02:17:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'b1e9c3d7a2f5'
down_revision = 'add_scope_id_to_components'
branch_labels = None
depends_on = None


def upgrade():
    # Create risk_frameworks table
    op.create_table(
        'risk_frameworks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('framework_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('impact_definitions', sa.JSON(), nullable=False),
        sa.Column('likelihood_definitions', sa.JSON(), nullable=False),
        sa.Column('risk_matrix', sa.JSON(), nullable=False),
        sa.Column('risk_thresholds', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_risk_frameworks_framework_id'), 'risk_frameworks', ['framework_id'], unique=True)
    op.create_index(op.f('ix_risk_frameworks_id'), 'risk_frameworks', ['id'], unique=False)


def downgrade():
    # Drop risk_frameworks table
    op.drop_index(op.f('ix_risk_frameworks_id'), table_name='risk_frameworks')
    op.drop_index(op.f('ix_risk_frameworks_framework_id'), table_name='risk_frameworks')
    op.drop_table('risk_frameworks')
