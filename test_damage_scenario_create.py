#!/usr/bin/env python
"""
Test script to create a damage scenario directly using SQLAlchemy.
This bypasses the API to help isolate database-related issues.
"""
import os
import sys
import json
from datetime import datetime

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import required modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models
from db.product_asset_models import ProductScope, Asset, DamageScenario

# Constants
DB_PATH = os.environ.get('QUICKTARA_DB', 'sqlite:///quicktara.db')

def get_engine():
    """Get database engine"""
    return create_engine(DB_PATH)

def get_session():
    """Create a database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def create_test_damage_scenario():
    """Create a test damage scenario directly using SQLAlchemy"""
    session = get_session()
    
    try:
        print("Starting test damage scenario creation...")
        
        # Generate a unique ID for the damage scenario
        scenario_id = "DS-TEST-123"
        
        # Check if this scenario already exists and delete if it does
        existing = session.query(DamageScenario).filter(DamageScenario.scenario_id == scenario_id).first()
        if existing:
            print(f"Deleting existing damage scenario: {scenario_id}")
            session.delete(existing)
            session.commit()
        
        # Get product scope to use
        product_scope = session.query(ProductScope).first()
        if not product_scope:
            print("No product scope found in database")
            return
        print(f"Using product scope: {product_scope.scope_id}")
        
        # Get assets to use
        assets = session.query(Asset).limit(2).all()
        if not assets:
            print("No assets found in database")
            return
        print(f"Found {len(assets)} assets to use")
        
        # Create violated_properties as a dict (will be converted to JSON by SQLAlchemy)
        violated_properties = {
            "confidentiality": True,
            "integrity": True,
            "availability": False,
            "severity": "Medium"
        }
        
        # Create the damage scenario
        print("Creating damage scenario...")
        db_scenario = DamageScenario(
            scenario_id=scenario_id,
            name="Test Damage Scenario",
            description="Created by test script",
            category="Operational",
            violated_properties=violated_properties,
            scope_id=product_scope.scope_id,
            safety_impact=False,
            financial_impact=False,
            operational_impact=True,
            privacy_impact=False,
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="test_script",
            updated_by="test_script"
        )
        
        print(f"Adding damage scenario to session...")
        session.add(db_scenario)
        session.flush()
        print(f"Created damage scenario: {db_scenario.scenario_id}")
        
        # Add affected assets
        print(f"Adding affected assets...")
        db_scenario.affected_assets = assets
        
        # Commit the transaction
        print("Committing changes...")
        session.commit()
        print(f"Damage scenario created successfully: {scenario_id}")
        
        # Verify the relationship was created
        session.refresh(db_scenario)
        print(f"Damage scenario has {len(db_scenario.affected_assets)} affected assets")
        
    except Exception as e:
        session.rollback()
        print(f"ERROR: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        session.close()

if __name__ == "__main__":
    create_test_damage_scenario()
