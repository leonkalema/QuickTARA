"""
Migration: Add cra_inventory_items table for SKU/inventory tracking

This adds inventory tracking for CRA assessments to support:
- SKUs to liquidate (non-EU markets)
- SKUs requiring mitigation stack (EU-bound)
- Field population estimates per OEM
"""
import sqlite3
import os


def run_migration():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'quicktara.db')
    db_path = os.path.abspath(db_path)
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='cra_inventory_items'
        """)
        if cursor.fetchone():
            print("cra_inventory_items table already exists")
            return True
        
        cursor.execute("""
            CREATE TABLE cra_inventory_items (
                id TEXT PRIMARY KEY,
                assessment_id TEXT NOT NULL REFERENCES cra_assessments(id) ON DELETE CASCADE,
                sku TEXT NOT NULL,
                firmware_version TEXT,
                units_in_stock INTEGER DEFAULT 0,
                units_in_field INTEGER DEFAULT 0,
                oem_customer TEXT,
                target_market TEXT DEFAULT 'eu',
                last_production_date TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX idx_cra_inventory_assessment 
            ON cra_inventory_items(assessment_id)
        """)
        
        print("Created cra_inventory_items table")
        conn.commit()
        print("Migration completed successfully")
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
