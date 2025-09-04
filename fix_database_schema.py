#!/usr/bin/env python3
"""
Quick fix for database schema - make primary_component_id nullable
"""
import sqlite3
import os

def fix_database_schema():
    """Fix the database schema to allow NULL primary_component_id"""
    db_path = "quicktara.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Fixing damage_scenarios table schema...")
        
        # Create a new table with the correct schema
        cursor.execute("""
        CREATE TABLE damage_scenarios_new (
            scenario_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            scope_id TEXT NOT NULL,
            violated_properties TEXT NOT NULL,
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
            updated_at DATETIME
        )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
        INSERT INTO damage_scenarios_new 
        SELECT * FROM damage_scenarios
        """)
        
        # Drop old table and rename new table
        cursor.execute("DROP TABLE damage_scenarios")
        cursor.execute("ALTER TABLE damage_scenarios_new RENAME TO damage_scenarios")
        
        conn.commit()
        print("✅ Database schema fixed successfully!")
        print("✅ primary_component_id is now nullable")
        
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_schema()
