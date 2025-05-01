/**
 * API client for Attack Path Analysis
 */
import { apiClient } from './index';
import type { AxiosResponse } from 'axios';

// Enums
export enum AttackPathType {
  DIRECT = 'Direct',
  MULTI_STEP = 'Multi-Step',
  LATERAL = 'Lateral',
  PRIVILEGE_ESCALATION = 'Privilege Escalation'
}

export enum AttackStepType {
  INITIAL_ACCESS = 'Initial Access',
  EXECUTION = 'Execution',
  PERSISTENCE = 'Persistence',
  PRIVILEGE_ESCALATION = 'Privilege Escalation',
  DEFENSE_EVASION = 'Defense Evasion',
  CREDENTIAL_ACCESS = 'Credential Access',
  DISCOVERY = 'Discovery',
  LATERAL_MOVEMENT = 'Lateral Movement',
  COLLECTION = 'Collection',
  EXFILTRATION = 'Exfiltration',
  COMMAND_AND_CONTROL = 'Command and Control',
  IMPACT = 'Impact'
}

export enum AttackComplexity {
  LOW = 'Low',
  MEDIUM = 'Medium',
  HIGH = 'High'
}

// Interfaces
export interface ImpactScores {
  confidentiality: number;
  integrity: number;
  availability: number;
}

// Fix for AttackPathAssumption import issue
export class AttackPathAssumption {
  assumption_id: string;
  description: string;
  type: string;

  constructor(assumption_id: string, description: string, type: string) {
    this.assumption_id = assumption_id;
    this.description = description;
    this.type = type;
  }
}

// Original interface kept for reference
export interface IAttackPathAssumption {
  assumption_id: string;
  description: string;
  type: string;
}

// Fix for AttackPathConstraint import issue
export class AttackPathConstraint {
  constraint_id: string;
  description: string;
  type: string;

  constructor(constraint_id: string, description: string, type: string) {
    this.constraint_id = constraint_id;
    this.description = description;
    this.type = type;
  }
}

// Original interface kept for reference
export interface IAttackPathConstraint {
  constraint_id: string;
  description: string;
  type: string;
}

// Fix for ThreatScenario import issue
export class ThreatScenario {
  scenario_id: string;
  name: string;
  description: string;
  threat_type: string;
  likelihood: number;

  constructor(scenario_id: string, name: string, description: string, threat_type: string, likelihood: number) {
    this.scenario_id = scenario_id;
    this.name = name;
    this.description = description;
    this.threat_type = threat_type;
    this.likelihood = likelihood;
  }
}

// Original interface kept for reference
export interface IThreatScenario {
  scenario_id: string;
  name: string;
  description: string;
  threat_type: string;
  likelihood: number;
}

export interface AttackStep {
  step_id: string;
  component_id: string;
  step_type: AttackStepType;
  description: string;
  prerequisites?: string;
  vulnerability_ids?: string[];
  threat_ids?: string[];
  order: number;
  created_at: string;
}

export interface AttackPath {
  path_id: string;
  name: string;
  description: string;
  path_type: AttackPathType;
  complexity: AttackComplexity;
  entry_point_id: string;
  target_id: string;
  success_likelihood: number;
  impact: ImpactScores;
  risk_score: number;
  analysis_id: string;
  scope_id: string | null;
  created_at: string;
  updated_at: string;
  steps: AttackStep[];
}

export interface AttackPathList {
  paths: AttackPath[];
  total: number;
}

export interface AttackChainPath {
  path_id: string;
  chain_id: string;
  order: number;
}

export interface AttackChain {
  chain_id: string;
  name: string;
  description: string;
  entry_point_id: string;
  final_target_id: string;
  total_steps: number;
  complexity: AttackComplexity;
  success_likelihood: number;
  impact: ImpactScores;
  risk_score: number;
  analysis_id: string;
  scope_id: string | null;
  created_at: string;
  updated_at: string;
  paths: AttackPath[];
}

