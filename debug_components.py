#!/usr/bin/env python3
"""
Debug script to list all components in the database
"""
from db.session import SessionLocal
from db.base import Component

def main():
    """List all components in the database"""
    db = SessionLocal()
    try:
        print("COMPONENTS IN DATABASE:")
        components = db.query(Component).all()
        if not components:
            print("No components found in the database!")
            return
            
        for c in components:
            print(f"ID: {c.component_id} | Type: {c.type} | Name: {c.name}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
