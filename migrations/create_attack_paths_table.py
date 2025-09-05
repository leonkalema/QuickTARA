#!/usr/bin/env python3
"""
Create attack_paths table for risk assessment
"""
import sqlite3
import sys
import os

# Add the parent directory to the path so we can import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_attack_paths_table():
    """Create the attack_paths table"""
    
    # Connect to the database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'quicktara.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create attack_paths table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attack_paths (
                attack_path_id TEXT PRIMARY KEY,
                threat_scenario_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                attack_steps TEXT NOT NULL,
                elapsed_time INTEGER NOT NULL CHECK (elapsed_time >= 1 AND elapsed_time <= 4),
                specialist_expertise INTEGER NOT NULL CHECK (specialist_expertise >= 1 AND specialist_expertise <= 4),
                knowledge_of_target INTEGER NOT NULL CHECK (knowledge_of_target >= 1 AND knowledge_of_target <= 4),
                window_of_opportunity INTEGER NOT NULL CHECK (window_of_opportunity >= 1 AND window_of_opportunity <= 4),
                equipment INTEGER NOT NULL CHECK (equipment >= 1 AND equipment <= 4),
                overall_rating REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on threat_scenario_id for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attack_paths_threat_scenario 
            ON attack_paths (threat_scenario_id)
        """)
        
        # Create trigger to update updated_at timestamp
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_attack_paths_updated_at
            AFTER UPDATE ON attack_paths
            FOR EACH ROW
            BEGIN
                UPDATE attack_paths SET updated_at = CURRENT_TIMESTAMP WHERE attack_path_id = NEW.attack_path_id;
            END
        """)
        
        conn.commit()
        print("✅ Successfully created attack_paths table")
        
        # Verify the table was created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attack_paths'")
        if cursor.fetchone():
            print("✅ Table verification successful")
        else:
            print("❌ Table verification failed")
            
    except Exception as e:
        print(f"❌ Error creating attack_paths table: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("Creating attack_paths table...")
    success = create_attack_paths_table()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)
