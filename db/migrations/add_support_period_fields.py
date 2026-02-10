"""
Migration: Add support_period_years and support_period_justification
to cra_assessments table.

Per CRA FAQs v1.2 Section 4.5:
- Minimum 5 years support period required.
- Less than 5 years only if product expected to be in use less than 5 years.
- Justification must be documented in technical documentation.
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "quicktara.db"


def migrate() -> None:
    """Add support period columns to cra_assessments."""
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    existing = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(cra_assessments)").fetchall()
    }
    added: list[str] = []
    if "support_period_years" not in existing:
        cursor.execute(
            "ALTER TABLE cra_assessments ADD COLUMN support_period_years INTEGER"
        )
        added.append("support_period_years")
    if "support_period_justification" not in existing:
        cursor.execute(
            "ALTER TABLE cra_assessments ADD COLUMN support_period_justification TEXT"
        )
        added.append("support_period_justification")
    conn.commit()
    conn.close()
    if added:
        print(f"Added columns: {', '.join(added)}")
    else:
        print("Columns already exist — nothing to do.")


if __name__ == "__main__":
    migrate()
