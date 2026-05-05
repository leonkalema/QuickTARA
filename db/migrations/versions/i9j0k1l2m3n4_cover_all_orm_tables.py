"""cover_all_orm_tables

Create all ORM-defined tables that were previously only bootstrapped via
Base.metadata.create_all(). After this migration, alembic alone is sufficient
to build a complete schema on a fresh database.

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-05-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'i9j0k1l2m3n4'
down_revision = 'h8i9j0k1l2m3'
branch_labels = None
depends_on = None


def upgrade():
    # ── Tables with no FK dependencies ───────────────────────────────────────
    op.create_table('approval_workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artifact_type', sa.String(length=50), nullable=False),
        sa.Column('artifact_id', sa.String(length=100), nullable=False),
        sa.Column('scope_id', sa.String(length=100), nullable=True),
        sa.Column('current_state', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('assigned_reviewer', sa.String(length=100), nullable=True),
        sa.Column('submitted_for_review_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('released_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_by', sa.String(length=100), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('released_by', sa.String(length=100), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approval_workflows_artifact_id', 'approval_workflows', ['artifact_id'])
    op.create_index('ix_approval_workflows_artifact_type', 'approval_workflows', ['artifact_type'])
    op.create_index('ix_approval_workflows_scope_id', 'approval_workflows', ['scope_id'])

    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('artifact_type', sa.String(length=50), nullable=False),
        sa.Column('artifact_id', sa.String(length=100), nullable=False),
        sa.Column('scope_id', sa.String(length=100), nullable=True),
        sa.Column('action', sa.String(length=30), nullable=False),
        sa.Column('performed_by', sa.String(length=100), nullable=False),
        sa.Column('performed_at', sa.DateTime(), nullable=False),
        sa.Column('field_changed', sa.String(length=100), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_logs_artifact_id', 'audit_logs', ['artifact_id'])
    op.create_index('ix_audit_logs_artifact_type', 'audit_logs', ['artifact_type'])
    op.create_index('ix_audit_logs_scope_id', 'audit_logs', ['scope_id'])

    op.create_table('evidence_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('evidence_id', sa.String(length=100), nullable=False),
        sa.Column('artifact_type', sa.String(length=50), nullable=False),
        sa.Column('artifact_id', sa.String(length=100), nullable=False),
        sa.Column('scope_id', sa.String(length=100), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('file_hash', sa.String(length=128), nullable=True),
        sa.Column('evidence_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.String(length=100), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evidence_attachments_artifact_id', 'evidence_attachments', ['artifact_id'])
    op.create_index('ix_evidence_attachments_artifact_type', 'evidence_attachments', ['artifact_type'])
    op.create_index('ix_evidence_attachments_evidence_id', 'evidence_attachments', ['evidence_id'])
    op.create_index('ix_evidence_attachments_scope_id', 'evidence_attachments', ['scope_id'])

    op.create_table('permissions',
        sa.Column('permission_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('resource', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('permission_id'),
        sa.UniqueConstraint('name'),
    )

    op.create_table('product_scopes',
        sa.Column('scope_id', sa.String(), nullable=False),
        sa.Column('organization_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('product_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('safety_level', sa.String(), nullable=False),
        sa.Column('interfaces', sa.JSON(), nullable=True),
        sa.Column('access_points', sa.JSON(), nullable=True),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('trust_zone', sa.String(), nullable=False),
        sa.Column('boundaries', sa.JSON(), nullable=True),
        sa.Column('objectives', sa.JSON(), nullable=True),
        sa.Column('stakeholders', sa.JSON(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False),
        sa.Column('revision_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('scope_id'),
    )
    op.create_index('ix_product_scopes_organization_id', 'product_scopes', ['organization_id'])
    op.create_index('ix_product_scopes_scope_id', 'product_scopes', ['scope_id'])

    op.create_table('tara_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('snapshot_id', sa.String(length=100), nullable=False),
        sa.Column('scope_id', sa.String(length=100), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('version_label', sa.String(length=50), nullable=True),
        sa.Column('asset_count', sa.Integer(), nullable=False),
        sa.Column('damage_scenario_count', sa.Integer(), nullable=False),
        sa.Column('threat_scenario_count', sa.Integer(), nullable=False),
        sa.Column('attack_path_count', sa.Integer(), nullable=False),
        sa.Column('risk_treatment_count', sa.Integer(), nullable=False),
        sa.Column('snapshot_data', sa.JSON(), nullable=False),
        sa.Column('workflow_state', sa.String(length=20), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tara_snapshots_scope_id', 'tara_snapshots', ['scope_id'])
    op.create_index('ix_tara_snapshots_snapshot_id', 'tara_snapshots', ['snapshot_id'])

    op.create_table('threat_catalog',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('stride_category', sa.String(), nullable=False),
        sa.Column('applicable_component_types', sa.JSON(), nullable=True),
        sa.Column('applicable_trust_zones', sa.JSON(), nullable=True),
        sa.Column('attack_vectors', sa.JSON(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('typical_likelihood', sa.Integer(), nullable=False),
        sa.Column('typical_severity', sa.Integer(), nullable=False),
        sa.Column('mitigation_strategies', sa.JSON(), nullable=True),
        sa.Column('cwe_ids', sa.JSON(), nullable=True),
        sa.Column('capec_ids', sa.JSON(), nullable=True),
        sa.Column('examples', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(), nullable=False, server_default='custom'),
        sa.Column('source_version', sa.String(), nullable=True),
        sa.Column('mitre_technique_id', sa.String(), nullable=True),
        sa.Column('mitre_tactic', sa.String(), nullable=True),
        sa.Column('automotive_relevance', sa.Integer(), nullable=False),
        sa.Column('automotive_context', sa.String(), nullable=True),
        sa.Column('is_user_modified', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_threat_catalog_id', 'threat_catalog', ['id'])
    op.create_index('ix_threat_catalog_mitre_technique_id', 'threat_catalog', ['mitre_technique_id'])

    # ── Tables with FK dependencies (depth 1) ────────────────────────────────
    op.create_table('approval_signoffs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('signer', sa.String(length=100), nullable=False),
        sa.Column('signer_role', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('signed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['workflow_id'], ['approval_workflows.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approval_signoffs_workflow_id', 'approval_signoffs', ['workflow_id'])

    op.create_table('assets',
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('asset_type', sa.String(), nullable=False),
        sa.Column('data_types', sa.JSON(), nullable=True),
        sa.Column('storage_location', sa.String(), nullable=True),
        sa.Column('scope_id', sa.String(), nullable=False),
        sa.Column('scope_version', sa.Integer(), nullable=False),
        sa.Column('confidentiality', sa.String(), nullable=False),
        sa.Column('integrity', sa.String(), nullable=False),
        sa.Column('availability', sa.String(), nullable=False),
        sa.Column('authenticity_required', sa.Boolean(), nullable=False),
        sa.Column('authorization_required', sa.Boolean(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False),
        sa.Column('revision_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['scope_id'], ['product_scopes.scope_id']),
        sa.PrimaryKeyConstraint('asset_id'),
    )
    op.create_index('ix_assets_asset_id', 'assets', ['asset_id'])

    op.create_table('cra_assessments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('classification', sa.String(), nullable=True),
        sa.Column('classification_answers', sa.JSON(), nullable=True, server_default="'{}'"),
        sa.Column('product_type', sa.String(), nullable=True, server_default='current'),
        sa.Column('compliance_path', sa.String(), nullable=True, server_default='direct_patch'),
        sa.Column('compliance_deadline', sa.String(), nullable=True),
        sa.Column('assessment_date', sa.DateTime(), nullable=True),
        sa.Column('assessor_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('overall_compliance_pct', sa.Integer(), nullable=True),
        sa.Column('support_period_years', sa.Integer(), nullable=True),
        sa.Column('support_period_justification', sa.Text(), nullable=True),
        sa.Column('support_period_end', sa.String(), nullable=True),
        sa.Column('eoss_date', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('automotive_exception', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('data_profile', sa.JSON(), nullable=True, server_default="'{}'"),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['product_scopes.scope_id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cra_assessments_id', 'cra_assessments', ['id'])
    op.create_index('ix_cra_assessments_product_id', 'cra_assessments', ['product_id'], unique=True)

    op.create_table('product_scope_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scope_id', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('product_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('safety_level', sa.String(), nullable=False),
        sa.Column('interfaces', sa.JSON(), nullable=True),
        sa.Column('access_points', sa.JSON(), nullable=True),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('trust_zone', sa.String(), nullable=False),
        sa.Column('boundaries', sa.JSON(), nullable=True),
        sa.Column('objectives', sa.JSON(), nullable=True),
        sa.Column('stakeholders', sa.JSON(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False),
        sa.Column('revision_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['scope_id'], ['product_scopes.scope_id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scope_id', 'version', name='unique_product_version'),
    )

    op.create_table('role_permissions',
        sa.Column('role', sa.String(length=12), nullable=False),
        sa.Column('permission_id', sa.String(), nullable=False),
        sa.Column('organization_scope', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.permission_id']),
        sa.PrimaryKeyConstraint('role', 'permission_id'),
    )

    op.create_table('threat_scenarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('threat_scenario_id', sa.String(length=50), nullable=False),
        sa.Column('damage_scenario_id', sa.String(length=50), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('attack_vector', sa.String(length=100), nullable=False),
        sa.Column('scope_id', sa.String(length=50), nullable=False),
        sa.Column('scope_version', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('revision_notes', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='accepted'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['damage_scenario_id'], ['damage_scenarios.scenario_id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_threat_scenarios_id', 'threat_scenarios', ['id'])
    op.create_index('ix_threat_scenarios_threat_scenario_id', 'threat_scenarios', ['threat_scenario_id'], unique=True)
    op.create_index('ix_threat_scenarios_scope_id', 'threat_scenarios', ['scope_id'])
    op.create_index('ix_threat_scenarios_damage_scenario_id', 'threat_scenarios', ['damage_scenario_id'])

    op.create_table('risk_treatments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('risk_treatment_id', sa.String(), nullable=True),
        sa.Column('damage_scenario_id', sa.String(), nullable=False),
        sa.Column('attack_path_id', sa.String(), nullable=True),
        sa.Column('scope_id', sa.String(), nullable=False),
        sa.Column('impact_level', sa.String(), nullable=False),
        sa.Column('feasibility_level', sa.String(), nullable=False),
        sa.Column('risk_level', sa.String(), nullable=False),
        sa.Column('feasibility_score', sa.Float(), nullable=False),
        sa.Column('suggested_treatment', sa.String(), nullable=False),
        sa.Column('selected_treatment', sa.String(), nullable=True),
        sa.Column('treatment_goal', sa.Text(), nullable=True),
        sa.Column('treatment_status', sa.String(), nullable=True, server_default='draft'),
        sa.Column('approved_by', sa.String(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['damage_scenario_id'], ['damage_scenarios.scenario_id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_risk_treatments_id', 'risk_treatments', ['id'])
    op.create_index('ix_risk_treatments_risk_treatment_id', 'risk_treatments', ['risk_treatment_id'], unique=True)

    # ── Tables with FK dependencies (depth 2+) ───────────────────────────────
    op.create_table('asset_connections',
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('connected_to_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id']),
        sa.ForeignKeyConstraint(['connected_to_id'], ['assets.asset_id']),
        sa.PrimaryKeyConstraint('asset_id', 'connected_to_id'),
    )

    op.create_table('asset_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('asset_type', sa.String(), nullable=False),
        sa.Column('data_types', sa.JSON(), nullable=True),
        sa.Column('storage_location', sa.String(), nullable=True),
        sa.Column('scope_id', sa.String(), nullable=False),
        sa.Column('scope_version', sa.Integer(), nullable=False),
        sa.Column('confidentiality', sa.String(), nullable=False),
        sa.Column('integrity', sa.String(), nullable=False),
        sa.Column('availability', sa.String(), nullable=False),
        sa.Column('authenticity_required', sa.Boolean(), nullable=False),
        sa.Column('authorization_required', sa.Boolean(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False),
        sa.Column('revision_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id']),
        sa.ForeignKeyConstraint(['scope_id'], ['product_scopes.scope_id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_id', 'version', name='unique_asset_version'),
    )

    op.create_table('cra_compensating_controls',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('assessment_id', sa.String(), nullable=False),
        sa.Column('control_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('implementation_status', sa.String(), nullable=False, server_default='planned'),
        sa.Column('supplier_actions', sa.Text(), nullable=True),
        sa.Column('oem_actions', sa.Text(), nullable=True),
        sa.Column('residual_risk', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['cra_assessments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cra_compensating_controls_id', 'cra_compensating_controls', ['id'])
    op.create_index('ix_cra_compensating_controls_assessment_id', 'cra_compensating_controls', ['assessment_id'])

    op.create_table('cra_inventory_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('assessment_id', sa.String(), nullable=False),
        sa.Column('sku', sa.String(), nullable=False),
        sa.Column('firmware_version', sa.String(), nullable=True),
        sa.Column('units_in_stock', sa.Integer(), nullable=True),
        sa.Column('units_in_field', sa.Integer(), nullable=True),
        sa.Column('oem_customer', sa.String(), nullable=True),
        sa.Column('target_market', sa.String(), nullable=True, server_default='eu'),
        sa.Column('last_production_date', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['cra_assessments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cra_inventory_items_id', 'cra_inventory_items', ['id'])
    op.create_index('ix_cra_inventory_items_assessment_id', 'cra_inventory_items', ['assessment_id'])

    op.create_table('cra_requirement_statuses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('assessment_id', sa.String(), nullable=False),
        sa.Column('requirement_id', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='not_started'),
        sa.Column('auto_mapped', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('mapped_artifact_type', sa.String(), nullable=True),
        sa.Column('mapped_artifact_count', sa.Integer(), nullable=True),
        sa.Column('owner', sa.String(), nullable=True),
        sa.Column('target_date', sa.String(), nullable=True),
        sa.Column('evidence_notes', sa.Text(), nullable=True),
        sa.Column('evidence_links', sa.JSON(), nullable=True, server_default="'[]'"),
        sa.Column('gap_description', sa.Text(), nullable=True),
        sa.Column('remediation_plan', sa.Text(), nullable=True),
        sa.Column('gap_severity', sa.String(), nullable=True),
        sa.Column('residual_risk_level', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['cra_assessments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cra_requirement_statuses_id', 'cra_requirement_statuses', ['id'])
    op.create_index('ix_cra_requirement_statuses_assessment_id', 'cra_requirement_statuses', ['assessment_id'])

    op.create_table('threat_analysis_results',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('analysis_id', sa.String(), nullable=True),
        sa.Column('component_id', sa.String(), nullable=True),
        sa.Column('threat_id', sa.String(), nullable=True),
        sa.Column('match_confidence', sa.Integer(), nullable=False),
        sa.Column('calculated_likelihood', sa.Integer(), nullable=False),
        sa.Column('calculated_severity', sa.Integer(), nullable=False),
        sa.Column('calculated_risk_score', sa.Integer(), nullable=False),
        sa.Column('applicable_mitigations', sa.JSON(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id']),
        sa.ForeignKeyConstraint(['component_id'], ['components.component_id']),
        sa.ForeignKeyConstraint(['threat_id'], ['threat_catalog.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_threat_analysis_results_id', 'threat_analysis_results', ['id'])
    op.create_index('ix_threat_analysis_results_analysis_id', 'threat_analysis_results', ['analysis_id'])
    op.create_index('ix_threat_analysis_results_component_id', 'threat_analysis_results', ['component_id'])
    op.create_index('ix_threat_analysis_results_threat_id', 'threat_analysis_results', ['threat_id'])

    op.create_table('asset_damage_scenario',
        sa.Column('asset_id', sa.String(), nullable=True),
        sa.Column('scenario_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id']),
        sa.ForeignKeyConstraint(['scenario_id'], ['damage_scenarios.scenario_id']),
    )

    op.create_table('cra_control_requirement_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('control_id', sa.String(), nullable=False),
        sa.Column('requirement_status_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['control_id'], ['cra_compensating_controls.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requirement_status_id'], ['cra_requirement_statuses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('cra_control_requirement_links')
    op.drop_table('asset_damage_scenario')
    op.drop_table('threat_analysis_results')
    op.drop_table('cra_requirement_statuses')
    op.drop_table('cra_inventory_items')
    op.drop_table('cra_compensating_controls')
    op.drop_table('asset_history')
    op.drop_table('asset_connections')
    op.drop_table('risk_treatments')
    op.drop_table('threat_scenarios')
    op.drop_table('role_permissions')
    op.drop_table('product_scope_history')
    op.drop_table('cra_assessments')
    op.drop_table('assets')
    op.drop_table('approval_signoffs')
    op.drop_table('threat_catalog')
    op.drop_table('tara_snapshots')
    op.drop_table('product_scopes')
    op.drop_table('permissions')
    op.drop_table('evidence_attachments')
    op.drop_table('audit_logs')
    op.drop_table('approval_workflows')
