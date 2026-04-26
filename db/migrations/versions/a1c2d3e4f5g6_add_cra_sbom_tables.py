"""add_cra_sbom_tables

Revision ID: a1c2d3e4f5g6
Revises: 74d4848fdb19
Create Date: 2026-04-26 09:30:00.000000

CRA Art. 13(6) — adds storage for uploaded SBOMs and their flattened
components, attached to a CRA assessment.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1c2d3e4f5g6"
down_revision = "74d4848fdb19"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = set(inspector.get_table_names())

    if "cra_sboms" not in existing_tables:
        op.create_table(
            "cra_sboms",
            sa.Column("id", sa.String(), primary_key=True, index=True),
            sa.Column(
                "assessment_id",
                sa.String(),
                sa.ForeignKey("cra_assessments.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("sbom_format", sa.String(), nullable=False),
            sa.Column("spec_version", sa.String(), nullable=False),
            sa.Column("serial_number", sa.String(), nullable=True),
            sa.Column("document_name", sa.String(), nullable=True),
            sa.Column("primary_component_name", sa.String(), nullable=True),
            sa.Column("primary_component_version", sa.String(), nullable=True),
            sa.Column("component_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("raw_size_bytes", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("uploaded_at", sa.DateTime(), nullable=False),
            sa.Column("uploaded_by", sa.String(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
        )

    if "cra_sbom_components" not in existing_tables:
        op.create_table(
            "cra_sbom_components",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "sbom_id",
                sa.String(),
                sa.ForeignKey("cra_sboms.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("bom_ref", sa.String(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("version", sa.String(), nullable=True),
            sa.Column("component_type", sa.String(), nullable=True),
            sa.Column("purl", sa.String(), nullable=True),
            sa.Column("cpe", sa.String(), nullable=True),
            sa.Column("supplier", sa.String(), nullable=True),
            sa.Column("licenses", sa.Text(), nullable=True),
            sa.Column("hashes", sa.Text(), nullable=True),
        )
        op.create_index(
            "ix_cra_sbom_components_purl",
            "cra_sbom_components",
            ["purl"],
        )
        op.create_index(
            "ix_cra_sbom_components_name_version",
            "cra_sbom_components",
            ["name", "version"],
        )


def downgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = set(inspector.get_table_names())

    if "cra_sbom_components" in existing_tables:
        op.drop_index(
            "ix_cra_sbom_components_name_version",
            table_name="cra_sbom_components",
        )
        op.drop_index(
            "ix_cra_sbom_components_purl",
            table_name="cra_sbom_components",
        )
        op.drop_table("cra_sbom_components")

    if "cra_sboms" in existing_tables:
        op.drop_table("cra_sboms")
