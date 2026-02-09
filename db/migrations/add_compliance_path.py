"""
Migration: Add compliance_path field to cra_assessments table

This adds the compliance_path field to track whether a product follows:
- direct_patch: Traditional SW updates via workshop/service channels
- compensating_control: Security updates via network-layer mitigations per Art. 5(3)
- hybrid: Combination of both paths
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
        cursor.execute("PRAGMA table_info(cra_assessments)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'compliance_path' not in columns:
            cursor.execute("""
                ALTER TABLE cra_assessments
                ADD COLUMN compliance_path TEXT DEFAULT 'direct_patch'
            """)
            print("Added compliance_path column to cra_assessments")
        else:
            print("compliance_path column already exists")
        
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
