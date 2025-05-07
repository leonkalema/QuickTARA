#!/usr/bin/env python3
"""
Debug current state of vulnerability setup
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def check_imports():
    """Check if all imports work correctly"""
    print("=== Checking imports ===\n")
    
    try:
        from api.routes import vulnerability
        print("✓ api.routes.vulnerability imports successfully")
    except Exception as e:
        print(f"✗ api.routes.vulnerability import failed: {e}")
    
    try:
        from api.services import vulnerability_service
        print("✓ api.services.vulnerability_service imports successfully")
    except Exception as e:
        print(f"✗ api.services.vulnerability_service import failed: {e}")
    
    try:
        from api.models import vulnerability
        print("✓ api.models.vulnerability imports successfully")
    except Exception as e:
        print(f"✗ api.models.vulnerability import failed: {e}")
    
    try:
        from db.base import Vulnerability
        print("✓ db.base.Vulnerability imports successfully")
    except Exception as e:
        print(f"✗ db.base.Vulnerability import failed: {e}")

def check_db_structure():
    """Check database table structure"""
    print("\n=== Checking database structure ===\n")
    
    try:
        from db.session import get_engine
        from sqlalchemy import inspect
        
        engine = get_engine()
        inspector = inspect(engine)
        
        if 'vulnerabilities' in inspector.get_table_names():
            columns = inspector.get_columns('vulnerabilities')
            print("✓ vulnerabilities table exists with columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("✗ vulnerabilities table does not exist")
    except Exception as e:
        print(f"✗ Error checking database: {e}")

def check_model_consistency():
    """Check model consistency between database and Pydantic"""
    print("\n=== Checking model consistency ===\n")
    
    try:
        from db.base import Vulnerability as DBVulnerability
        from api.models.vulnerability import Vulnerability as PydanticVulnerability
        
        # Get database model fields
        db_fields = [column.name for column in DBVulnerability.__table__.columns]
        
        # Get Pydantic model fields
        pydantic_fields = PydanticVulnerability.__fields__.keys()
        
        print("Database model fields:")
        print(db_fields)
        print("\nPydantic model fields:")
        print(list(pydantic_fields))
        
        # Check for mismatches
        db_only = set(db_fields) - set(pydantic_fields)
        pydantic_only = set(pydantic_fields) - set(db_fields)
        
        if db_only:
            print("\n✗ Fields in database but not in Pydantic model:")
            print(db_only)
        
        if pydantic_only:
            print("\n✗ Fields in Pydantic model but not in database:")
            print(pydantic_only)
        
        if not db_only and not pydantic_only:
            print("\n✓ Models are consistent")
    except Exception as e:
        print(f"✗ Error checking model consistency: {e}")

def check_app_routes():
    """Check if vulnerability routes are properly registered"""
    print("\n=== Checking application routes ===\n")
    
    try:
        from api.app import create_app
        from config.settings import load_settings
        
        settings = load_settings()
        app = create_app(settings)
        
        vulnerability_routes = []
        for route in app.routes:
            if "/api/vulnerability" in route.path:
                vulnerability_routes.append(route.path)
        
        if vulnerability_routes:
            print(f"✓ Found {len(vulnerability_routes)} vulnerability routes:")
            for route in vulnerability_routes:
                print(f"  - {route}")
        else:
            print("✗ No vulnerability routes found")
    except Exception as e:
        print(f"✗ Error checking routes: {e}")

def main():
    print("QuickTARA Vulnerability Setup Debugging")
    print("======================================\n")
    
    check_imports()
    check_db_structure()
    check_model_consistency()
    check_app_routes()
    
    print("\n======================================")
    print("Debug complete. Check output above for issues.")

if __name__ == "__main__":
    main()
