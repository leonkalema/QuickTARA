import type { 
  ThreatScenario, 
  CreateThreatScenarioRequest, 
  UpdateThreatScenarioRequest, 
  ThreatScenarioListResponse 
} from '../types/threatScenario';

const API_BASE_URL = 'http://127.0.0.1:8080/api';

class ThreatScenarioApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ThreatScenarioApiError';
  }
}

export const threatScenarioApi = {
  async getThreatScenariosByProduct(scopeId: string): Promise<ThreatScenarioListResponse> {
    const response = await fetch(`${API_BASE_URL}/threat-scenarios?scope_id=${scopeId}`);
    if (!response.ok) {
      throw new ThreatScenarioApiError(`Failed to fetch threat scenarios: ${response.statusText}`, response.status);
    }
    return response.json();
  },

  async getThreatScenariosByDamageScenario(damageScenarioId: string): Promise<ThreatScenarioListResponse> {
    const response = await fetch(`${API_BASE_URL}/threat-scenarios?damage_scenario_id=${damageScenarioId}`);
    if (!response.ok) {
      throw new ThreatScenarioApiError(`Failed to fetch threat scenarios: ${response.statusText}`, response.status);
    }
    return response.json();
  },

  async getThreatScenario(threatScenarioId: string): Promise<ThreatScenario> {
    const response = await fetch(`${API_BASE_URL}/threat-scenarios/${threatScenarioId}`);
    if (!response.ok) {
      throw new ThreatScenarioApiError(`Failed to fetch threat scenario: ${response.statusText}`, response.status);
    }
    return response.json();
  },

  async createThreatScenario(threatScenario: CreateThreatScenarioRequest): Promise<ThreatScenario> {
    const response = await fetch(`${API_BASE_URL}/threat-scenarios`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(threatScenario),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ThreatScenarioApiError(`Failed to create threat scenario: ${errorText}`, response.status);
    }

    return response.json();
  },

  async updateThreatScenario(threatScenarioId: string, updates: UpdateThreatScenarioRequest): Promise<ThreatScenario> {
    const response = await fetch(`${API_BASE_URL}/threat-scenarios/${threatScenarioId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ThreatScenarioApiError(`Failed to update threat scenario: ${errorText}`, response.status);
    }

    return response.json();
  },

  async deleteThreatScenario(threatScenarioId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/threat-scenarios/${threatScenarioId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new ThreatScenarioApiError(`Failed to delete threat scenario: ${errorText}`, response.status);
    }
  }
};
