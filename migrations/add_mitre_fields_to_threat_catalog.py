"""
Migration: Add MITRE ATT&CK provenance fields to threat_catalog table
Purpose: Track data source, ATT&CK version, technique IDs, and automotive relevance
"""
import sqlite3
import sys
from pathlib import Path


MIGRATION_NAME = "add_mitre_fields_to_threat_catalog"

COLUMNS_TO_ADD = [
    ("source", "TEXT NOT NULL DEFAULT 'custom'"),
    ("source_version", "TEXT"),
    ("mitre_technique_id", "TEXT"),
    ("mitre_tactic", "TEXT"),
    ("automotive_relevance", "INTEGER NOT NULL DEFAULT 3"),
    ("automotive_context", "TEXT"),
    ("is_user_modified", "INTEGER NOT NULL DEFAULT 0"),
]


def column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    """Check if a column already exists in a table."""
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns = [row[1] for row in cursor.fetchall()]
    return column in existing_columns


def run_migration(db_path: str) -> None:
    """Add MITRE provenance columns to the threat_catalog table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        for col_name, col_def in COLUMNS_TO_ADD:
            if column_exists(cursor, "threat_catalog", col_name):
                print(f"  Column '{col_name}' already exists, skipping.")
                continue
            sql = f"ALTER TABLE threat_catalog ADD COLUMN {col_name} {col_def}"
            cursor.execute(sql)
            print(f"  Added column '{col_name}' to threat_catalog.")

        # Create index on mitre_technique_id for fast lookups
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS ix_threat_catalog_mitre_technique_id "
            "ON threat_catalog (mitre_technique_id)"
        )
        print("  Created index on mitre_technique_id.")

        conn.commit()
        print(f"Migration '{MIGRATION_NAME}' completed successfully.")
    except Exception as exc:
        conn.rollback()
        print(f"Migration '{MIGRATION_NAME}' failed: {exc}", file=sys.stderr)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else str(Path("quicktara.db"))
    print(f"Running migration '{MIGRATION_NAME}' on {db_file}")
    run_migration(db_file)
