/**
 * System Scope API client
 */
import apiClient from './index';

/**
 * System type enumeration
 */
export enum SystemType {
  SUBSYSTEM = 'subsystem',
  API = 'api',
  BACKEND = 'backend',
  FULLSYSTEM = 'fullsystem',
  EMBEDDED = 'embedded',
  OTHER = 'other'
}

/**
 * SystemScope interface
 */
export interface SystemScope {
  scope_id: string;
  name: string;
  system_type: SystemType;
  description?: string;
  boundaries?: string[];
  objectives?: string[];
  stakeholders?: string[];
  created_at: string;
  updated_at: string;
}

/**
 * SystemScopeCreate interface - for creating new scopes
 */
export interface SystemScopeCreate {
  name: string;
  system_type: SystemType;
  description?: string;
  boundaries?: string[];
  objectives?: string[];
  stakeholders?: string[];
  scope_id?: string;
}

/**
 * SystemScopeUpdate interface - for updating existing scopes
 */
export interface SystemScopeUpdate {
  name?: string;
  system_type?: SystemType;
  description?: string;
  boundaries?: string[];
  objectives?: string[];
  stakeholders?: string[];
}

/**
 * SystemScopeList interface - for listing scopes
 */
export interface SystemScopeList {
  scopes: SystemScope[];
  total: number;
}

/**
 * System Scope API methods
 */
export const scopeApi = {
  /**
   * Get a list of all system scopes
   */
  async getAll(skip = 0, limit = 100): Promise<SystemScopeList> {
    try {
      const queryParams = `?skip=${skip}&limit=${limit}`;
      return await apiClient.get(`/scope${queryParams}`);
    } catch (error) {
      console.error('Error fetching scopes:', error);
      throw error;
    }
  },

  /**
   * Get a specific system scope by ID
   */
  async getById(scopeId: string): Promise<SystemScope> {
    try {
      return await apiClient.get(`/scope/${scopeId}`);
    } catch (error) {
      console.error(`Error fetching scope ${scopeId}:`, error);
      throw error;
    }
  },

  /**
   * Create a new system scope
   */
  async create(scope: SystemScopeCreate): Promise<SystemScope> {
    try {
      return await apiClient.post('/scope', scope);
    } catch (error) {
      console.error('Error creating scope:', error);
      throw error;
    }
  },

  /**
   * Update an existing system scope
   */
  async update(scopeId: string, scope: SystemScopeUpdate): Promise<SystemScope> {
    try {
      return await apiClient.put(`/scope/${scopeId}`, scope);
    } catch (error) {
      console.error(`Error updating scope ${scopeId}:`, error);
      throw error;
    }
  },

  /**
   * Delete a system scope
   */
  async delete(scopeId: string): Promise<void> {
    try {
      return await apiClient.delete(`/scope/${scopeId}`);
    } catch (error) {
      console.error(`Error deleting scope ${scopeId}:`, error);
      throw error;
    }
  }
};

export default scopeApi;
