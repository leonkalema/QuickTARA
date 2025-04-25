#!/usr/bin/env python3
"""
Add scope_id column to components table in QuickTARA database.
This is a direct SQLite approach to apply the migration without needing Alembic.
"""
import sqlite3
import os
import sys
from pathlib import Path

# Database path - default SQLite database location
DB_PATH = Path('./quicktara.db').absolute()

def migrate_database():
    """Add scope_id column to components table"""
    if not DB_PATH.exists():
        print(f"Error: Database file not found at {DB_PATH}")
        print("Please run this script from the project root directory or specify the correct path.")
        sys.exit(1)
    
    print(f"Found database at: {DB_PATH}")
    
    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if scope_id column already exists
        cursor.execute("PRAGMA table_info(components)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'scope_id' in columns:
            print("Column 'scope_id' already exists in 'components' table. No changes needed.")
            return
        
        print("Adding 'scope_id' column to 'components' table...")
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Add scope_id column to components table
        cursor.execute("ALTER TABLE components ADD COLUMN scope_id TEXT")
        
        # SQLite doesn't support adding foreign key constraints to existing tables directly
        # So we need to create a new table with the constraint and copy the data
        
        # Create temporary table with the new schema
        cursor.execute("""
        CREATE TABLE components_new (
            component_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            safety_level TEXT NOT NULL,
            interfaces TEXT,
            access_points TEXT,
            data_types TEXT,
            location TEXT NOT NULL,
            trust_zone TEXT NOT NULL,
            scope_id TEXT,
            FOREIGN KEY (scope_id) REFERENCES system_scopes(scope_id)
        )
        """)
        
        # Copy data from old table to new table
        cursor.execute("""
        INSERT INTO components_new (
            component_id, name, type, safety_level, interfaces, 
            access_points, data_types, location, trust_zone, scope_id
        )
        SELECT 
            component_id, name, type, safety_level, interfaces, 
            access_points, data_types, location, trust_zone, scope_id
        FROM components
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE components")
        
        # Rename new table to original name
        cursor.execute("ALTER TABLE components_new RENAME TO components")
        
        # Re-create the many-to-many relationship for connected components
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS component_connections (
            component_id TEXT NOT NULL, 
            connected_to_id TEXT NOT NULL,
            PRIMARY KEY (component_id, connected_to_id),
            FOREIGN KEY (component_id) REFERENCES components (component_id) ON DELETE CASCADE,
            FOREIGN KEY (connected_to_id) REFERENCES components (component_id) ON DELETE CASCADE
        )
        """)
        
        # Commit transaction
        conn.commit()
        print("Migration successful! 'scope_id' column added to 'components' table.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
