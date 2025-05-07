#!/usr/bin/env python3
"""
Add risk_frameworks table to QuickTARA database.
This is a direct SQLite approach to apply the migration without needing Alembic.
"""
import sqlite3
import os
import sys
from pathlib import Path
import json

# Database path - default SQLite database location
DB_PATH = Path('./quicktara.db').absolute()

def migrate_database():
    """Add risk_frameworks table to the database"""
    if not DB_PATH.exists():
        print(f"Error: Database file not found at {DB_PATH}")
        print("Please run this script from the project root directory or specify the correct path.")
        sys.exit(1)
    
    print(f"Found database at: {DB_PATH}")
    
    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Check if risk_frameworks table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='risk_frameworks'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("Table 'risk_frameworks' already exists in the database. No changes needed.")
            return
        
        print("Adding 'risk_frameworks' table to the database...")
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # Create risk_frameworks table
        cursor.execute("""
        CREATE TABLE risk_frameworks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            framework_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            version TEXT NOT NULL,
            impact_definitions JSON NOT NULL,
            likelihood_definitions JSON NOT NULL,
            risk_matrix JSON NOT NULL,
            risk_thresholds JSON NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1
        )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX ix_risk_frameworks_id ON risk_frameworks (id)")
        cursor.execute("CREATE UNIQUE INDEX ix_risk_frameworks_framework_id ON risk_frameworks (framework_id)")
        
        # Commit transaction
        conn.commit()
        print("Migration successful! 'risk_frameworks' table added to the database.")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
