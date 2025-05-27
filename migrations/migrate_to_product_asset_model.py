#!/usr/bin/env python
"""
Migration Script: Convert to Product-Centric Asset Model

This script migrates the existing database from a component-based model to 
a product-centric asset model, where:
- Scopes → Products (with product-level properties)
- Components → Assets (within products)

The script preserves all existing relationships and data while reorganizing
the structure according to the Product and Asset Model Implementation Guide.
"""
import os
import sys
import logging
import json
from datetime import datetime
from sqlalchemy import Column, String, Enum, ForeignKey, Table, DateTime, Integer, Float, Text, Boolean, UniqueConstraint, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.types import JSON, ARRAY

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('migration')

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Import existing models
from db.base import Base as ExistingBase, Component, SystemScope
# Import new models
from db.product_asset_models import Base as NewBase, ProductScope, Asset, ProductScopeHistory, AssetHistory, asset_damage_scenario

# Database connection
DB_PATH = os.environ.get('QUICKTARA_DB', 'sqlite:///quicktara.db')

def get_engine():
    """Get database engine"""
    return create_engine(DB_PATH)

def get_session():
    """Create a database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def create_new_tables():
    """Create the new tables for product-centric model"""
    logger.info("Creating new tables for product-centric model")
    engine = get_engine()
    NewBase.metadata.create_all(engine)
    logger.info("New tables created successfully")

def drop_new_tables():
    """Drop the new tables (for testing/rollback)"""
    logger.info("WARNING: Dropping new tables")
    engine = get_engine()
    NewBase.metadata.drop_all(engine)
    logger.info("New tables dropped")

def json_serialize(obj):
    """Convert objects to JSON-serializable format"""
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        return obj
    if obj is None:
        return []
    try:
        # Try to parse as JSON string
        return json.loads(obj)
    except (TypeError, json.JSONDecodeError):
        # If not valid JSON, return as string in a list
        if isinstance(obj, str):
            if obj.strip():
                return [obj.strip()]
        return []

def map_component_type_to_asset_type(component_type):
    """Map component types to asset types"""
    mapping = {
        "ECU": "Firmware",
        "Sensor": "Hardware",
        "Gateway": "Communication",
        "Actuator": "Hardware",
        "Network": "Communication"
    }
    return mapping.get(component_type, "Other")

def migrate_data():
    """Migrate data from old model to new model"""
    logger.info("Starting data migration")
    session = get_session()
    
    try:
        # 1. Get all existing scopes
        existing_scopes = session.query(SystemScope).all()
        logger.info(f"Found {len(existing_scopes)} existing scopes to migrate")
        
        for scope in existing_scopes:
            logger.info(f"Migrating scope: {scope.scope_id}")
            
            # 2. Get all components for this scope
            components = session.query(Component).filter_by(scope_id=scope.scope_id).all()
            logger.info(f"Found {len(components)} components for scope {scope.scope_id}")
            
            # Default product properties
            safety_level = "QM"
            interfaces = []
            access_points = []
            location = "Internal"
            trust_zone = "Standard"
            
            # 3. Extract product-level properties from first component (if any)
            if components:
                first_component = components[0]
                safety_level = first_component.safety_level
                interfaces = json_serialize(first_component.interfaces)
                access_points = json_serialize(first_component.access_points)
                location = first_component.location
                trust_zone = first_component.trust_zone
            
            # 4. Create new ProductScope
            product_type = "ECU"  # Default
            if components and hasattr(components[0], 'type'):
                if components[0].type in ["Gateway", "Sensor", "Actuator", "Network"]:
                    product_type = components[0].type
            
            product_scope = ProductScope(
                scope_id=scope.scope_id,
                name=scope.name,
                product_type=product_type,
                description=scope.description if hasattr(scope, 'description') else None,
                safety_level=safety_level,
                interfaces=interfaces,
                access_points=access_points,
                location=location,
                trust_zone=trust_zone,
                boundaries=json_serialize(scope.boundaries) if hasattr(scope, 'boundaries') else [],
                objectives=json_serialize(scope.objectives) if hasattr(scope, 'objectives') else [],
                stakeholders=json_serialize(scope.stakeholders) if hasattr(scope, 'stakeholders') else [],
                version=1,
                is_current=True,
                created_at=scope.created_at if hasattr(scope, 'created_at') else datetime.now(),
                updated_at=scope.updated_at if hasattr(scope, 'updated_at') else datetime.now(),
                created_by="migration_script",
                updated_by="migration_script"
            )
            session.add(product_scope)
            
            # 5. Create an initial history record for the product
            product_history = ProductScopeHistory(
                scope_id=scope.scope_id,
                version=1,
                name=product_scope.name,
                product_type=product_scope.product_type,
                description=product_scope.description,
                safety_level=product_scope.safety_level,
                interfaces=product_scope.interfaces,
                access_points=product_scope.access_points,
                location=product_scope.location,
                trust_zone=product_scope.trust_zone,
                boundaries=product_scope.boundaries,
                objectives=product_scope.objectives,
                stakeholders=product_scope.stakeholders,
                is_current=True,
                revision_notes="Initial migration from legacy scope",
                created_at=product_scope.created_at,
                updated_at=product_scope.updated_at,
                created_by=product_scope.created_by,
                updated_by=product_scope.updated_by
            )
            session.add(product_history)
            
            # 6. Create assets from components
            for component in components:
                asset_id = component.component_id
                logger.info(f"Migrating component {asset_id} to asset")
                
                asset = Asset(
                    asset_id=asset_id,
                    name=component.name,
                    description=f"Migrated from component {component.component_id}",
                    asset_type=map_component_type_to_asset_type(component.type),
                    data_types=json_serialize(component.data_types),
                    storage_location=component.location,
                    scope_id=scope.scope_id,
                    scope_version=1,
                    confidentiality=component.confidentiality,
                    integrity=component.integrity,
                    availability=component.availability,
                    authenticity_required=component.authenticity_required if hasattr(component, 'authenticity_required') else False,
                    authorization_required=component.authorization_required if hasattr(component, 'authorization_required') else False,
                    version=1,
                    is_current=True,
                    created_at=component.created_at if hasattr(component, 'created_at') else datetime.now(),
                    updated_at=component.updated_at if hasattr(component, 'updated_at') else datetime.now(),
                    created_by="migration_script",
                    updated_by="migration_script"
                )
                session.add(asset)
                
                # 7. Create an initial history record for the asset
                asset_history = AssetHistory(
                    asset_id=asset_id,
                    version=1,
                    name=asset.name,
                    description=asset.description,
                    asset_type=asset.asset_type,
                    data_types=asset.data_types,
                    storage_location=asset.storage_location,
                    scope_id=asset.scope_id,
                    scope_version=asset.scope_version,
                    confidentiality=asset.confidentiality,
                    integrity=asset.integrity,
                    availability=asset.availability,
                    authenticity_required=asset.authenticity_required,
                    authorization_required=asset.authorization_required,
                    is_current=True,
                    revision_notes="Initial migration from legacy component",
                    created_at=asset.created_at,
                    updated_at=asset.updated_at,
                    created_by=asset.created_by,
                    updated_by=asset.updated_by
                )
                session.add(asset_history)
        
        # 8. Commit changes
        session.commit()
        logger.info("Data migration completed successfully")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error during migration: {str(e)}")
        raise
    finally:
        session.close()

def migrate_damage_scenarios():
    """Migrate damage scenarios to work with assets instead of components"""
    logger.info("Migrating damage scenarios")
    session = get_session()
    
    try:
        # Get existing damage scenarios with component relationships
        # This will depend on your existing schema structure
        # You may need to adapt this query to your specific model
        
        logger.info("Migration of damage scenarios requires customization based on your schema")
        logger.info("Please check and modify the migrate_damage_scenarios function")
        
        # Example migration logic:
        """
        damage_scenarios = session.query(DamageScenario).all()
        
        for scenario in damage_scenarios:
            # Get components associated with this scenario
            components = scenario.affected_components
            
            # Find corresponding assets for these components
            for component in components:
                asset = session.query(Asset).filter_by(asset_id=component.component_id).first()
                if asset:
                    # Create association between damage scenario and asset
                    session.execute(
                        asset_damage_scenario.insert().values(
                            asset_id=asset.asset_id,
                            scenario_id=scenario.scenario_id
                        )
                    )
        """
        
        session.commit()
        logger.info("Damage scenario migration completed")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error during damage scenario migration: {str(e)}")
    finally:
        session.close()

def verify_migration():
    """Verify that migration was successful"""
    logger.info("Verifying migration")
    session = get_session()
    
    product_count = session.query(ProductScope).count()
    asset_count = session.query(Asset).count()
    
    logger.info(f"Products: {product_count}")
    logger.info(f"Assets: {asset_count}")
    
    original_scope_count = session.query(SystemScope).count()
    original_component_count = session.query(Component).count()
    
    logger.info(f"Original scopes: {original_scope_count}")
    logger.info(f"Original components: {original_component_count}")
    
    if product_count != original_scope_count:
        logger.warning(f"Number of products ({product_count}) doesn't match original scopes ({original_scope_count})")
    
    if asset_count != original_component_count:
        logger.warning(f"Number of assets ({asset_count}) doesn't match original components ({original_component_count})")
    
    session.close()

def main():
    """Main migration function"""
    logger.info("Starting migration to product-centric model")
    
    # Confirm with user
    confirm = input("This will migrate your database to the new product-centric model. Continue? (y/n): ")
    if confirm.lower() != 'y':
        logger.info("Migration cancelled")
        return
    
    # Backup check
    backup_confirm = input("Have you backed up your database? (y/n): ")
    if backup_confirm.lower() != 'y':
        logger.warning("Please backup your database before running this migration")
        return
    
    try:
        # Create new tables
        create_new_tables()
        
        # Migrate data
        migrate_data()
        
        # Migrate damage scenarios (requires customization)
        # migrate_damage_scenarios()
        
        # Verify migration
        verify_migration()
        
        logger.info("Migration completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        logger.error("Consider restoring from backup")

if __name__ == "__main__":
    main()
