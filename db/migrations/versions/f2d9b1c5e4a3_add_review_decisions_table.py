"""Add review decisions table

Revision ID: f2d9b1c5e4a3
Revises: e1c8d1ad3c7b
Create Date: 2023-04-24 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import JSON


# revision identifiers, used by Alembic.
revision = 'f2d9b1c5e4a3'
down_revision = 'e1c8d1ad3c7b'
branch_labels = None
depends_on = None


def upgrade():
    # Create review_decisions table
    op.create_table('review_decisions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('analysis_id', sa.String(), nullable=False),
        sa.Column('component_id', sa.String(), nullable=False),
        sa.Column('threat_id', sa.String(), nullable=False),
        sa.Column('original_decision', sa.String(), nullable=False),
        sa.Column('final_decision', sa.String(), nullable=False),
        sa.Column('reviewer', sa.String(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('additional_notes', sa.Text(), nullable=True),
        sa.Column('review_date', sa.String(), nullable=False),
        sa.Column('evidence_references', JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ),
        sa.ForeignKeyConstraint(['component_id'], ['components.component_id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_review_decisions_analysis_id'), 'review_decisions', ['analysis_id'], unique=False)
    op.create_index(op.f('ix_review_decisions_component_id'), 'review_decisions', ['component_id'], unique=False)
    op.create_index(op.f('ix_review_decisions_id'), 'review_decisions', ['id'], unique=False)
    
    # Create unique constraint on analysis_id, component_id, threat_id
    op.create_index(
        'uix_review_decisions_analysis_component_threat',
        'review_decisions',
        ['analysis_id', 'component_id', 'threat_id'],
        unique=True
    )


def downgrade():
    # Drop review_decisions table
    op.drop_index('uix_review_decisions_analysis_component_threat', table_name='review_decisions')
    op.drop_index(op.f('ix_review_decisions_id'), table_name='review_decisions')
    op.drop_index(op.f('ix_review_decisions_component_id'), table_name='review_decisions')
    op.drop_index(op.f('ix_review_decisions_analysis_id'), table_name='review_decisions')
    op.drop_table('review_decisions')
