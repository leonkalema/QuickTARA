-- Add SFOP impact rating fields to damage_scenarios table

-- SFOP rating fields
ALTER TABLE damage_scenarios ADD COLUMN safety_impact TEXT;
ALTER TABLE damage_scenarios ADD COLUMN financial_impact TEXT;
ALTER TABLE damage_scenarios ADD COLUMN operational_impact TEXT;
ALTER TABLE damage_scenarios ADD COLUMN privacy_impact TEXT;
ALTER TABLE damage_scenarios ADD COLUMN impact_rating_notes TEXT;

-- Audit fields for regulatory compliance (UN R155 and ISO 21434)
ALTER TABLE damage_scenarios ADD COLUMN sfop_rating_auto_generated BOOLEAN NOT NULL DEFAULT 1;
ALTER TABLE damage_scenarios ADD COLUMN sfop_rating_last_edited_by TEXT;
ALTER TABLE damage_scenarios ADD COLUMN sfop_rating_last_edited_at TIMESTAMP;
ALTER TABLE damage_scenarios ADD COLUMN sfop_rating_override_reason TEXT;
