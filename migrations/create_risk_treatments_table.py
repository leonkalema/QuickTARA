#!/usr/bin/env python3
"""
Create risk_treatments table migration
"""
import sqlite3
import sys
from pathlib import Path

def create_risk_treatments_table():
    """Create the risk_treatments table"""
    
    # Get the database path
    db_path = Path(__file__).parent.parent / "quicktara.db"
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create risk_treatments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                risk_treatment_id TEXT UNIQUE NOT NULL,
                damage_scenario_id TEXT NOT NULL,
                attack_path_id TEXT NOT NULL,
                scope_id TEXT NOT NULL,
                impact_level TEXT NOT NULL,
                feasibility_level TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                feasibility_score REAL NOT NULL,
                suggested_treatment TEXT NOT NULL,
                selected_treatment TEXT,
                treatment_goal TEXT,
                treatment_status TEXT DEFAULT 'draft',
                approved_by TEXT,
                approved_at DATETIME,
                approval_notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                updated_by TEXT,
                FOREIGN KEY (damage_scenario_id) REFERENCES damage_scenarios (scenario_id),
                FOREIGN KEY (attack_path_id) REFERENCES attack_paths (attack_path_id),
                FOREIGN KEY (scope_id) REFERENCES system_scopes (scope_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_treatments_damage_scenario ON risk_treatments (damage_scenario_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_treatments_attack_path ON risk_treatments (attack_path_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_treatments_scope ON risk_treatments (scope_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_treatments_status ON risk_treatments (treatment_status)")
        
        # Create trigger for updated_at
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_risk_treatments_updated_at
            AFTER UPDATE ON risk_treatments
            FOR EACH ROW
            BEGIN
                UPDATE risk_treatments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
        """)
        
        conn.commit()
        print("✅ Successfully created risk_treatments table")
        
    except sqlite3.Error as e:
        print(f"❌ Error creating risk_treatments table: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_risk_treatments_table()
