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
 */
export async function getComponents(): Promise<Component[]> {
  const response: AxiosResponse<Component[]> = await apiClient.get('/components');
  return response.data;
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
