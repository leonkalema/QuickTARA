-- Create damage_scenarios table
CREATE TABLE IF NOT EXISTS damage_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    damage_category TEXT NOT NULL,
    impact_type TEXT NOT NULL,
    confidentiality_impact BOOLEAN DEFAULT 0,
    integrity_impact BOOLEAN DEFAULT 0,
    availability_impact BOOLEAN DEFAULT 0,
    severity TEXT NOT NULL,
    impact_details JSON,
    version INTEGER DEFAULT 1,
    revision_notes TEXT,
    is_deleted BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scope_id TEXT NOT NULL,
    primary_component_id TEXT NOT NULL,
    FOREIGN KEY (scope_id) REFERENCES system_scopes(scope_id),
    FOREIGN KEY (primary_component_id) REFERENCES components(component_id)
);

-- Create component_damage_scenario association table
CREATE TABLE IF NOT EXISTS component_damage_scenario (
    component_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    FOREIGN KEY (component_id) REFERENCES components(component_id),
    FOREIGN KEY (scenario_id) REFERENCES damage_scenarios(scenario_id),
    UNIQUE (component_id, scenario_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS ix_damage_scenarios_scenario_id ON damage_scenarios(scenario_id);
CREATE INDEX IF NOT EXISTS ix_damage_scenarios_scope_id ON damage_scenarios(scope_id);
CREATE INDEX IF NOT EXISTS ix_damage_scenarios_primary_component_id ON damage_scenarios(primary_component_id);
