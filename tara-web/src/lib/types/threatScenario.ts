export type ImpactRatingLevel = 'negligible' | 'moderate' | 'major' | 'severe';

export interface ImpactRating {
  safety: ImpactRatingLevel;
  financial: ImpactRatingLevel;
  operational: ImpactRatingLevel;
  privacy: ImpactRatingLevel;
}

export interface ThreatScenario {
  threat_scenario_id: string;
  damage_scenario_id: string;
  name: string;
  description: string;
  attack_vector: string;
  scope_id: string;
  scope_version: number;
  version: number;
  revision_notes?: string;
  status: 'draft' | 'accepted';
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateThreatScenarioRequest {
  threat_scenario_id?: string; // Auto-generated if not provided
  damage_scenario_id: string;
  name: string;
  description: string;
  attack_vector: string;
  scope_id: string;
  scope_version: number;
}

export interface UpdateThreatScenarioRequest {
  name?: string;
  description?: string;
  attack_vector?: string;
}

export interface ThreatScenarioListResponse {
  threat_scenarios: ThreatScenario[];
  total: number;
}
