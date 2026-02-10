"""
Migration: Add data_profile JSON column to cra_assessments table.

Stores product data classification answers as a JSON dict of boolean flags.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "quicktara.db")


def migrate() -> None:
    """Add data_profile column if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(cra_assessments)")
    columns = [row[1] for row in cursor.fetchall()]
    if "data_profile" not in columns:
        cursor.execute(
            "ALTER TABLE cra_assessments ADD COLUMN data_profile TEXT DEFAULT '{}'"
        )
        print("Added data_profile column to cra_assessments")
    else:
        print("data_profile column already exists")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    migrate()
