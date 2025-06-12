#!/usr/bin/env python
"""
Database Update Script: Add Product Damage Scenario Columns

This script directly adds the necessary columns to the damage_scenarios table
to support the product-centric damage scenario model.

It avoids using Alembic to work around migration chain issues.
"""
import os
import sys
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, text, Column, String, JSON, Boolean, ForeignKey, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('db_update')

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Database connection
DB_PATH = os.environ.get('QUICKTARA_DB', 'sqlite:///quicktara.db')

def get_engine():
    """Get database engine"""
    return create_engine(DB_PATH)

def get_session():
    """Create a database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def add_columns():
    """Add the required columns to the damage_scenarios table"""
    logger.info("Adding columns to damage_scenarios table...")
    engine = get_engine()
    conn = engine.connect()
    
    try:
        # Check if columns already exist
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        if 'damage_scenarios' not in metadata.tables:
            logger.error("damage_scenarios table doesn't exist")
            return
            
        existing_columns = [c.name for c in metadata.tables['damage_scenarios'].columns]
        
        # Add violated_properties column
        if 'violated_properties' not in existing_columns:
            logger.info("Adding violated_properties column...")
            conn.execute(text("ALTER TABLE damage_scenarios ADD COLUMN violated_properties JSON"))
            logger.info("violated_properties column added successfully.")
        
        # Add category column
        if 'category' not in existing_columns:
            logger.info("Adding category column...")
            conn.execute(text("ALTER TABLE damage_scenarios ADD COLUMN category STRING"))
            logger.info("category column added successfully.")
        
        # Add is_current column if it doesn't exist
        if 'is_current' not in existing_columns:
            logger.info("Adding is_current column...")
            conn.execute(text("ALTER TABLE damage_scenarios ADD COLUMN is_current BOOLEAN NOT NULL DEFAULT 1"))
            logger.info("is_current column added successfully.")
            
        # Create asset_damage_scenario table if it doesn't exist
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        if 'asset_damage_scenario' not in metadata.tables:
            logger.info("Creating asset_damage_scenario table...")
            
            # Create the table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS asset_damage_scenario (
                asset_id VARCHAR NOT NULL,
                scenario_id VARCHAR NOT NULL,
                PRIMARY KEY (asset_id, scenario_id),
                FOREIGN KEY (asset_id) REFERENCES assets (asset_id),
                FOREIGN KEY (scenario_id) REFERENCES damage_scenarios (scenario_id)
            )
            """
            conn.execute(text(create_table_sql))
            logger.info("asset_damage_scenario table created successfully.")
            
        # Migrate existing CIA impact data to violated_properties JSON
        migrate_cia_data(conn)
        
        logger.info("All columns added successfully.")
    except Exception as e:
        logger.error(f"Error adding columns: {str(e)}")
        raise
    finally:
        conn.close()

def migrate_cia_data(conn):
    """Migrate existing CIA impact data to violated_properties JSON"""
    logger.info("Migrating CIA impact data to violated_properties...")
    
    try:
        # Get all damage scenarios
        result = conn.execute(text(
            "SELECT scenario_id, confidentiality_impact, integrity_impact, availability_impact "
            "FROM damage_scenarios"
        ))
        
        # Update each scenario
        for row in result:
            scenario_id = row[0]
            confidentiality = row[1] or "LOW"
            integrity = row[2] or "LOW"
            availability = row[3] or "LOW"
            
            # Create violated_properties JSON
            violated_props = {
                "confidentiality": confidentiality,
                "integrity": integrity, 
                "availability": availability,
                "severity": "LOW"  # Default severity
            }
            
            # Update the record
            conn.execute(
                text("UPDATE damage_scenarios SET violated_properties = :props, category = :category WHERE scenario_id = :id"),
                {"props": json.dumps(violated_props), "category": "Logical", "id": scenario_id}
            )
            
        logger.info("CIA impact data migration completed.")
    except Exception as e:
        logger.error(f"Error migrating CIA data: {str(e)}")
        raise

def main():
    """Main function"""
    logger.info("Starting database update...")
    
    try:
        add_columns()
        logger.info("Database update completed successfully.")
    except Exception as e:
        logger.error(f"Database update failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
