import apiClient from './index';
import type { DamageScenario } from './damage-scenarios';

export enum SeverityLevel {
  LOW = 'Low',
  MEDIUM = 'Medium',
  HIGH = 'High',
  CRITICAL = 'Critical'
}

export interface ImpactRating {
  safety_impact: SeverityLevel | null;
  financial_impact: SeverityLevel | null;
  operational_impact: SeverityLevel | null;
  privacy_impact: SeverityLevel | null;
  impact_rating_notes: string | null;
  sfop_rating_auto_generated: boolean;
  sfop_rating_last_edited_by: string | null;
  sfop_rating_last_edited_at: string | null;
  sfop_rating_override_reason: string | null;
}

export interface ImpactRatingUpdate {
  safety_impact?: SeverityLevel;
  financial_impact?: SeverityLevel;
  operational_impact?: SeverityLevel;
  privacy_impact?: SeverityLevel;
  impact_rating_notes?: string;
  sfop_rating_override_reason?: string;
}

export interface ImpactRatingExplanation {
  safety_impact: string;
  financial_impact: string;
  operational_impact: string;
  privacy_impact: string;
}

export const impactRatingApi = {
  getScenarioRatings: async (scenarioId: string): Promise<DamageScenario> => {
    return await apiClient.get<DamageScenario>(`/impact-ratings/scenarios/${scenarioId}/impact-ratings`);
  },
  
  updateScenarioRatings: async (scenarioId: string, data: ImpactRatingUpdate): Promise<DamageScenario> => {
    return await apiClient.put<DamageScenario>(`/impact-ratings/scenarios/${scenarioId}/impact-ratings`, data);
  },
  
  getSuggestedRatings: async (params: {
    component_id: string;
    damage_category: string;
    confidentiality_impact?: boolean;
    integrity_impact?: boolean;
    availability_impact?: boolean;
  }): Promise<{
    ratings: ImpactRating;
    explanations: ImpactRatingExplanation;
  }> => {
    // Construct query string
    const queryParams = new URLSearchParams();
    queryParams.append('component_id', params.component_id);
    queryParams.append('damage_category', params.damage_category);
    
    if (params.confidentiality_impact !== undefined) {
      queryParams.append('confidentiality_impact', params.confidentiality_impact.toString());
    }
    
    if (params.integrity_impact !== undefined) {
      queryParams.append('integrity_impact', params.integrity_impact.toString());
    }
    
    if (params.availability_impact !== undefined) {
      queryParams.append('availability_impact', params.availability_impact.toString());
    }
    
    return await apiClient.get<{
      ratings: ImpactRating;
      explanations: ImpactRatingExplanation;
    }>(`/impact-ratings/suggest-ratings?${queryParams.toString()}`);
  },
  
  listRatings: async (params?: {
    skip?: number;
    limit?: number;
    scope_id?: string;
    safety_impact?: SeverityLevel;
    financial_impact?: SeverityLevel;
    operational_impact?: SeverityLevel;
    privacy_impact?: SeverityLevel;
    auto_generated_only?: boolean;
  }): Promise<DamageScenario[]> => {
    // Construct query string
    const queryParams = new URLSearchParams();
    
    if (params) {
      if (params.skip !== undefined) {
        queryParams.append('skip', params.skip.toString());
      }
      
      if (params.limit !== undefined) {
        queryParams.append('limit', params.limit.toString());
      }
      
      if (params.scope_id) {
        queryParams.append('scope_id', params.scope_id);
      }
      
      if (params.safety_impact) {
        queryParams.append('safety_impact', params.safety_impact);
      }
      
      if (params.financial_impact) {
        queryParams.append('financial_impact', params.financial_impact);
      }
      
      if (params.operational_impact) {
        queryParams.append('operational_impact', params.operational_impact);
      }
      
      if (params.privacy_impact) {
        queryParams.append('privacy_impact', params.privacy_impact);
      }
      
      if (params.auto_generated_only !== undefined) {
        queryParams.append('auto_generated_only', params.auto_generated_only.toString());
      }
    }
    
    const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return await apiClient.get<DamageScenario[]>(`/impact-ratings/list${queryString}`);
  
  }
};
