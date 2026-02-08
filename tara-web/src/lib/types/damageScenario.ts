export type ImpactRatingLevel = 'negligible' | 'moderate' | 'major' | 'severe';

export interface ImpactRating {
  safety: ImpactRatingLevel;
  financial: ImpactRatingLevel;
  operational: ImpactRatingLevel;
  privacy: ImpactRatingLevel;
}

export interface DamageScenario {
  scenario_id: string;
  damage_scenario_id?: string; // New DS-XXX format ID
  name: string;
  description?: string;
  damage_category: DamageCategory;
  impact_type: ImpactType;
  confidentiality_impact: boolean;
  integrity_impact: boolean;
  availability_impact: boolean;
  severity: SeverityLevel;
  impact_details?: Record<string, any>;
  impact_rating?: ImpactRating; // New structured impact ratings
  impact_rating_notes?: string;
  scope_id: string;
  primary_component_id: string;
  affected_component_ids: string[];
  // SFOP Impact fields
  safety_impact?: ImpactRatingLevel;
  financial_impact?: ImpactRatingLevel;
  operational_impact?: ImpactRatingLevel;
  privacy_impact?: ImpactRatingLevel;
  version: number;
  revision_notes?: string;
  status: 'draft' | 'accepted';
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateDamageScenarioRequest {
  damage_scenario_id?: string; // Auto-generated if not provided
  name: string;
  description?: string;
  damage_category: DamageCategory;
  impact_type: ImpactType;
  confidentiality_impact: boolean;
  integrity_impact: boolean;
  availability_impact: boolean;
  severity: SeverityLevel;
  impact_rating?: ImpactRating;
  scope_id: string;
  primary_component_id: string;
  scenario_id?: string;
  version?: number;
  revision_notes?: string;
}

export interface UpdateDamageScenarioRequest {
  name?: string;
  description?: string;
  damage_category?: DamageCategory;
  impact_type?: ImpactType;
  confidentiality_impact?: boolean;
  integrity_impact?: boolean;
  availability_impact?: boolean;
  severity?: SeverityLevel;
  primary_component_id?: string;
  scope_id?: string;
  version?: number;
  revision_notes?: string;
}

export interface DamageScenariosResponse {
  scenarios: DamageScenario[];
  total: number;
}

export enum DamageCategory {
  PHYSICAL = "Physical",
  OPERATIONAL = "Operational", 
  FINANCIAL = "Financial",
  PRIVACY = "Privacy",
  SAFETY = "Safety",
  ENVIRONMENTAL = "Environmental",
  REPUTATIONAL = "Reputational",
  LEGAL = "Legal",
  OTHER = "Other"
}

export enum ImpactType {
  DIRECT = "Direct",
  INDIRECT = "Indirect",
  CASCADING = "Cascading"
}

export enum SeverityLevel {
  LOW = "Low",
  MEDIUM = "Medium",
  HIGH = "High",
  CRITICAL = "Critical"
}

export class DamageScenarioApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DamageScenarioApiError';
  }
}
