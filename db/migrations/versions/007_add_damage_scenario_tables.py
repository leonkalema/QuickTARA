"""
Add damage scenario tables

Revision ID: 007_add_damage_scenario_tables
Revises: 006_add_security_properties_to_components
Create Date: 2025-05-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '007_add_damage_scenario_tables'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Create damage_scenarios table
    op.create_table(
        'damage_scenarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scenario_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('damage_category', sa.String(), nullable=False),
        sa.Column('impact_type', sa.String(), nullable=False),
        sa.Column('confidentiality_impact', sa.Boolean(), default=False),
        sa.Column('integrity_impact', sa.Boolean(), default=False),
        sa.Column('availability_impact', sa.Boolean(), default=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('impact_details', sa.JSON(), nullable=True),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('revision_notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('scope_id', sa.String(), nullable=False),
        sa.Column('primary_component_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scenario_id'),
        sa.ForeignKeyConstraint(['scope_id'], ['system_scopes.scope_id'], ),
        sa.ForeignKeyConstraint(['primary_component_id'], ['components.component_id'], ),
        sa.Index('ix_damage_scenarios_scenario_id', 'scenario_id', unique=True)
    )
    
    # Create component_damage_scenario association table
    op.create_table(
        'component_damage_scenario',
        sa.Column('component_id', sa.String(), nullable=False),
        sa.Column('scenario_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['component_id'], ['components.component_id'], ),
        sa.ForeignKeyConstraint(['scenario_id'], ['damage_scenarios.scenario_id'], ),
        sa.UniqueConstraint('component_id', 'scenario_id', name='uq_component_damage_scenario')
    )
    
    # Update the SystemScope model to add relationship with damage scenarios
    # This doesn't require schema changes, just ORM relationship updates
    
    # Update the Component model to add relationship with damage scenarios
    # This doesn't require schema changes, just ORM relationship updates


def downgrade():
    # Drop the association table first (due to foreign key constraints)
    op.drop_table('component_damage_scenario')
    
    # Drop the damage_scenarios table
    op.drop_table('damage_scenarios')
