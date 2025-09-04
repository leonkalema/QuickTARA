"""Update SFOP impact columns to store severity levels

Revision ID: 009_update_sfop_columns
Revises: 008_make_primary_component_id_nullable
Create Date: 2025-09-04 12:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009_update_sfop_columns'
down_revision = '008_add_sfop_impact_rating_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Update SFOP impact columns from Boolean to String to store severity levels"""
    
    # For SQLite, we need to recreate the table since ALTER COLUMN is not supported
    # First, create a temporary table with the new schema
    op.execute("""
        CREATE TABLE damage_scenarios_temp (
            scenario_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            damage_category TEXT NOT NULL,
            impact_type TEXT NOT NULL DEFAULT 'Direct',
            severity TEXT NOT NULL DEFAULT 'Medium',
            confidentiality_impact BOOLEAN DEFAULT 0,
            integrity_impact BOOLEAN DEFAULT 0,
            availability_impact BOOLEAN DEFAULT 0,
            primary_component_id TEXT,
            safety_impact TEXT DEFAULT 'negligible',
            financial_impact TEXT DEFAULT 'negligible',
            operational_impact TEXT DEFAULT 'negligible',
            privacy_impact TEXT DEFAULT 'negligible',
            version INTEGER DEFAULT 1 NOT NULL,
            is_current BOOLEAN DEFAULT 1 NOT NULL,
            revision_notes TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            violated_properties TEXT,
            scope_id TEXT NOT NULL,
            FOREIGN KEY(scope_id) REFERENCES product_scopes (scope_id)
        )
    """)
    
    # Copy data from old table to new table, converting boolean SFOP values to strings
    op.execute("""
        INSERT INTO damage_scenarios_temp (
            scenario_id, name, description, category, damage_category, impact_type, severity,
            confidentiality_impact, integrity_impact, availability_impact, primary_component_id,
            safety_impact, financial_impact, operational_impact, privacy_impact,
            version, is_current, revision_notes, created_at, updated_at, violated_properties, scope_id
        )
        SELECT 
            scenario_id, name, description, category, damage_category, impact_type, severity,
            confidentiality_impact, integrity_impact, availability_impact, primary_component_id,
            CASE WHEN safety_impact = 1 THEN 'major' ELSE 'negligible' END,
            CASE WHEN financial_impact = 1 THEN 'major' ELSE 'negligible' END,
            CASE WHEN operational_impact = 1 THEN 'major' ELSE 'negligible' END,
            CASE WHEN privacy_impact = 1 THEN 'major' ELSE 'negligible' END,
            version, is_current, revision_notes, created_at, updated_at, violated_properties, scope_id
        FROM damage_scenarios
    """)
    
    # Drop the old table
    op.drop_table('damage_scenarios')
    
    # Rename the temporary table to the original name
    op.execute("ALTER TABLE damage_scenarios_temp RENAME TO damage_scenarios")


def downgrade():
    """Revert SFOP impact columns back to Boolean"""
    
    # Create temporary table with boolean SFOP columns
    op.execute("""
        CREATE TABLE damage_scenarios_temp (
            scenario_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            damage_category TEXT NOT NULL,
            impact_type TEXT NOT NULL DEFAULT 'Direct',
            severity TEXT NOT NULL DEFAULT 'Medium',
            confidentiality_impact BOOLEAN DEFAULT 0,
            integrity_impact BOOLEAN DEFAULT 0,
            availability_impact BOOLEAN DEFAULT 0,
            primary_component_id TEXT,
            safety_impact BOOLEAN DEFAULT 0,
            financial_impact BOOLEAN DEFAULT 0,
            operational_impact BOOLEAN DEFAULT 0,
            privacy_impact BOOLEAN DEFAULT 0,
            version INTEGER DEFAULT 1 NOT NULL,
            is_current BOOLEAN DEFAULT 1 NOT NULL,
            revision_notes TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            violated_properties TEXT,
            scope_id TEXT NOT NULL,
            FOREIGN KEY(scope_id) REFERENCES product_scopes (scope_id)
        )
    """)
    
    # Copy data back, converting string SFOP values to booleans
    op.execute("""
        INSERT INTO damage_scenarios_temp (
            scenario_id, name, description, category, damage_category, impact_type, severity,
            confidentiality_impact, integrity_impact, availability_impact, primary_component_id,
            safety_impact, financial_impact, operational_impact, privacy_impact,
            version, is_current, revision_notes, created_at, updated_at, violated_properties, scope_id
        )
        SELECT 
            scenario_id, name, description, category, damage_category, impact_type, severity,
            confidentiality_impact, integrity_impact, availability_impact, primary_component_id,
            CASE WHEN safety_impact != 'negligible' THEN 1 ELSE 0 END,
            CASE WHEN financial_impact != 'negligible' THEN 1 ELSE 0 END,
            CASE WHEN operational_impact != 'negligible' THEN 1 ELSE 0 END,
            CASE WHEN privacy_impact != 'negligible' THEN 1 ELSE 0 END,
            version, is_current, revision_notes, created_at, updated_at, violated_properties, scope_id
        FROM damage_scenarios
    """)
    
    # Drop the old table and rename temp table
    op.drop_table('damage_scenarios')
    op.execute("ALTER TABLE damage_scenarios_temp RENAME TO damage_scenarios")
