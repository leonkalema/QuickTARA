"""fix_damage_scenarios_is_deleted_default

The initial migration created damage_scenarios.is_deleted as nullable with no
server_default.  The product-centric DamageScenario ORM does not include
is_deleted in its INSERT statements, so newly created rows have is_deleted=NULL.

The list query filters with `is_deleted == False` which uses SQL `= 0` and
does not match NULL rows, causing every newly created damage scenario to
disappear from the list immediately after creation.

Fix: add server_default=0 (False) so omitted inserts default to not-deleted.
The Python service filter has also been updated to use IS NOT TRUE (NULL-safe).

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2025-01-09 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'f6g7h8i9j0k1'
down_revision = 'e5f6g7h8i9j0'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if 'damage_scenarios' not in inspector.get_table_names():
        return

    with op.batch_alter_table('damage_scenarios', schema=None) as batch_op:
        batch_op.alter_column(
            'is_deleted',
            existing_type=sa.Boolean(),
            nullable=True,
            server_default='0',
        )


def downgrade():
    pass
