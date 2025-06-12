#!/usr/bin/env python
"""
Debug script for damage scenario creation using product-centric model.
This will isolate and test each step of the process to identify issues.
"""
import os
import sys
import json
import traceback
from datetime import datetime

# Database connection
DB_PATH = os.environ.get('QUICKTARA_DB', 'sqlite:///quicktara.db')

def debug_damage_scenario_creation():
    """Debug damage scenario creation with detailed error reporting"""
    try:
        # Import SQLAlchemy using explicit imports to avoid potential circular imports
        from sqlalchemy import create_engine, Column, String, JSON, Boolean, Text, DateTime, ForeignKey
        from sqlalchemy.orm import sessionmaker, relationship
        from sqlalchemy.ext.declarative import declarative_base
        print("✓ Successfully imported SQLAlchemy")
        
        # Get database connection
        engine = create_engine(DB_PATH, echo=True)  # Enable echo to see SQL queries
        Session = sessionmaker(bind=engine)
        session = Session()
        print(f"✓ Connected to database: {DB_PATH}")
        
        # Import models - do this after SQLAlchemy to avoid import issues
        from db.product_asset_models import ProductScope, Asset, DamageScenario
        print("✓ Successfully imported models")
        
        # Step 1: Find a product scope to use
        product_scope = session.query(ProductScope).first()
        if not product_scope:
            print("❌ No product scope found in database")
            return
        print(f"✓ Found product scope: {product_scope.scope_id}")
        
        # Step 2: Find some assets to use
        assets = session.query(Asset).limit(2).all()
        if not assets:
            print("❌ No assets found in database")
            return
        print(f"✓ Found {len(assets)} assets: {[asset.asset_id for asset in assets]}")
        
        # Step 3: Generate a test scenario ID
        scenario_id = f"DS-DEBUG-{datetime.now().strftime('%H%M%S')}"
        print(f"✓ Generated scenario ID: {scenario_id}")
        
        # Step 4: Check for an existing scenario with this ID
        existing = session.query(DamageScenario).filter(DamageScenario.scenario_id == scenario_id).first()
        if existing:
            print(f"⚠️ Found existing scenario with ID {scenario_id}, will delete")
            session.delete(existing)
            session.commit()
        
        # Step 5: Create violated_properties as JSON
        violated_properties_dict = {
            "confidentiality": True,
            "integrity": True,
            "availability": False,
            "severity": "Medium"
        }
        violated_properties = json.dumps(violated_properties_dict)
        print(f"✓ Created violated_properties JSON: {violated_properties}")
        
        # Step 6: Create the damage scenario object
        print("Creating damage scenario object...")
        damage_scenario = DamageScenario(
            scenario_id=scenario_id,
            name="Debug Test Scenario",
            description="Created for debugging",
            scope_id=product_scope.scope_id,
            violated_properties=violated_properties,
            category="Operational",
            safety_impact=False,
            financial_impact=False,
            operational_impact=True,
            privacy_impact=False,
            version=1,
            is_current=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="debug_script",
            updated_by="debug_script"
        )
        print("✓ Created damage scenario object")
        
        # Step 7: Add to session and flush to get ID without committing
        try:
            print("Adding damage scenario to session and flushing...")
            session.add(damage_scenario)
            session.flush()
            print(f"✓ Successfully flushed damage scenario: {damage_scenario.scenario_id}")
        except Exception as e:
            session.rollback()
            print(f"❌ Error during flush: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return
            
        # Step 8: Set affected assets relationship
        try:
            print("Setting affected assets relationship...")
            damage_scenario.affected_assets = assets
            print(f"✓ Set {len(assets)} affected assets for damage scenario")
        except Exception as e:
            session.rollback()
            print(f"❌ Error setting affected assets: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return
        
        # Step 9: Commit the transaction
        try:
            print("Committing transaction...")
            session.commit()
            print(f"✓ Successfully committed damage scenario with relationships")
        except Exception as e:
            session.rollback()
            print(f"❌ Error during commit: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return
            
        # Step 10: Verify the damage scenario was created correctly
        try:
            print("Verifying damage scenario was created...")
            session.refresh(damage_scenario)
            print(f"✓ Scenario has {len(damage_scenario.affected_assets)} affected assets")
            print(f"✓ Scenario violated_properties: {damage_scenario.violated_properties}")
            print("✅ ALL TESTS PASSED - Damage scenario creation works!")
        except Exception as e:
            print(f"❌ Error verifying damage scenario: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        try:
            session.close()
        except:
            pass

if __name__ == "__main__":
    debug_damage_scenario_creation()
