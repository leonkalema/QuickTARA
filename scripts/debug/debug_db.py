#!/usr/bin/env python3
"""
Debug database script to check component storage and access
"""
from db.session import SessionLocal
from db.base import Component as DBComponent
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Check the database for components"""
    db = SessionLocal()
    try:
        # 1. List all components in database
        logger.info("===== LISTING ALL COMPONENTS IN DATABASE =====")
        components = db.query(DBComponent).all()
        
        if not components:
            logger.error("No components found in the database!")
            return
            
        for c in components:
            logger.info(f"ID: {c.component_id} | Type: {c.type} | Name: {c.name}")
        
        # 2. Test specific component lookups by ID
        test_ids = ["ECU001", "SNS001", "GWY001"]
        logger.info("\n===== TESTING COMPONENT LOOKUPS =====")
        
        # Exact match
        for comp_id in test_ids:
            result = db.query(DBComponent).filter(DBComponent.component_id == comp_id).first()
            logger.info(f"Exact lookup for '{comp_id}': {'FOUND' if result else 'NOT FOUND'}")
            
        # Case-insensitive match
        for comp_id in test_ids:
            result = db.query(DBComponent).filter(DBComponent.component_id.ilike(comp_id)).first()
            logger.info(f"Case-insensitive lookup for '{comp_id}': {'FOUND' if result else 'NOT FOUND'}")
            
        # Try lowercase
        for comp_id in test_ids:
            lower_id = comp_id.lower()
            result = db.query(DBComponent).filter(DBComponent.component_id == lower_id).first()
            logger.info(f"Lowercase exact lookup for '{lower_id}': {'FOUND' if result else 'NOT FOUND'}")
            
        # Try uppercase
        for comp_id in test_ids:
            upper_id = comp_id.upper()
            result = db.query(DBComponent).filter(DBComponent.component_id == upper_id).first()
            logger.info(f"Uppercase exact lookup for '{upper_id}': {'FOUND' if result else 'NOT FOUND'}")
            
        # 3. Check table structure
        logger.info("\n===== COMPONENT TABLE DETAILS =====")
        from sqlalchemy import inspect
        inspector = inspect(db.get_bind())
        columns = inspector.get_columns('components')
        logger.info(f"Columns in components table: {[col['name'] for col in columns]}")
        pk = inspector.get_pk_constraint('components')
        logger.info(f"Primary key: {pk}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
