"""add product damage scenario columns

Revision ID: add_product_damage_scenario_columns
Revises: 008_add_sfop_impact_rating_fields
Create Date: 2025-06-12

This migration adds the necessary columns to support the product-centric damage scenario model.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = 'add_product_damage_scenario_columns'
down_revision = '008_add_sfop_impact_rating_fields'  # Adjust this based on your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Add the new violated_properties column as JSON type
    op.add_column('damage_scenarios', sa.Column('violated_properties', sa.JSON, nullable=True))
    
    # Add the category column
    op.add_column('damage_scenarios', sa.Column('category', sa.String, nullable=True))
    
    # Convert existing CIA impacts to violated_properties JSON
    conn = op.get_bind()
    damage_scenarios = table(
        'damage_scenarios',
        column('scenario_id', sa.String),
        column('confidentiality_impact', sa.String),
        column('integrity_impact', sa.String),
        column('availability_impact', sa.String),
        column('violated_properties', sa.JSON)
    )
    
    # Get all damage scenarios
    results = conn.execute(sa.select(
        damage_scenarios.c.scenario_id,
        damage_scenarios.c.confidentiality_impact, 
        damage_scenarios.c.integrity_impact,
        damage_scenarios.c.availability_impact
    )).fetchall()
    
    # Update each scenario with the violated_properties JSON
    for scenario_id, confidentiality, integrity, availability in results:
        if scenario_id:
            # Create violated_properties JSON
            violated_props = {
                "confidentiality": confidentiality if confidentiality else "LOW",
                "integrity": integrity if integrity else "LOW",
                "availability": availability if availability else "LOW",
                "severity": "LOW"  # Default to LOW as we don't have severity in old schema
            }
            
            # Update the row
            conn.execute(
                damage_scenarios.update().
                where(damage_scenarios.c.scenario_id == scenario_id).
                values(violated_properties=violated_props, category="Logical")  # Default category
            )
    
    # Create the asset_damage_scenario table for many-to-many relationship
    op.create_table(
        'asset_damage_scenario',
        sa.Column('asset_id', sa.String(), nullable=False),
        sa.Column('scenario_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id'], ),
        sa.ForeignKeyConstraint(['scenario_id'], ['damage_scenarios.scenario_id'], ),
        sa.PrimaryKeyConstraint('asset_id', 'scenario_id')
    )
    
    # Add is_current column if it doesn't exist
    try:
        op.add_column('damage_scenarios', sa.Column('is_current', sa.Boolean, nullable=False, server_default='1'))
    except Exception:
        # Column might already exist in some versions
        pass


def downgrade():
    # Drop the new columns
    op.drop_column('damage_scenarios', 'violated_properties')
    op.drop_column('damage_scenarios', 'category')
    
    # Drop the join table
    op.drop_table('asset_damage_scenario')
    
    # Don't remove is_current as it might be used by other tables
