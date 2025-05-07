"""
Script to add security properties columns to components table
"""
import sqlite3
import os

# Get the database path from environment or use default
DB_PATH = os.environ.get('DATABASE_URL', 'quicktara.db')
DB_PATH = DB_PATH.replace('sqlite:///', '')

def apply_migration():
    """Apply the security properties migration directly"""
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(components)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add columns if they don't exist
        if 'confidentiality' not in columns:
            print("Adding confidentiality column")
            cursor.execute("ALTER TABLE components ADD COLUMN confidentiality TEXT")
            cursor.execute("UPDATE components SET confidentiality = 'MEDIUM'")
        
        if 'integrity' not in columns:
            print("Adding integrity column")
            cursor.execute("ALTER TABLE components ADD COLUMN integrity TEXT")
            cursor.execute("UPDATE components SET integrity = 'MEDIUM'")
            
        if 'availability' not in columns:
            print("Adding availability column")
            cursor.execute("ALTER TABLE components ADD COLUMN availability TEXT")
            cursor.execute("UPDATE components SET availability = 'MEDIUM'")
            
        if 'authenticity_required' not in columns:
            print("Adding authenticity_required column")
            cursor.execute("ALTER TABLE components ADD COLUMN authenticity_required BOOLEAN")
            cursor.execute("UPDATE components SET authenticity_required = 0")
            
        if 'authorization_required' not in columns:
            print("Adding authorization_required column")
            cursor.execute("ALTER TABLE components ADD COLUMN authorization_required BOOLEAN")
            cursor.execute("UPDATE components SET authorization_required = 0")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error applying migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_migration()
