-- SQL to create the attack_path_analyses table
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
