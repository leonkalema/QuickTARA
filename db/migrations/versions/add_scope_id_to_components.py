"""add scope_id to components

Revision ID: add_scope_id_column
Revises: f2d9b1c5e4a3_add_review_decisions_table
Create Date: 2025-04-26 01:12:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_scope_id_column'
down_revision = 'f2d9b1c5e4a3_add_review_decisions_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create scope ID column
    with op.batch_alter_table('components') as batch_op:
        batch_op.add_column(sa.Column('scope_id', sa.String(), nullable=True))
        batch_op.create_foreign_key(
            'fk_component_scope',
            'system_scopes',
            ['scope_id'],
            ['scope_id']
        )


def downgrade():
    # Remove scope ID column
    with op.batch_alter_table('components') as batch_op:
        batch_op.drop_constraint('fk_component_scope', type_='foreignkey')
        batch_op.drop_column('scope_id')
