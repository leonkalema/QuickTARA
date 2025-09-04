import type { 
  DamageScenario, 
  CreateDamageScenarioRequest, 
  UpdateDamageScenarioRequest,
  DamageScenariosResponse
} from '../types/damageScenario';
import { DamageScenarioApiError } from '../types/damageScenario';

const API_BASE_URL = 'http://127.0.0.1:8080/api';

class DamageScenarioApi {
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorText = await response.text();
      throw new DamageScenarioApiError(`API Error: ${response.status} - ${errorText}`);
    }
    return response.json();
  }

  // Damage Scenarios
  async getAll(skip = 0, limit = 100): Promise<DamageScenariosResponse> {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios?skip=${skip}&limit=${limit}`);
    return this.handleResponse<DamageScenariosResponse>(response);
  }

  async getById(id: string): Promise<DamageScenario> {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios/${id}`);
    return this.handleResponse<DamageScenario>(response);
  }

  async getDamageScenariosByProduct(productId: string): Promise<DamageScenariosResponse> {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios?scope_id=${productId}`);
    if (!response.ok) {
      throw new DamageScenarioApiError(`Failed to fetch damage scenarios: ${response.statusText}`);
    }
    return response.json();
  }

  async updateDamageScenario(scenarioId: string, updateData: UpdateDamageScenarioRequest): Promise<DamageScenario> {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios/${scenarioId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateData),
    });
    
    if (!response.ok) {
      throw new DamageScenarioApiError(`Failed to update damage scenario: ${response.statusText}`);
    }
    
    return response.json();
  }

  async deleteDamageScenario(scenarioId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios/${scenarioId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new DamageScenarioApiError(`Failed to delete damage scenario: ${response.statusText}`);
    }
  }

  async create(damageScenario: CreateDamageScenarioRequest): Promise<DamageScenario> {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(damageScenario),
    });
    return this.handleResponse<DamageScenario>(response);
  }

  async createDamageScenario(damageScenario: CreateDamageScenarioRequest): Promise<DamageScenario> {
    return this.create(damageScenario);
  }

  async update(id: string, updates: UpdateDamageScenarioRequest): Promise<DamageScenario> {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    return this.handleResponse<DamageScenario>(response);
  }

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/damage-scenarios/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const errorText = await response.text();
      throw new DamageScenarioApiError(`API Error: ${response.status} - ${errorText}`);
    }
  }
}

export const damageScenarioApi = new DamageScenarioApi();
