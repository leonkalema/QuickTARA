"""create_attack_paths

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2026-06-03 13:00:00.000000

Creates the attack_paths table used by api/models/simple_attack_path.py
(AttackPathDB, string primary key attack_path_id). This table was previously
only created via create_all on dev machines and was missing from the migration
chain, so fresh migration-only deployments lacked it. Its absence caused
GET /api/attack-paths/product/{id} to 500 on the Risk Assessment page.

Guarded with an inspector check so deployments that already have the table
(bootstrapped via create_all) upgrade cleanly.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "l2m3n4o5p6q7"
down_revision = "k1l2m3n4o5p6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "attack_paths" in set(inspector.get_table_names()):
        return

    op.create_table(
        "attack_paths",
        sa.Column("attack_path_id", sa.String(), primary_key=True),
        sa.Column("threat_scenario_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("attack_steps", sa.Text(), nullable=False),
        sa.Column("elapsed_time", sa.Integer(), nullable=False),
        sa.Column("specialist_expertise", sa.Integer(), nullable=False),
        sa.Column("knowledge_of_target", sa.Integer(), nullable=False),
        sa.Column("window_of_opportunity", sa.Integer(), nullable=False),
        sa.Column("equipment", sa.Integer(), nullable=False),
        sa.Column("overall_rating", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_attack_paths_threat_scenario_id",
        "attack_paths",
        ["threat_scenario_id"],
    )


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "attack_paths" not in set(inspector.get_table_names()):
        return

    op.drop_index(
        "ix_attack_paths_threat_scenario_id", table_name="attack_paths"
    )
    op.drop_table("attack_paths")
