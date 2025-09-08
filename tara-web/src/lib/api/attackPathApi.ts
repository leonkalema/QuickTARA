import type { AttackPath, CreateAttackPathRequest, AttackPathResponse } from '../types/attackPath';
import { API_BASE_URL } from '$lib/config';

export const attackPathApi = {
  async getByThreatScenario(threatScenarioId: string): Promise<AttackPathResponse> {
    const response = await fetch(`${API_BASE_URL}/attack-paths-analysis?threat_scenario_id=${threatScenarioId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch attack paths: ${response.statusText}`);
    }
    return response.json();
  },

  async getByProduct(productId: string): Promise<AttackPathResponse> {
    const response = await fetch(`${API_BASE_URL}/attack-paths/product/${productId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch attack paths: ${response.statusText}`);
    }
    return response.json();
  },

  async create(attackPath: CreateAttackPathRequest): Promise<AttackPath> {
    const response = await fetch(`${API_BASE_URL}/attack-paths`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(attackPath),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to create attack path: ${response.statusText}`);
    }
    
    return response.json();
  },

  async update(attackPathId: string, attackPath: Partial<CreateAttackPathRequest>): Promise<AttackPath> {
    const response = await fetch(`${API_BASE_URL}/attack-paths/${attackPathId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(attackPath),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to update attack path: ${response.statusText}`);
    }
    
    return response.json();
  },

  async delete(attackPathId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/attack-paths/${attackPathId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete attack path: ${response.statusText}`);
    }
  }
};
