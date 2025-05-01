#!/usr/bin/env python3
"""
Setup Attack Path Analyses Table

This is a direct SQL approach to create the attack_path_analyses table.
This script can be run directly or imported from the API initialization.
"""
import logging
from sqlalchemy import text
from db.session import get_session_factory

logger = logging.getLogger(__name__)

# SQL to create the attack_path_analyses table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS attack_path_analyses (
    analysis_id TEXT PRIMARY KEY,
    component_count INTEGER NOT NULL,
    total_paths INTEGER NOT NULL,
    high_risk_paths INTEGER NOT NULL,
    total_chains INTEGER NOT NULL,
    high_risk_chains INTEGER NOT NULL,
    entry_points JSON,
    critical_targets JSON,
    scope_id TEXT,
    primary_component_id TEXT,
    created_at TEXT NOT NULL
);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_attack_path_analyses_scope_id 
ON attack_path_analyses (scope_id);

CREATE INDEX IF NOT EXISTS idx_attack_path_analyses_primary_component_id 
ON attack_path_analyses (primary_component_id);
"""

def setup_attack_path_analyses_table():
    """Create the attack_path_analyses table if it doesn't exist"""
    try:
        logger.info("Setting up attack_path_analyses table...")
        session_factory = get_session_factory()
        with session_factory() as session:
            session.execute(text(CREATE_TABLE_SQL))
            session.commit()
        logger.info("attack_path_analyses table setup complete")
        return True
    except Exception as e:
        logger.error(f"Error setting up attack_path_analyses table: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    result = setup_attack_path_analyses_table()
    if result:
        print("Successfully created attack_path_analyses table")
    else:
        print("Failed to create attack_path_analyses table")
