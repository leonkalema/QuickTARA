"""add_cra_incidents

Revision ID: b2d3e4f5g6h7
Revises: a1c2d3e4f5g6
Create Date: 2026-04-27 07:00:00.000000

CRA Art. 14 — adds the cra_incidents table for tracking 24h / 72h / 14d
ENISA reporting obligations.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2d3e4f5g6h7"
down_revision = "a1c2d3e4f5g6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "cra_incidents" in set(inspector.get_table_names()):
        return

    op.create_table(
        "cra_incidents",
        sa.Column("id", sa.String(), primary_key=True, index=True),
        sa.Column(
            "assessment_id",
            sa.String(),
            sa.ForeignKey("cra_assessments.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("product_id", sa.String(), nullable=True),
        sa.Column("incident_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("corrective_measure_available_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("early_warning_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("incident_report_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("final_report_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actively_exploited", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("member_states_affected", sa.Text(), nullable=True),
        sa.Column("product_description", sa.Text(), nullable=True),
        sa.Column("vulnerability_nature", sa.Text(), nullable=True),
        sa.Column("mitigations_taken", sa.Text(), nullable=True),
        sa.Column("mitigations_recommended", sa.Text(), nullable=True),
        sa.Column("vulnerability_description", sa.Text(), nullable=True),
        sa.Column("impact_description", sa.Text(), nullable=True),
        sa.Column("malicious_actor_info", sa.Text(), nullable=True),
        sa.Column("fixes_applied", sa.Text(), nullable=True),
        sa.Column("cve_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_cra_incidents_status", "cra_incidents", ["status"])
    op.create_index("ix_cra_incidents_discovered_at", "cra_incidents", ["discovered_at"])
    op.create_index("ix_cra_incidents_assessment_id", "cra_incidents", ["assessment_id"])


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "cra_incidents" not in set(inspector.get_table_names()):
        return

    op.drop_index("ix_cra_incidents_assessment_id", table_name="cra_incidents")
    op.drop_index("ix_cra_incidents_discovered_at", table_name="cra_incidents")
    op.drop_index("ix_cra_incidents_status", table_name="cra_incidents")
    op.drop_table("cra_incidents")
