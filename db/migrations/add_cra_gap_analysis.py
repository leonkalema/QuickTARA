"""
Migration: Add CRA Gap Analysis fields

Adds:
1. gap_severity and residual_risk_level to cra_requirement_statuses
2. Junction table cra_control_requirement_links for many-to-many
"""
import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "quicktara.db"
)


def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add gap_severity to cra_requirement_statuses
    try:
        cursor.execute("""
            ALTER TABLE cra_requirement_statuses
            ADD COLUMN gap_severity VARCHAR(20) DEFAULT 'none'
        """)
        print("Added gap_severity column to cra_requirement_statuses")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("gap_severity column already exists")
        else:
            raise

    # Add residual_risk_level to cra_requirement_statuses
    try:
        cursor.execute("""
            ALTER TABLE cra_requirement_statuses
            ADD COLUMN residual_risk_level VARCHAR(20) DEFAULT 'none'
        """)
        print("Added residual_risk_level column to cra_requirement_statuses")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("residual_risk_level column already exists")
        else:
            raise

    # Create junction table for control → requirement links
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cra_control_requirement_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            control_id VARCHAR(50) NOT NULL,
            requirement_status_id VARCHAR(50) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (control_id) REFERENCES cra_compensating_controls(id) ON DELETE CASCADE,
            FOREIGN KEY (requirement_status_id) REFERENCES cra_requirement_statuses(id) ON DELETE CASCADE,
            UNIQUE(control_id, requirement_status_id)
        )
    """)
    print("Created cra_control_requirement_links junction table")

    conn.commit()
    conn.close()
    print("Migration complete!")


if __name__ == "__main__":
    run_migration()
