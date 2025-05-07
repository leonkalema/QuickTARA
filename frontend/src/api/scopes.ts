/**
 * Scopes API client
 * Handles all API calls related to scope management
 */

import apiClient from './index';

/**
 * Scope interface
 */
export interface Scope {
  scope_id: string;
  name: string;
  description: string;
  version: string;
  status: string;
  created_at: string;
  updated_at: string;
}

/**
 * Scope list response
 */
export interface ScopeList {
  scopes: Scope[];
  total: number;
}

/**
 * New scope data (for creation)
 */
export type ScopeCreate = Omit<Scope, 'scope_id' | 'created_at' | 'updated_at'>;

/**
 * Scope update data
 */
export type ScopeUpdate = Partial<Omit<Scope, 'scope_id' | 'created_at' | 'updated_at'>>;

/**
 * Scopes API service
 */
export const scopeApi = {
  /**
   * Get all scopes
   * @param options - Filter options
   * @returns Promise with array of scopes
   */
  async getAll(options?: {
    skip?: number;
    limit?: number;
    status?: string;
  }): Promise<ScopeList> {
    try {
      // Build query parameters
      const queryParams = new URLSearchParams();
      if (options?.skip !== undefined) queryParams.append('skip', options.skip.toString());
      if (options?.limit !== undefined) queryParams.append('limit', options.limit.toString());
      if (options?.status) queryParams.append('status', options.status);
      
      const queryString = queryParams.toString();
      const endpoint = `/scope${queryString ? `?${queryString}` : ''}`;
      
      const response = await apiClient.get<ScopeList>(endpoint);
      return response;
    } catch (error) {
      console.error('Error fetching scopes:', error);
      return { scopes: [], total: 0 };
    }
  },

  /**
   * Get a scope by ID
   * @param id - Scope ID
   * @returns Promise with scope data
   */
  async getById(id: string): Promise<Scope> {
    return apiClient.get<Scope>(`/scope/${id}`);
  },

  /**
   * Create a new scope
   * @param scope - Scope data
   * @returns Promise with created scope
   */
  async create(scope: ScopeCreate): Promise<Scope> {
    try {
      const response = await apiClient.post<Scope>('/scope', scope);
      return response;
    } catch (error) {
      console.error('Error creating scope:', error);
      throw error;
    }
  },

  /**
   * Update an existing scope
   * @param id - Scope ID
   * @param scope - Updated scope data
   * @returns Promise with updated scope
   */
  async update(id: string, scope: ScopeUpdate): Promise<Scope> {
    try {
      const response = await apiClient.put<Scope>(`/scope/${id}`, scope);
      return response;
    } catch (error) {
      console.error('Error updating scope:', error);
      throw error;
    }
  },

  /**
   * Delete a scope
   * @param id - Scope ID
   * @returns Promise with success response
   */
  async delete(id: string): Promise<void> {
    try {
      await apiClient.delete(`/scope/${id}`);
    } catch (error) {
      console.error('Error deleting scope:', error);
    }
  },

  /**
   * Get components for a scope
   * @param scopeId - Scope ID
   * @returns Promise with array of components
   */
  async getComponents(scopeId: string): Promise<any[]> {
    try {
      const response = await apiClient.get<{components: any[], total: number}>(`/scope/${scopeId}/components`);
      if (response && response.components) {
        return response.components;
      }
      return [];
    } catch (error) {
      console.error(`Error fetching components for scope ${scopeId}:`, error);
      return [];
    }
  }
};

export default scopeApi;
