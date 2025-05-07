/**
 * Damage Scenarios API client
 * Handles all API calls related to damage scenario management
 */

import apiClient from './index';

/**
 * Damage category enum
 */
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

/**
 * Impact type enum
 */
export enum ImpactType {
  DIRECT = "Direct",
  INDIRECT = "Indirect",
  CASCADING = "Cascading"
}

/**
 * Severity level enum
 */
export enum SeverityLevel {
  LOW = "Low",
  MEDIUM = "Medium",
  HIGH = "High",
  CRITICAL = "Critical"
}

/**
 * Damage Scenario interface
 */
export interface DamageScenario {
  scenario_id: string;
  name: string;
  description: string;
  damage_category: DamageCategory;
  impact_type: ImpactType;
  confidentiality_impact: boolean;
  integrity_impact: boolean;
  availability_impact: boolean;
  severity: SeverityLevel;
  impact_details?: Record<string, any>;
  scope_id: string;
  primary_component_id: string;
  affected_component_ids: string[];
  version: number;
  revision_notes?: string;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Damage Scenario list response
 */
export interface DamageScenarioList {
  scenarios: DamageScenario[];
  total: number;
}

/**
 * New damage scenario data (for creation)
 */
export type DamageScenarioCreate = Omit<DamageScenario, 'scenario_id' | 'is_deleted' | 'created_at' | 'updated_at'> & {
  scenario_id?: string;
};

/**
 * Damage scenario update data
 */
export type DamageScenarioUpdate = Partial<Omit<DamageScenario, 'scenario_id' | 'is_deleted' | 'created_at' | 'updated_at'>>;

/**
 * Propagation suggestion interface
 */
export interface PropagationSuggestion {
  source_component_id: string;
  target_component_id: string;
  confidentiality_impact: boolean;
  integrity_impact: boolean;
  availability_impact: boolean;
  damage_category: DamageCategory;
  impact_type: ImpactType;
  severity: SeverityLevel;
  confidence: number;
  path: string[];
}

/**
 * Propagation suggestion response
 */
export interface PropagationSuggestionResponse {
  suggestions: PropagationSuggestion[];
  total: number;
}

/**
 * Damage Scenarios API service
 */
export const damageScenarioApi = {
  /**
   * Get all damage scenarios with optional filters
   * @param options - Filter options
   * @returns Promise with array of damage scenarios
   */
  async getAll(options?: {
    skip?: number;
    limit?: number;
    scope_id?: string;
    component_id?: string;
    damage_category?: string;
    severity?: string;
  }): Promise<DamageScenarioList> {
    try {
      // Build query parameters
      const queryParams = new URLSearchParams();
      if (options?.skip !== undefined) queryParams.append('skip', options.skip.toString());
      if (options?.limit !== undefined) queryParams.append('limit', options.limit.toString());
      if (options?.scope_id) queryParams.append('scope_id', options.scope_id);
      if (options?.component_id) queryParams.append('component_id', options.component_id);
      if (options?.damage_category) queryParams.append('damage_category', options.damage_category);
      if (options?.severity) queryParams.append('severity', options.severity);
      
      const queryString = queryParams.toString();
      const endpoint = `/damage-scenarios${queryString ? `?${queryString}` : ''}`;
      
      const response = await apiClient.get<DamageScenarioList>(endpoint);
      return response;
    } catch (error) {
      console.error('Error fetching damage scenarios:', error);
      return { scenarios: [], total: 0 };
    }
  },

  /**
   * Get a damage scenario by ID
   * @param id - Damage scenario ID
   * @returns Promise with damage scenario data
   */
  async getById(id: string): Promise<DamageScenario> {
    return apiClient.get<DamageScenario>(`/damage-scenarios/${id}`);
  },

  /**
   * Create a new damage scenario
   * @param scenario - Damage scenario data
   * @returns Promise with created damage scenario
   */
  async create(scenario: DamageScenarioCreate): Promise<DamageScenario> {
    try {
      const response = await apiClient.post<DamageScenario>('/damage-scenarios', scenario);
      return response;
    } catch (error) {
      console.error('Error creating damage scenario:', error);
      throw error;
    }
  },

  /**
   * Update an existing damage scenario
   * @param id - Damage scenario ID
   * @param scenario - Updated damage scenario data
   * @returns Promise with updated damage scenario
   */
  async update(id: string, scenario: DamageScenarioUpdate): Promise<DamageScenario> {
    return apiClient.put<DamageScenario>(`/damage-scenarios/${id}`, scenario);
  },

  /**
   * Delete a damage scenario
   * @param id - Damage scenario ID
   * @returns Promise with success response
   */
  async delete(id: string): Promise<void> {
    return apiClient.delete<void>(`/damage-scenarios/${id}`);
  },

  /**
   * Get propagation suggestions for a component
   * @param componentId - Source component ID
   * @param impacts - Impact types to consider
   * @returns Promise with propagation suggestions
   */
  async getPropagationSuggestions(
    componentId: string,
    impacts: {
      confidentiality?: boolean;
      integrity?: boolean;
      availability?: boolean;
    } = {}
  ): Promise<PropagationSuggestionResponse> {
    try {
      const queryParams = new URLSearchParams();
      queryParams.append('component_id', componentId);
      
      if (impacts.confidentiality !== undefined) {
        queryParams.append('confidentiality_impact', impacts.confidentiality.toString());
      }
      
      if (impacts.integrity !== undefined) {
        queryParams.append('integrity_impact', impacts.integrity.toString());
      }
      
      if (impacts.availability !== undefined) {
        queryParams.append('availability_impact', impacts.availability.toString());
      }
      
      const response = await apiClient.get<PropagationSuggestionResponse>(
        `/damage-scenarios/propagation/suggestions?${queryParams.toString()}`
      );
      
      return response;
    } catch (error) {
      console.error('Error fetching propagation suggestions:', error);
      return { suggestions: [], total: 0 };
    }
  }
};

export default damageScenarioApi;
