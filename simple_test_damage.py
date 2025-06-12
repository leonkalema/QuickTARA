#!/usr/bin/env python
"""
Minimalist test script for damage scenario creation
Using direct SQLite operations to bypass SQLAlchemy complexities
"""
import os
import sqlite3
import json
import uuid
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.getcwd(), "quicktara.db")

def create_damage_scenario():
    """Create a damage scenario using direct SQL"""
    try:
        print(f"Connecting to database: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Step 1: Generate a unique ID
        scenario_id = f"DS-{uuid.uuid4().hex[:8].upper()}"
        print(f"Generated scenario ID: {scenario_id}")
        
        # Step 2: Find a valid product scope
        cursor.execute("SELECT scope_id FROM product_scopes LIMIT 1")
        scope_id = cursor.fetchone()[0]
        print(f"Found scope_id: {scope_id}")
        
        # Step 3: Find valid assets
        cursor.execute("SELECT asset_id FROM assets LIMIT 2")
        assets = [row[0] for row in cursor.fetchall()]
        print(f"Found assets: {assets}")
        
        # Step 4: Create violated_properties as JSON
        violated_properties = json.dumps({
            "confidentiality": True,
            "integrity": True,
            "availability": False,
            "severity": "Medium"
        })
        
        # Step 5: Check for column names in the table
        print("Checking table structure...")
        cursor.execute("PRAGMA table_info(damage_scenarios)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        print(f"Available columns: {column_names}")
        
        # Step 6: Insert damage scenario
        print("Inserting damage scenario...")
        now = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO damage_scenarios (
                scenario_id, name, description, scope_id, 
                violated_properties, damage_category, safety_impact, 
                financial_impact, operational_impact, privacy_impact,
                version, is_current, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scenario_id, "Direct SQL Test", "Testing damage scenario creation", scope_id,
                violated_properties, "Operational", 0,
                0, 1, 0,
                1, 1, now, now
            )
        )
        print("✓ Damage scenario inserted successfully")
        
        # Step 6: Create asset-damage scenario relationships
        print("Creating asset relationships...")
        for asset_id in assets:
            try:
                cursor.execute(
                    "INSERT INTO asset_damage_scenario (asset_id, scenario_id) VALUES (?, ?)",
                    (asset_id, scenario_id)
                )
                print(f"✓ Added relationship for asset {asset_id}")
            except Exception as e:
                print(f"❌ Error creating relationship for asset {asset_id}: {str(e)}")
        
        # Step 7: Commit the transaction
        conn.commit()
        print("✓ Transaction committed successfully")
        
        # Step 8: Verify data was inserted
        cursor.execute("SELECT * FROM damage_scenarios WHERE scenario_id = ?", (scenario_id,))
        result = cursor.fetchone()
        if result:
            print(f"✓ Verified damage scenario exists: {scenario_id}")
            
            # Check relationships
            cursor.execute(
                "SELECT COUNT(*) FROM asset_damage_scenario WHERE scenario_id = ?", 
                (scenario_id,)
            )
            count = cursor.fetchone()[0]
            print(f"✓ Verified {count} asset relationships")
            
            print("✅ TEST PASSED - Direct SQL approach works!")
            return scenario_id
        else:
            print("❌ Could not verify damage scenario was inserted")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_damage_scenario()
