export interface AttackPath {
  attack_path_id: string;
  threat_scenario_id: string;
  name: string;
  description?: string;
  attack_steps: string; // Multi-line text with steps separated by lines
  feasibility_rating: FeasibilityRating;
  created_at?: string;
  updated_at?: string;
}

export interface FeasibilityRating {
  elapsed_time: number; // 1-4 scale
  specialist_expertise: number; // 1-4 scale  
  knowledge_of_target: number; // 1-4 scale
  window_of_opportunity: number; // 1-4 scale
  equipment: number; // 1-4 scale
  overall_rating?: number; // Calculated average
}

export interface CreateAttackPathRequest {
  threat_scenario_id: string;
  name: string;
  description?: string;
  attack_steps: string;
  feasibility_rating: FeasibilityRating;
}

export interface AttackPathResponse {
  attack_paths: AttackPath[];
  total: number;
}
