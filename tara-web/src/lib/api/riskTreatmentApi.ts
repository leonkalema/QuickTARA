import { apiFetch } from './apiClient';

export interface RiskTreatmentData {
  risk_treatment_id: string;
  scenario_id: string;
  name: string;
  description: string;
  primary_component_id: string;
  safety_impact?: string;
  financial_impact?: string;
  operational_impact?: string;
  privacy_impact?: string;
  confidentiality_impact?: boolean;
  integrity_impact?: boolean;
  availability_impact?: boolean;
  severity?: string;
  attack_path_id?: string;
  highest_feasibility_score?: number;
  impact_level?: string;
  feasibility_level?: string;
  risk_level?: string;
  suggested_treatment?: string;
  selected_treatment?: string;
  treatment_goal?: string;
  treatment_status?: string;
  // New fields from backend for auto-suggestion
  product_name?: string;
  asset_name?: string;
  cia?: string;
  suggested_goal?: string;
}

export interface AttackPathData {
  attack_path_id: string;
  feasibility_rating: any;
  threat_scenario_id: string;
  threat_name: string;
}

export interface RiskTreatmentResponse {
  damage_scenarios: RiskTreatmentData[];
  total_count: number;
}

export class RiskTreatmentApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RiskTreatmentApiError';
  }
}

export class RiskTreatmentApi {
  getRiskTreatmentData(scopeId: string): Promise<RiskTreatmentResponse> {
    return apiFetch<RiskTreatmentResponse>(`/risk-treatment?scope_id=${scopeId}`);
  }

  updateRiskTreatment(riskTreatmentId: string, treatmentData: {
    selected_treatment?: string;
    treatment_goal?: string;
    treatment_status?: string;
  }): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/risk-treatment/${riskTreatmentId}`, {
      method: 'PUT',
      body: JSON.stringify(treatmentData),
    });
  }

  approveRiskTreatment(riskTreatmentId: string): Promise<{ message: string }> {
    return apiFetch<{ message: string }>(`/risk-treatment/${riskTreatmentId}/approve`, {
      method: 'PUT',
    });
  }
}

export const riskTreatmentApi = new RiskTreatmentApi();
