"""add cra_conformity_checklists table

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-05-05

Art. 13 conformity workflow — tracks the procedural compliance acts beyond Annex I:
conformity assessment, Declaration of Conformity, CE marking, EU registration (Art. 31),
10-year retention plan (Art. 23(1)), and post-market surveillance plan (Art. 13(14)).
"""
from alembic import op
import sqlalchemy as sa

revision = 'j0k1l2m3n4o5'
down_revision = 'i9j0k1l2m3n4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cra_conformity_checklists',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('assessment_id', sa.String(), nullable=False),

        # Art. 32 conformity assessment
        sa.Column('conformity_assessment_done', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('conformity_assessment_module', sa.String(), nullable=True),
        sa.Column('conformity_assessment_date', sa.String(), nullable=True),
        sa.Column('conformity_assessment_notes', sa.Text(), nullable=True),

        # Art. 28 + Annex V — Declaration of Conformity
        sa.Column('doc_signed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('doc_signed_date', sa.String(), nullable=True),
        sa.Column('doc_signatory', sa.String(), nullable=True),
        sa.Column('doc_storage_location', sa.String(), nullable=True),

        # Art. 28 — CE marking
        sa.Column('ce_marking_applied', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('ce_marking_date', sa.String(), nullable=True),
        sa.Column('ce_marking_notes', sa.Text(), nullable=True),

        # Art. 31 — EU central database registration
        sa.Column('eu_registration_done', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('eu_registration_id', sa.String(), nullable=True),
        sa.Column('eu_registration_date', sa.String(), nullable=True),

        # Art. 23(1) — 10-year retention plan
        sa.Column('retention_plan_confirmed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('retention_plan_notes', sa.Text(), nullable=True),

        # Art. 13(14) — post-market surveillance plan
        sa.Column('post_market_plan_confirmed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('post_market_plan_notes', sa.Text(), nullable=True),

        # Art. 14(2) — EOSS published
        sa.Column('eoss_published', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('eoss_published_url', sa.String(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['assessment_id'], ['cra_assessments.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('assessment_id'),
    )
    op.create_index('ix_cra_conformity_checklists_id', 'cra_conformity_checklists', ['id'])
    op.create_index('ix_cra_conformity_checklists_assessment_id', 'cra_conformity_checklists', ['assessment_id'])


def downgrade() -> None:
    op.drop_index('ix_cra_conformity_checklists_assessment_id', table_name='cra_conformity_checklists')
    op.drop_index('ix_cra_conformity_checklists_id', table_name='cra_conformity_checklists')
    op.drop_table('cra_conformity_checklists')