export interface AttackChainList {
  chains: AttackChain[];
  total: number;
}

export interface ComponentSummary {
  component_id: string;
  name: string;
  type: string;
  safety_level?: string;
  trust_zone?: string;
}

// Fix for AttackPathRequest import issue
export class AttackPathRequest {
  primary_component_id: string;
  component_ids: string[];
  entry_point_ids?: string[];
  target_ids?: string[];
  include_chains: boolean;
  max_depth?: number;
  assumptions?: AttackPathAssumption[];
  constraints?: AttackPathConstraint[];
  threat_scenarios?: ThreatScenario[];
  vulnerability_ids?: string[];

  constructor(args: {
    primary_component_id: string;
    component_ids: string[];
    entry_point_ids?: string[];
    target_ids?: string[];
    include_chains: boolean;
    max_depth?: number;
    assumptions?: AttackPathAssumption[];
    constraints?: AttackPathConstraint[];
    threat_scenarios?: ThreatScenario[];
    vulnerability_ids?: string[];
  }) {
    this.primary_component_id = args.primary_component_id;
    this.component_ids = args.component_ids;
    this.entry_point_ids = args.entry_point_ids;
    this.target_ids = args.target_ids;
    this.include_chains = args.include_chains;
    this.max_depth = args.max_depth;
    this.assumptions = args.assumptions;
    this.constraints = args.constraints;
    this.threat_scenarios = args.threat_scenarios;
    this.vulnerability_ids = args.vulnerability_ids;
  }
}

// Original interface kept for reference
export interface IAttackPathRequest {
  // Primary component to analyze (focal point of the analysis)
  primary_component_id: string;
  
  // Component IDs to include in the analysis
  component_ids: string[];
  
  // Entry points and targets
  entry_point_ids?: string[];
  target_ids?: string[];
  
  // Analysis parameters
  include_chains: boolean;
  max_depth?: number;
  
  // Analysis context
  assumptions?: AttackPathAssumption[];
  constraints?: AttackPathConstraint[];
  threat_scenarios?: ThreatScenario[];
  vulnerability_ids?: string[];
}

export interface AttackPathAnalysisResult {
  analysis_id: string;
  component_count: number;
  entry_points: ComponentSummary[];
  critical_targets: ComponentSummary[];
  total_paths: number;
  high_risk_paths: number;
  total_chains: number;
  high_risk_chains: number;
  created_at: string;
  scope_id: string | null;
}

/**
 * Generate attack paths based on component connections
 * 
 * @param request - The attack path analysis request parameters
 * @returns Promise with the attack path analysis result
 */
export async function generateAttackPaths(
  request: AttackPathRequest | IAttackPathRequest
): Promise<AttackPathAnalysisResult> {
  try {
    console.log('Generating attack paths with request:', request);
    
    // Validate the request has all required fields
    if (!request.primary_component_id) {
      throw new Error('Missing required field: primary_component_id');
    }
    
    if (!request.component_ids || request.component_ids.length === 0) {
      throw new Error('Missing required field: component_ids');
    }
    
    // IMPORTANT: Ensure we have target_ids
    if (!request.target_ids || request.target_ids.length === 0) {
      throw new Error('Missing required field: target_ids. The API requires at least one target component.');
    }
    
    // Ensure primary component is in the component_ids list
    if (!request.component_ids.includes(request.primary_component_id)) {
      request.component_ids.push(request.primary_component_id);
    }
    
    // Use direct fetch for most reliable results
    const url = 'http://127.0.0.1:8080/api/attack-paths';
    console.log('Making direct API call to:', url);
    console.log('Request payload:', JSON.stringify(request, null, 2));
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response from API:', errorText);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }
    
    // Check if the response has content
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const text = await response.text();
      console.log('Non-JSON response:', text);
      throw new Error('API did not return JSON. Response: ' + text);
    }
    
    const data = await response.json();
    console.log('API response data:', data);
    
    if (!data) {
      throw new Error('API returned empty response');
    }
    
    return data;
  } catch (error) {
    console.error('Error generating attack paths:', error);
    throw error;
  }
}

