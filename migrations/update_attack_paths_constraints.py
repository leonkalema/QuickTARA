#!/usr/bin/env python3
"""
Update attack_paths table constraints to match new feasibility rating ranges
"""
import sqlite3
import sys
import os

# Add the parent directory to the path so we can import from api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_attack_paths_constraints():
    """Update the attack_paths table constraints for new scoring ranges"""
    
    # Connect to the database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'quicktara.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First, create a new table with the correct constraints
        cursor.execute("""
            CREATE TABLE attack_paths_new (
                attack_path_id TEXT PRIMARY KEY,
                threat_scenario_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                attack_steps TEXT NOT NULL,
                elapsed_time INTEGER NOT NULL CHECK (elapsed_time >= 0 AND elapsed_time <= 19),
                specialist_expertise INTEGER NOT NULL CHECK (specialist_expertise >= 0 AND specialist_expertise <= 8),
                knowledge_of_target INTEGER NOT NULL CHECK (knowledge_of_target >= 0 AND knowledge_of_target <= 11),
                window_of_opportunity INTEGER NOT NULL CHECK (window_of_opportunity >= 0 AND window_of_opportunity <= 10),
                equipment INTEGER NOT NULL CHECK (equipment >= 0 AND equipment <= 9),
                overall_rating REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Copy existing data to the new table
        cursor.execute("""
            INSERT INTO attack_paths_new 
            SELECT * FROM attack_paths
        """)
        
        # Drop the old table
        cursor.execute("DROP TABLE attack_paths")
        
        # Rename the new table
        cursor.execute("ALTER TABLE attack_paths_new RENAME TO attack_paths")
        
        # Recreate the index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attack_paths_threat_scenario 
            ON attack_paths (threat_scenario_id)
        """)
        
        # Recreate the trigger
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_attack_paths_updated_at
            AFTER UPDATE ON attack_paths
            FOR EACH ROW
            BEGIN
                UPDATE attack_paths SET updated_at = CURRENT_TIMESTAMP WHERE attack_path_id = NEW.attack_path_id;
            END
        """)
        
        conn.commit()
        print("✅ Successfully updated attack_paths table constraints")
        
        # Verify the table structure
        cursor.execute("PRAGMA table_info(attack_paths)")
        columns = cursor.fetchall()
        print("✅ Updated table structure:")
        for col in columns:
            print(f"   {col[1]} {col[2]}")
            
    except Exception as e:
        print(f"❌ Error updating attack_paths table: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("Updating attack_paths table constraints...")
    success = update_attack_paths_constraints()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)
