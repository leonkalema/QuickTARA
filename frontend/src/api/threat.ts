/**
 * API client for threat catalog and STRIDE analysis
 */
import { apiClient } from './index';
import type { AxiosResponse } from 'axios';

// Enums
export enum StrideCategory {
  SPOOFING = 'spoofing',
  TAMPERING = 'tampering',
  REPUDIATION = 'repudiation',
  INFO_DISCLOSURE = 'info_disclosure',
  DENIAL_OF_SERVICE = 'denial_of_service',
  ELEVATION = 'elevation_of_privilege'
}

export enum ComponentType {
  SENSOR = 'sensor',
  ACTUATOR = 'actuator',
  CONTROLLER = 'controller',
  GATEWAY = 'gateway',
  PROCESSING_UNIT = 'processing_unit',
  STORAGE = 'storage',
  COMMUNICATION = 'communication',
  INTERFACE = 'interface',
  HMI = 'hmi',
  EXTERNAL_SERVICE = 'external_service',
  OTHER = 'other'
}

export enum TrustZone {
  SECURE = 'secure',
  TRUSTED = 'trusted',
  UNTRUSTED = 'untrusted',
  EXTERNAL = 'external',
  UNKNOWN = 'unknown'
}

export enum AttackVector {
  PHYSICAL = 'physical',
  LOCAL_NETWORK = 'local_network',
  ADJACENT_NETWORK = 'adjacent_network',
  NETWORK = 'network',
  BLUETOOTH = 'bluetooth',
  WIFI = 'wifi',
  CAN_BUS = 'can_bus',
  USB = 'usb',
  SUPPLY_CHAIN = 'supply_chain',
  SOCIAL_ENGINEERING = 'social_engineering',
  OTHER = 'other'
}

// Interfaces
export interface MitigationStrategy {
  title: string;
  description: string;
  effectiveness: number;
  implementation_complexity: number;
  references: string[];
}

export interface ThreatCatalogItem {
  id: string;
  title: string;
  description: string;
  stride_category: StrideCategory;
  applicable_component_types: ComponentType[];
  applicable_trust_zones: TrustZone[];
  attack_vectors: AttackVector[];
  prerequisites: string[];
  typical_likelihood: number;
  typical_severity: number;
  mitigation_strategies: MitigationStrategy[];
  cwe_ids: string[];
  capec_ids: string[];
  examples: string[];
  created_at: string;
  updated_at: string;
}

export interface ThreatCatalogCreate {
  title: string;
  description: string;
  stride_category: StrideCategory;
  applicable_component_types: ComponentType[];
  applicable_trust_zones: TrustZone[];
  attack_vectors: AttackVector[];
  prerequisites: string[];
  typical_likelihood: number;
  typical_severity: number;
  mitigation_strategies: MitigationStrategy[];
  cwe_ids: string[];
  capec_ids: string[];
  examples: string[];
}

export interface ThreatCatalogUpdate {
  title?: string;
  description?: string;
  stride_category?: StrideCategory;
  applicable_component_types?: ComponentType[];
  applicable_trust_zones?: TrustZone[];
  attack_vectors?: AttackVector[];
  prerequisites?: string[];
  typical_likelihood?: number;
  typical_severity?: number;
  mitigation_strategies?: MitigationStrategy[];
  cwe_ids?: string[];
  capec_ids?: string[];
  examples?: string[];
}

export interface ThreatCatalogList {
  catalog_items: ThreatCatalogItem[];
  total: number;
}

export interface ThreatMatchResult {
  threat_id: string;
  component_id: string;
  title: string;
  stride_category: StrideCategory;
  match_confidence: number;
  calculated_likelihood: number;
  calculated_severity: number;
  calculated_risk_score: number;
  applicable_mitigation_strategies: MitigationStrategy[];
  notes?: string;
}

export interface ComponentThreatAnalysis {
  component_id: string;
  component_name: string;
  component_type: string;
  total_threats_identified: number;
  high_risk_threats: number;
  medium_risk_threats: number;
  low_risk_threats: number;
  threat_matches: ThreatMatchResult[];
  stride_summary: Record<string, number>;
}

export interface ThreatAnalysisRequest {
  component_ids: string[];
  custom_threats?: ThreatCatalogItem[];
  risk_framework_id?: string;
}

export interface ThreatAnalysisResponse {
  analysis_id: string;
  component_analyses: ComponentThreatAnalysis[];
  total_components: number;
  total_threats: number;
  high_risk_threats: number;
  stride_summary: Record<string, number>;
  timestamp: string;
}

export interface ComponentThreatProfile {
  component_id: string;
  threat_id: string;
  title: string;
  description: string;
  stride_category: StrideCategory;
  likelihood: number;
  severity: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  mitigation_strategies: MitigationStrategy[];
}

export interface ThreatAnalysisResult {
  analysis_id: string;
  component_threat_profiles: ComponentThreatProfile[];
  total_components: number;
  total_threats: number;
  high_risk_threats: number;
  medium_risk_threats: number;
  low_risk_threats: number;
  risk_framework_id: string;
  risk_framework_name: string;
  timestamp: string;
}

/**
 * Get all threat catalog items
 */
export async function getThreatCatalogItems(
  skip: number = 0,
  limit: number = 100,
  strideCategory?: StrideCategory,
  componentType?: ComponentType,
  trustZone?: TrustZone
): Promise<ThreatCatalogList> {
  let params: Record<string, any> = { skip, limit };
  
  if (strideCategory) {
    params.stride_category = strideCategory;
  }
  
  if (componentType) {
    params.component_type = componentType;
  }
  
  if (trustZone) {
    params.trust_zone = trustZone;
  }
  
  const response: AxiosResponse<ThreatCatalogList> = await apiClient.get('/threat/catalog', { params });
  return response.data;
}

/**
 * Get a threat catalog item by ID
 */
export async function getThreatCatalogItem(id: string): Promise<ThreatCatalogItem> {
  const response: AxiosResponse<ThreatCatalogItem> = await apiClient.get(`/threat/catalog/${id}`);
  return response.data;
}

/**
 * Create a new threat catalog item
 */
export async function createThreatCatalogItem(threat: ThreatCatalogCreate): Promise<ThreatCatalogItem> {
  const response: AxiosResponse<ThreatCatalogItem> = await apiClient.post('/threat/catalog', threat);
  return response.data;
}

/**
 * Update an existing threat catalog item
 */
export async function updateThreatCatalogItem(
  id: string,
  threatUpdate: ThreatCatalogUpdate
): Promise<ThreatCatalogItem> {
  const response: AxiosResponse<ThreatCatalogItem> = await apiClient.put(`/threat/catalog/${id}`, threatUpdate);
  return response.data;
}

/**
 * Delete a threat catalog item
 */
export async function deleteThreatCatalogItem(id: string): Promise<void> {
  await apiClient.delete(`/threat/catalog/${id}`);
}

/**
 * Perform threat analysis on components
 */
export async function performThreatAnalysis(
  componentIds: string[] | ThreatAnalysisRequest
): Promise<ThreatAnalysisResult> {
  let request: ThreatAnalysisRequest;
  
  if (Array.isArray(componentIds)) {
    request = { component_ids: componentIds };
  } else {
    request = componentIds;
  }
  
  const response: AxiosResponse<ThreatAnalysisResult> = await apiClient.post('/threat/analyze', request);
  return response.data;
}