/**
 * Get all attack paths with optional filtering
 * 
 * @param analysisId - Optional analysis ID to filter by
 * @param skip - Number of items to skip for pagination
 * @param limit - Maximum number of items to return
 * @returns Promise with the list of attack paths and total count
 */
export async function getAttackPaths(
  analysisId?: string,
  skip: number = 0,
  limit: number = 100
): Promise<AttackPathList> {
  try {
    // Build the URL exactly like the curl command that works
    let url = 'http://127.0.0.1:8080/api/attack-paths?skip=' + skip + '&limit=' + limit;
    
    if (analysisId) {
      url += '&analysis_id=' + analysisId;
    }
    
    console.log('Fetching attack paths from: ' + url);
    
    // Use simple fetch with the exact same parameters as the curl command
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('API error: ' + response.status);
    }
    
    // Get the raw data first so we can log it
    const data = await response.json();
    console.log('Raw API response:', data);
    
    // Handle what we get from the API
    if (Array.isArray(data)) {
      // If we got an array, wrap it in the expected format
      return { paths: data, total: data.length };
    } else if (data && data.paths && Array.isArray(data.paths)) {
      // If we got the expected format, return it as is
      return data;
    } else {
      // If we can't find paths, return empty array
      console.error('Unexpected API response format:', data);
      return { paths: [], total: 0 };
    }
  } catch (error) {
    console.error('Error fetching attack paths:', error);
    return { paths: [], total: 0 };
  }
}

/**
 * Get a specific attack path by ID
 * 
 * @param pathId - The attack path ID
 * @returns Promise with the attack path details
 */
export async function getAttackPath(pathId: string): Promise<AttackPath> {
  try {
    const response = await apiClient.get<AttackPath>(
      `/attack-paths/${pathId}`
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching attack path ${pathId}:`, error);
    throw error;
  }
}

/**
 * Get all attack chains with optional filtering
 * 
 * @param analysisId - Optional analysis ID to filter by
 * @param skip - Number of items to skip for pagination
 * @param limit - Maximum number of items to return
 * @returns Promise with the list of attack chains and total count
 */
export async function getAttackChains(
  analysisId?: string,
  skip: number = 0,
  limit: number = 100
): Promise<AttackChainList> {
  try {
    // Build the URL exactly like the working endpoint
    let url = 'http://127.0.0.1:8080/api/attack-paths/chains?skip=' + skip + '&limit=' + limit;
    
    if (analysisId) {
      url += '&analysis_id=' + analysisId;
    }
    
    console.log('Fetching attack chains from: ' + url);
    
    // Use simple fetch
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('API error: ' + response.status);
    }
    
    // Get the raw data first so we can log it
    const data = await response.json();
    console.log('Raw chains API response:', data);
    
    // Handle what we get from the API
    if (Array.isArray(data)) {
      // If we got an array, wrap it in the expected format
      return { chains: data, total: data.length };
    } else if (data && data.chains && Array.isArray(data.chains)) {
      // If we got the expected format, return it as is
      return data;
    } else {
      // If we can't find chains, return empty array
      console.error('Unexpected API response format for chains:', data);
      return { chains: [], total: 0 };
    }
  } catch (error) {
    console.error('Error fetching attack chains:', error);
    return { chains: [], total: 0 };
  }
}

/**
 * Get a specific attack chain by ID
 * 
 * @param chainId - The attack chain ID
 * @returns Promise with the attack chain details
 */
export async function getAttackChain(chainId: string): Promise<AttackChain> {
  try {
    const response = await apiClient.get<AttackChain>(
      `/attack-paths/chains/${chainId}`
    );
    return response.data;
  } catch (error) {
    console.error(`Error fetching attack chain ${chainId}:`, error);
    throw error;
  }
}
