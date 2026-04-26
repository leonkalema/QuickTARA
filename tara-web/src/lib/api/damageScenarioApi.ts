import type { 
  DamageScenario, 
  CreateDamageScenarioRequest, 
  UpdateDamageScenarioRequest,
  DamageScenariosResponse
} from '../types/damageScenario';
import { apiFetch } from './apiClient';

const BASE = '/damage-scenarios';

export const damageScenarioApi = {
  getAll: (skip = 0, limit = 100): Promise<DamageScenariosResponse> =>
    apiFetch<DamageScenariosResponse>(`${BASE}?skip=${skip}&limit=${limit}`),

  getById: (id: string): Promise<DamageScenario> =>
    apiFetch<DamageScenario>(`${BASE}/${id}`),

  getDamageScenariosByProduct: (productId: string): Promise<DamageScenariosResponse> =>
    apiFetch<DamageScenariosResponse>(`${BASE}?scope_id=${productId}&limit=1000`),

  create: (damageScenario: CreateDamageScenarioRequest): Promise<DamageScenario> =>
    apiFetch<DamageScenario>(BASE, { method: 'POST', body: JSON.stringify(damageScenario) }),

  createDamageScenario: (damageScenario: CreateDamageScenarioRequest): Promise<DamageScenario> =>
    apiFetch<DamageScenario>(BASE, { method: 'POST', body: JSON.stringify(damageScenario) }),

  update: (id: string, updates: UpdateDamageScenarioRequest): Promise<DamageScenario> =>
    apiFetch<DamageScenario>(`${BASE}/${id}`, { method: 'PUT', body: JSON.stringify(updates) }),

  updateDamageScenario: (id: string, updates: UpdateDamageScenarioRequest): Promise<DamageScenario> =>
    apiFetch<DamageScenario>(`${BASE}/${id}`, { method: 'PUT', body: JSON.stringify(updates) }),

  acceptScenario: (id: string): Promise<DamageScenario> =>
    apiFetch<DamageScenario>(`${BASE}/${id}/accept`, { method: 'PATCH' }),

  delete: (id: string): Promise<void> =>
    apiFetch<void>(`${BASE}/${id}`, { method: 'DELETE' }),

  deleteDamageScenario: (id: string): Promise<void> =>
    apiFetch<void>(`${BASE}/${id}`, { method: 'DELETE' }),
};
