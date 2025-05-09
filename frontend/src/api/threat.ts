/**
 * API client for threat catalog and STRIDE analysis
 */
import { apiClient } from './index';

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
  const qs = new URLSearchParams();
  qs.append('skip', String(skip));
  qs.append('limit', String(limit));
  if (strideCategory) qs.append('stride_category', strideCategory);
  if (componentType) qs.append('component_type', componentType);
  if (trustZone) qs.append('trust_zone', trustZone);

  return await apiClient.get<ThreatCatalogList>(`/threat/catalog?${qs.toString()}`);
}

/**
 * Get a threat catalog item by ID
 */
export async function getThreatCatalogItem(id: string): Promise<ThreatCatalogItem> {
  return await apiClient.get<ThreatCatalogItem>(`/threat/catalog/${id}`);
}

/**
 * Create a new threat catalog item
 */
export async function createThreatCatalogItem(threat: ThreatCatalogCreate): Promise<ThreatCatalogItem> {
  return await apiClient.post<ThreatCatalogItem>('/threat/catalog', threat);
}

/**
 * Bulk create new threat catalog items
 */
export async function bulkCreateThreatCatalogItems(
  threats: ThreatCatalogCreate[]
): Promise<ThreatCatalogItem[]> {
  const res = await apiClient.post<{ inserted: number; catalog_items: ThreatCatalogItem[] }>('/threat/catalog/bulk', threats);
  return res.catalog_items;
}

/**
 * Update an existing threat catalog item
 */
export async function updateThreatCatalogItem(
  id: string,
  threatUpdate: ThreatCatalogUpdate
): Promise<ThreatCatalogItem> {
  return await apiClient.put<ThreatCatalogItem>(`/threat/catalog/${id}`, threatUpdate);
}

/**
 * Delete a threat catalog item
 */
export async function deleteThreatCatalogItem(id: string): Promise<void> {
  await apiClient.delete(`/threat/catalog/${id}`);
}

/**
 * Performs a threat analysis on the selected components
 * 
 * This function sends the selected component IDs to the threat analysis API endpoint
 * and returns the threat analysis results. The analysis identifies potential threats
 * for each component based on its type, trust zone, and other properties using the
 * STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure,
 * Denial of Service, Elevation of Privilege).
 * 
 * @param {string[]} componentIds - Array of component IDs to analyze
 * @param {ThreatCatalogItem[]} [options.customThreats] - Optional array of custom threats to include in the analysis
 * @param {string} [options.riskFrameworkId] - Optional risk framework ID to use for the analysis
 * @returns {Promise<ThreatAnalysisResult>} The threat analysis results containing threats mapped to components
 * 
 * @example
 * // Analyze threats for specific components
 * const analysisResult = await performThreatAnalysis(['COMP001', 'COMP002']);
 * 
 * // Handle the results
 * console.log(`Found ${analysisResult.total_threats} threats`);
 */
export async function performThreatAnalysis(
  componentIds: string[],
  options?: {
    customThreats?: ThreatCatalogItem[];
    riskFrameworkId?: string;
  }
): Promise<ThreatAnalysisResult> {
  try {
    // Simple request body with just component IDs
    const requestBody = {
      component_ids: componentIds,
      // Adding optional fields only if explicitly provided
      ...(options?.customThreats?.length ? { custom_threats: options.customThreats } : {}),
      ...(options?.riskFrameworkId ? { risk_framework_id: options.riskFrameworkId } : {})
    };

    console.log('Sending threat analysis request:', requestBody);
    const response: ThreatAnalysisResult = await apiClient.post('/threat/analyze', requestBody);
    console.log('Threat analysis response:', response);
    return response;
  } catch (error) {
    console.error('Error in threat analysis:', error);
    throw error; // Re-throw to allow handling in component
  }
}
