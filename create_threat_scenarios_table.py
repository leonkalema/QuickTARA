#!/usr/bin/env python3
"""
Create threat_scenarios table with correct schema
"""
import sqlite3
from datetime import datetime

def create_threat_scenarios_table():
    conn = sqlite3.connect('quicktara.db')
    cursor = conn.cursor()
    
    # Create threat_scenarios table with correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threat_scenarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            threat_scenario_id VARCHAR(50) UNIQUE NOT NULL,
            damage_scenario_id VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            attack_vector VARCHAR(100) NOT NULL,
            scope_id VARCHAR(50) NOT NULL,
            scope_version INTEGER NOT NULL,
            version INTEGER DEFAULT 1 NOT NULL,
            revision_notes TEXT,
            is_deleted BOOLEAN DEFAULT 0 NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_threat_scenarios_threat_scenario_id ON threat_scenarios (threat_scenario_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_threat_scenarios_damage_scenario_id ON threat_scenarios (damage_scenario_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_threat_scenarios_scope_id ON threat_scenarios (scope_id)')
    
    conn.commit()
    conn.close()
    print("✅ threat_scenarios table created successfully")

if __name__ == "__main__":
    create_threat_scenarios_table()
