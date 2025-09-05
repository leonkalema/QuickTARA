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
  elapsed_time: number; // 0-19 scale
  specialist_expertise: number; // 0-8 scale  
  knowledge_of_target: number; // 0-11 scale
  window_of_opportunity: number; // 0-10 scale
  equipment: number; // 0-9 scale
  overall_rating?: number; // Calculated total
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
