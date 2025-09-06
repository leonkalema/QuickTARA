const API_BASE_URL = 'http://localhost:8000/api';

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
  async getRiskTreatmentData(scopeId: string): Promise<RiskTreatmentResponse> {
    const response = await fetch(`${API_BASE_URL}/risk-treatment?scope_id=${scopeId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch risk treatment data: ${response.statusText}`);
    }
    return response.json();
  }

  async updateRiskTreatment(riskTreatmentId: string, treatmentData: {
    selected_treatment?: string;
    treatment_goal?: string;
    treatment_status?: string;
  }): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/risk-treatment/${riskTreatmentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(treatmentData),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update risk treatment: ${response.statusText}`);
    }
    return response.json();
  }

  async approveRiskTreatment(riskTreatmentId: string): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/risk-treatment/${riskTreatmentId}/approve`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to approve risk treatment: ${response.statusText}`);
    }
    return response.json();
  }
}

export const riskTreatmentApi = new RiskTreatmentApi();
