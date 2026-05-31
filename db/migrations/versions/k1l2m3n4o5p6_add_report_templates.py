"""add_report_templates

Revision ID: k1l2m3n4o5p6
Revises: j0k1l2m3n4o5
Create Date: 2026-05-31 10:00:00.000000

Adds the report_templates table holding reusable, org-scoped report
configurations (serialized ReportConfig). Built-in presets are code-defined
and not stored here.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "k1l2m3n4o5p6"
down_revision = "j0k1l2m3n4o5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "report_templates" in set(inspector.get_table_names()):
        return

    op.create_table(
        "report_templates",
        sa.Column("template_id", sa.String(), primary_key=True, index=True),
        sa.Column(
            "organization_id",
            sa.String(),
            sa.ForeignKey("organizations.organization_id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_report_templates_organization_id",
        "report_templates",
        ["organization_id"],
    )


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    if "report_templates" not in set(inspector.get_table_names()):
        return

    op.drop_index(
        "ix_report_templates_organization_id", table_name="report_templates"
    )
    op.drop_table("report_templates")
