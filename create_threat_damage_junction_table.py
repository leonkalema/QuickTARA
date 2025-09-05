#!/usr/bin/env python3
"""
Create junction table for many-to-many threat scenario to damage scenario relationships
"""
import sqlite3

def create_junction_table():
    conn = sqlite3.connect('quicktara.db')
    cursor = conn.cursor()
    
    # Create junction table for threat-damage relationships
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threat_damage_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            threat_scenario_id VARCHAR(50) NOT NULL,
            damage_scenario_id VARCHAR(50) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (threat_scenario_id) REFERENCES threat_scenarios (threat_scenario_id),
            FOREIGN KEY (damage_scenario_id) REFERENCES damage_scenarios (scenario_id),
            UNIQUE(threat_scenario_id, damage_scenario_id)
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_threat_damage_threat_id ON threat_damage_links (threat_scenario_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS ix_threat_damage_damage_id ON threat_damage_links (damage_scenario_id)')
    
    # Migrate existing single relationships to junction table
    cursor.execute('''
        INSERT OR IGNORE INTO threat_damage_links (threat_scenario_id, damage_scenario_id)
        SELECT threat_scenario_id, damage_scenario_id 
        FROM threat_scenarios 
        WHERE damage_scenario_id IS NOT NULL AND damage_scenario_id != ''
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Junction table created and existing relationships migrated")

if __name__ == "__main__":
    create_junction_table()
