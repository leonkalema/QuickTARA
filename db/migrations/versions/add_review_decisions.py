"""Add review_decisions table

Revision ID: 85b4d7c9e2a1
Revises: f8a52c9271e3
Create Date: 2023-09-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.types import JSON

# revision identifiers, used by Alembic.
revision = '85b4d7c9e2a1'
down_revision = 'f8a52c9271e3'
branch_labels = None
depends_on = None


def table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = Inspector.from_engine(op.get_bind())
    return table_name in inspector.get_table_names()


def upgrade():
    """Add review_decisions table if it doesn't exist"""
    # Skip if table already exists
    if table_exists('review_decisions'):
        return
    
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


def downgrade():
    """Remove review_decisions table"""
    # Only attempt to drop if table exists
    if table_exists('review_decisions'):
        op.drop_index(op.f('ix_review_decisions_component_id'), table_name='review_decisions')
        op.drop_index(op.f('ix_review_decisions_analysis_id'), table_name='review_decisions')
        op.drop_table('review_decisions')
