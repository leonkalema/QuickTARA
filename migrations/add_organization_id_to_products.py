"""
Migration: Add organization_id column to product_scopes table
"""
from sqlalchemy import create_engine, text

def run_migration():
    engine = create_engine('sqlite:///quicktara.db')
    
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("PRAGMA table_info(product_scopes)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'organization_id' not in columns:
            # Add organization_id column
            conn.execute(text("""
                ALTER TABLE product_scopes 
                ADD COLUMN organization_id VARCHAR REFERENCES organizations(organization_id)
            """))
            conn.commit()
            print("Added organization_id column to product_scopes table")
        else:
            print("organization_id column already exists")
        
        # Create index if not exists
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_product_scopes_organization_id 
                ON product_scopes(organization_id)
            """))
            conn.commit()
            print("Created index on organization_id")
        except Exception as e:
            print(f"Index may already exist: {e}")

if __name__ == "__main__":
    run_migration()
