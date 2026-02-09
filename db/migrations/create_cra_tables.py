"""
Migration: Create CRA compliance tables

Tables created:
  - cra_assessments
  - cra_requirement_statuses
  - cra_compensating_controls
"""
import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from db.session import get_engine

logger = logging.getLogger(__name__)

MIGRATION_SQL = """
CREATE TABLE IF NOT EXISTS cra_assessments (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL UNIQUE,
    classification TEXT,
    classification_answers TEXT DEFAULT '{}',
    product_type TEXT DEFAULT 'current',
    compliance_deadline TEXT,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assessor_id TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    overall_compliance_pct INTEGER DEFAULT 0,
    support_period_end TEXT,
    eoss_date TEXT,
    notes TEXT,
    automotive_exception INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES product_scopes(scope_id)
);

CREATE TABLE IF NOT EXISTS cra_requirement_statuses (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'not_started',
    auto_mapped INTEGER DEFAULT 0,
    mapped_artifact_type TEXT,
    mapped_artifact_count INTEGER DEFAULT 0,
    owner TEXT,
    target_date TEXT,
    evidence_notes TEXT,
    evidence_links TEXT DEFAULT '[]',
    gap_description TEXT,
    remediation_plan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES cra_assessments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cra_compensating_controls (
    id TEXT PRIMARY KEY,
    assessment_id TEXT NOT NULL,
    control_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    implementation_status TEXT NOT NULL DEFAULT 'planned',
    supplier_actions TEXT,
    oem_actions TEXT,
    residual_risk TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES cra_assessments(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cra_assessments_product
    ON cra_assessments(product_id);
CREATE INDEX IF NOT EXISTS idx_cra_req_status_assessment
    ON cra_requirement_statuses(assessment_id);
CREATE INDEX IF NOT EXISTS idx_cra_comp_ctrl_assessment
    ON cra_compensating_controls(assessment_id);
"""


def run_migration() -> None:
    """Execute the CRA tables migration."""
    engine = get_engine()
    with engine.connect() as conn:
        for statement in MIGRATION_SQL.strip().split(";"):
            cleaned = statement.strip()
            if cleaned:
                conn.execute(text(cleaned))
        conn.commit()
    logger.info("CRA tables migration completed successfully")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migration()
    print("CRA tables created successfully.")
