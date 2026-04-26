import type { 
  ThreatScenario, 
  CreateThreatScenarioRequest, 
  UpdateThreatScenarioRequest, 
  ThreatScenarioListResponse 
} from '../types/threatScenario';
import { apiFetch } from './apiClient';

const BASE = '/threat-scenarios';

export const threatScenarioApi = {
  getThreatScenariosByProduct: (scopeId: string): Promise<ThreatScenarioListResponse> =>
    apiFetch<ThreatScenarioListResponse>(`${BASE}?scope_id=${scopeId}&limit=1000`),

  getThreatScenariosByDamageScenario: (damageScenarioId: string): Promise<ThreatScenarioListResponse> =>
    apiFetch<ThreatScenarioListResponse>(`${BASE}?damage_scenario_id=${damageScenarioId}`),

  getThreatScenario: (id: string): Promise<ThreatScenario> =>
    apiFetch<ThreatScenario>(`${BASE}/${id}`),

  createThreatScenario: (threatScenario: CreateThreatScenarioRequest): Promise<ThreatScenario> =>
    apiFetch<ThreatScenario>(BASE, { method: 'POST', body: JSON.stringify(threatScenario) }),

  updateThreatScenario: (id: string, updates: UpdateThreatScenarioRequest): Promise<ThreatScenario> =>
    apiFetch<ThreatScenario>(`${BASE}/${id}`, { method: 'PUT', body: JSON.stringify(updates) }),

  deleteThreatScenario: (id: string): Promise<void> =>
    apiFetch<void>(`${BASE}/${id}`, { method: 'DELETE' }),

  acceptScenario: (id: string): Promise<ThreatScenario> =>
    apiFetch<ThreatScenario>(`${BASE}/${id}/accept`, { method: 'PATCH' }),

  async getLinkedDamageScenarios(id: string): Promise<string[]> {
    const data = await apiFetch<{ damage_scenario_ids?: string[] }>(`${BASE}/${id}/damage-scenarios`);
    return data.damage_scenario_ids ?? [];
  },
};
