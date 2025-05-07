"""
Add CIA security properties to components table

Revision ID: 006
Revises: 005_add_attack_path_analyses_table
Create Date: 2025-05-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005_add_attack_path_analyses_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add security properties columns to components table
    op.add_column('components', sa.Column('confidentiality', sa.String(), nullable=True))
    op.add_column('components', sa.Column('integrity', sa.String(), nullable=True))
    op.add_column('components', sa.Column('availability', sa.String(), nullable=True))
    op.add_column('components', sa.Column('authenticity_required', sa.Boolean(), nullable=True))
    op.add_column('components', sa.Column('authorization_required', sa.Boolean(), nullable=True))
    
    # Set default values for existing records
    op.execute("UPDATE components SET confidentiality = 'Medium', integrity = 'Medium', availability = 'Medium', authenticity_required = false, authorization_required = false")


def downgrade():
    # Drop security properties columns
    op.drop_column('components', 'confidentiality')
    op.drop_column('components', 'integrity')
    op.drop_column('components', 'availability')
    op.drop_column('components', 'authenticity_required')
    op.drop_column('components', 'authorization_required')
