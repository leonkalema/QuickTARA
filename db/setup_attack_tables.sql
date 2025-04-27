-- SQLite script to set up Attack Path Analysis tables

-- Create attack paths table
CREATE TABLE IF NOT EXISTS attack_paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path_id TEXT UNIQUE NOT NULL,
    analysis_id TEXT NOT NULL,
    scope_id TEXT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    path_type TEXT NOT NULL,
    complexity TEXT NOT NULL,
    entry_point_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    success_likelihood REAL NOT NULL,
    impact TEXT NOT NULL,  -- JSON format
    risk_score REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
    FOREIGN KEY (scope_id) REFERENCES system_scopes(scope_id),
    FOREIGN KEY (entry_point_id) REFERENCES components(component_id),
    FOREIGN KEY (target_id) REFERENCES components(component_id)
);

-- Create attack steps table
CREATE TABLE IF NOT EXISTS attack_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_id TEXT UNIQUE NOT NULL,
    path_id TEXT NOT NULL,
    component_id TEXT NOT NULL,
    step_type TEXT NOT NULL,
    description TEXT NOT NULL,
    prerequisites TEXT,  -- JSON format
    vulnerability_ids TEXT,  -- JSON format
    threat_ids TEXT,  -- JSON format
    "order" INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (path_id) REFERENCES attack_paths(path_id),
    FOREIGN KEY (component_id) REFERENCES components(component_id)
);

-- Create attack chains table
CREATE TABLE IF NOT EXISTS attack_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_id TEXT UNIQUE NOT NULL,
    analysis_id TEXT NOT NULL,
    scope_id TEXT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    entry_points TEXT NOT NULL,  -- JSON format
    targets TEXT NOT NULL,  -- JSON format
    attack_goal TEXT NOT NULL,
    complexity TEXT NOT NULL,
    success_likelihood REAL NOT NULL,
    impact TEXT NOT NULL,  -- JSON format
    risk_score REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
    FOREIGN KEY (scope_id) REFERENCES system_scopes(scope_id)
);

-- Create association table for attack chains and paths
CREATE TABLE IF NOT EXISTS attack_chain_paths (
    chain_id TEXT NOT NULL,
    path_id TEXT NOT NULL,
    PRIMARY KEY (chain_id, path_id),
    FOREIGN KEY (chain_id) REFERENCES attack_chains(chain_id),
    FOREIGN KEY (path_id) REFERENCES attack_paths(path_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_attack_steps_path_id ON attack_steps(path_id);
CREATE INDEX IF NOT EXISTS idx_attack_steps_component_id ON attack_steps(component_id);
CREATE INDEX IF NOT EXISTS idx_attack_paths_analysis_id ON attack_paths(analysis_id);
CREATE INDEX IF NOT EXISTS idx_attack_paths_scope_id ON attack_paths(scope_id);
CREATE INDEX IF NOT EXISTS idx_attack_chains_analysis_id ON attack_chains(analysis_id);
CREATE INDEX IF NOT EXISTS idx_attack_chains_scope_id ON attack_chains(scope_id);

-- Sample data for testing: Insert sample attack path
INSERT INTO attack_paths (
    path_id, analysis_id, name, description, path_type, complexity, 
    entry_point_id, target_id, success_likelihood, impact, risk_score
)
SELECT 
    'path_sample1', 
    id,  -- Use the first analysis ID from the analyses table
    'Sample Attack Path from External to ECU',
    'This is a sample attack path from an external component to a critical ECU',
    'Multi-Step',
    'Medium',
    c1.component_id,  -- Use the first component as entry point
    c2.component_id,  -- Use the second component as target
    0.7,
    '{"confidentiality": 7, "integrity": 9, "availability": 8}',
    6.3
FROM 
    analyses, 
    components c1, 
    components c2
WHERE 
    c1.component_id != c2.component_id
LIMIT 1;

-- Sample data: Insert steps for the sample attack path
INSERT INTO attack_steps (
    step_id, path_id, component_id, step_type, description, "order"
)
SELECT 
    'step_entry_sample1', 
    'path_sample1',
    c1.component_id,
    'Initial Access',
    'Initial access via external interface',
    0
FROM components c1 LIMIT 1;

INSERT INTO attack_steps (
    step_id, path_id, component_id, step_type, description, "order"
)
SELECT 
    'step_lateral_sample1', 
    'path_sample1',
    c2.component_id,
    'Lateral Movement',
    'Move laterally through the network',
    1
FROM components c2 
WHERE c2.component_id != (SELECT component_id FROM attack_steps WHERE step_id = 'step_entry_sample1')
LIMIT 1;

INSERT INTO attack_steps (
    step_id, path_id, component_id, step_type, description, "order"
)
SELECT 
    'step_target_sample1', 
    'path_sample1',
    c3.component_id,
    'Impact',
    'Compromise target ECU',
    2
FROM components c3 
WHERE c3.component_id != (SELECT component_id FROM attack_steps WHERE step_id = 'step_entry_sample1')
  AND c3.component_id != (SELECT component_id FROM attack_steps WHERE step_id = 'step_lateral_sample1')
LIMIT 1;

-- Sample data: Insert attack chain
INSERT INTO attack_chains (
    chain_id, analysis_id, name, description, entry_points, targets, 
    attack_goal, complexity, success_likelihood, impact, risk_score
)
SELECT 
    'chain_sample1',
    analysis_id,
    'Sample Attack Chain',
    'This is a sample attack chain involving multiple components',
    '[' || (SELECT json_group_array(component_id) FROM (SELECT component_id FROM components LIMIT 2)) || ']',
    '[' || (SELECT json_group_array(component_id) FROM (SELECT component_id FROM components LIMIT 2 OFFSET 2)) || ']',
    'Vehicle Control System Compromise',
    'Medium',
    0.6,
    '{"confidentiality": 8, "integrity": 9, "availability": 10}',
    6.0
FROM attack_paths
WHERE path_id = 'path_sample1';

-- Link sample path to the chain
INSERT INTO attack_chain_paths (chain_id, path_id) VALUES ('chain_sample1', 'path_sample1');
