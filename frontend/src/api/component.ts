/**
 * API client for components
 */
import { apiClient } from './index';
import type { AxiosResponse } from 'axios';

// Component interfaces
export interface Component {
  id: string;
  name: string;
  description: string;
  component_type: string;
  trust_zone: string;
  safety_level: string;
  interfaces: ComponentInterface[];
  dependencies: ComponentDependency[];
  created_at: string;
  updated_at: string;
}

export interface ComponentInterface {
  id: string;
  name: string;
  description: string;
  interface_type: string;
  direction: 'in' | 'out' | 'bidirectional';
  data_format?: string;
  protocols?: string[];
}

export interface ComponentDependency {
  id: string;
  target_component_id: string;
  dependency_type: string;
  description: string;
}

export interface ComponentCreateRequest {
  name: string;
  description: string;
  component_type: string;
  trust_zone: string;
  safety_level: string;
  interfaces?: ComponentInterface[];
  dependencies?: ComponentDependency[];
}

export interface ComponentUpdateRequest {
  name?: string;
  description?: string;
  component_type?: string;
  trust_zone?: string;
  safety_level?: string;
  interfaces?: ComponentInterface[];
  dependencies?: ComponentDependency[];
}

/**
 * Get all components
 * @param skip - Number of records to skip for pagination
 * @param limit - Maximum number of records to return
 */
export async function getComponents(skip: number = 0, limit: number = 100): Promise<any> {
  try {
    // Use the exact API path from the curl example
    const url = `http://127.0.0.1:8080/api/components?skip=${skip}&limit=${limit}`;
    console.log('Fetching components from:', url);
    
    // Make a direct fetch call to the API
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Component API raw response:', data);
    
    // Handle the response format from your API
    let components = [];
    if (data && data.components && Array.isArray(data.components)) {
      components = data.components;
    } else if (Array.isArray(data)) {
      components = data;
    }
    
    // Map the components to ensure they have component_id property
    // This fixes the issue with the AttackPathForm.svelte component
    const mappedComponents = components.map(comp => ({
      ...comp,
      component_id: comp.component_id || comp.id // Use component_id if exists, otherwise use id
    }));
    
    console.log('Mapped components for UI:', mappedComponents);
    
    return {
      components: mappedComponents,
      total: mappedComponents.length
    };
  } catch (error) {
    console.error('Error fetching components:', error);
    return { components: [], total: 0 }; // Return empty array on error
  }
}

/**
 * Get a component by ID
 */
export async function getComponent(id: string): Promise<Component> {
  const response: AxiosResponse<Component> = await apiClient.get(`/components/${id}`);
  return response.data;
}

/**
 * Create a new component
 */
export async function createComponent(component: ComponentCreateRequest): Promise<Component> {
  const response: AxiosResponse<Component> = await apiClient.post('/components', component);
  return response.data;
}

/**
 * Update an existing component
 */
export async function updateComponent(id: string, update: ComponentUpdateRequest): Promise<Component> {
  const response: AxiosResponse<Component> = await apiClient.put(`/components/${id}`, update);
  return response.data;
}

/**
 * Delete a component
 */
export async function deleteComponent(id: string): Promise<void> {
  await apiClient.delete(`/components/${id}`);
}
