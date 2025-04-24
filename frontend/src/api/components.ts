/**
 * Component API client
 * Handles all API calls related to component management
 */

import apiClient from './index';

/**
 * Component interface
 */
export interface Component {
  component_id: string;
  name: string;
  type: string;
  safety_level: string;
  interfaces: string[];
  access_points: string[];
  data_types: string[];
  location: string;
  trust_zone: string;
  connected_to: string[];
}

/**
 * New component data (for creation)
 */
export type ComponentCreate = Component;

/**
 * Component update data
 * component_id cannot be changed, so it's omitted
 */
export type ComponentUpdate = Omit<Component, 'component_id'>;

/**
 * Component API service
 */
export const componentApi = {
  /**
   * Get all components
   * @returns Promise with array of components
   */
  async getAll(): Promise<Component[]> {
    return apiClient.get<Component[]>('/components');
  },

  /**
   * Get a component by ID
   * @param id - Component ID
   * @returns Promise with component data
   */
  async getById(id: string): Promise<Component> {
    return apiClient.get<Component>(`/components/${id}`);
  },

  /**
   * Create a new component
   * @param component - Component data
   * @returns Promise with created component
   */
  async create(component: ComponentCreate): Promise<Component> {
    return apiClient.post<Component>('/components', component);
  },

  /**
   * Update an existing component
   * @param id - Component ID
   * @param component - Updated component data
   * @returns Promise with updated component
   */
  async update(id: string, component: ComponentUpdate): Promise<Component> {
    return apiClient.put<Component>(`/components/${id}`, component);
  },

  /**
   * Delete a component
   * @param id - Component ID
   * @returns Promise with success response
   */
  async delete(id: string): Promise<void> {
    return apiClient.delete<void>(`/components/${id}`);
  },

  /**
   * Import components from CSV file
   * @param file - CSV file
   * @returns Promise with array of imported components
   */
  async importFromCsv(file: File): Promise<Component[]> {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.uploadForm<Component[]>('/components/import', formData);
  },

  /**
   * Export components to CSV
   * This will trigger a file download, so we return the URL rather than
   * processing the response directly
   * @returns URL for downloading the CSV
   */
  getExportUrl(): string {
    return `${apiClient.API_BASE_URL}/components/export`;
  },

  /**
   * Get components by search criteria
   * @param searchTerm - Search term to match against component properties
   * @returns Promise with array of matching components
   */
  async search(searchTerm: string): Promise<Component[]> {
    return apiClient.get<Component[]>(`/components/search?term=${encodeURIComponent(searchTerm)}`);
  },

  /**
   * Get components by type
   * @param type - Component type to filter by
   * @returns Promise with array of matching components
   */
  async getByType(type: string): Promise<Component[]> {
    return apiClient.get<Component[]>(`/components?type=${encodeURIComponent(type)}`);
  },

  /**
   * Get components by safety level
   * @param safetyLevel - Safety level to filter by
   * @returns Promise with array of matching components
   */
  async getBySafetyLevel(safetyLevel: string): Promise<Component[]> {
    return apiClient.get<Component[]>(`/components?safety_level=${encodeURIComponent(safetyLevel)}`);
  },

  /**
   * Get components by trust zone
   * @param trustZone - Trust zone to filter by
   * @returns Promise with array of matching components
   */
  async getByTrustZone(trustZone: string): Promise<Component[]> {
    return apiClient.get<Component[]>(`/components?trust_zone=${encodeURIComponent(trustZone)}`);
  }
};

export default componentApi;
