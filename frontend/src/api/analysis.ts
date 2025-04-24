/**
 * Analysis API client
 * Handles all API calls related to threat and risk analysis
 */

import apiClient from './index';
import type { Component } from './components';

/**
 * Analysis creation request
 */
export interface AnalysisCreate {
  component_ids: string[];
  name: string;
  description?: string;
}

/**
 * Analysis metadata
 */
export interface Analysis {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  status: AnalysisStatus;
  component_ids: string[];
}

/**
 * Analysis status enum
 */
export enum AnalysisStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

/**
 * Stride Category enum
 */
export enum StrideCategory {
  SPOOFING = 'spoofing',
  TAMPERING = 'tampering',
  REPUDIATION = 'repudiation',
  INFO_DISCLOSURE = 'info_disclosure',
  DENIAL_OF_SERVICE = 'denial_of_service',
  ELEVATION = 'elevation_of_privilege'
}

/**
 * Impact category types
 */
export interface ImpactScores {
  financial: number;
  safety: number;
  privacy: number;
}

/**
 * STRIDE analysis result for a component
 */
export interface StrideAnalysisResult {
  category: StrideCategory;
  risk_level: 'High' | 'Medium' | 'Low';
  recommendations: string[];
}

/**
 * Risk factors for a component
 */
export interface RiskFactors {
  exposure: number;
  complexity: number;
  attack_surface: number;
}

/**
 * Threat information
 */
export interface Threat {
  name: string;
  id: string;
  description: string;
  impact: ImpactScores;
  likelihood: number;
  mitigations: string;
  risk_factors: RiskFactors;
}

/**
 * Attack path information
 */
export interface AttackPath {
  path: string[];
  risk: ImpactScores;
}

/**
 * Compliance requirement
 */
export interface ComplianceRequirement {
  standard: string;
  requirement: string;
  description: string;
}

/**
 * Attacker profile relevance
 */
export interface AttackerProfiles {
  Hobbyist: number;
  Criminal: number;
  Hacktivist: number;
  Insider: number;
  'Advanced Persistent Threat': number;
}

/**
 * Feasibility assessment
 */
export interface FeasibilityAssessment {
  feasibility: {
    technical_capability: number;
    knowledge_required: number;
    resources_needed: number;
    time_required: number;
    overall_score: number;
    feasibility_level: string;
  };
  profiles: AttackerProfiles;
  mitigating_factors: string[];
  enabling_factors: string[];
}

/**
 * Risk acceptance decision
 */
export interface RiskAcceptance {
  risk_severity: string;
  decision: string;
  criteria: {
    max_severity: string;
    required_controls: number;
    stakeholder_approval: string[];
    residual_risk_threshold: number;
    reassessment_period: number;
    conditional_factors: string[];
  };
  justification: string;
  conditions: string[];
  residual_risk: number;
  approvers: string[];
}

/**
 * Component analysis result
 */
export interface ComponentAnalysisResult {
  name: string;
  type: string;
  safety_level: string;
  interfaces: string[];
  access_points: string[];
  data_types: string[];
  location: string;
  trust_zone: string;
  connected_to: string[];
  threats: Threat[];
  stride_analysis: Record<string, StrideAnalysisResult>;
  compliance: ComplianceRequirement[];
  attack_paths?: AttackPath[];
  feasibility_assessments: Record<string, FeasibilityAssessment>;
  risk_acceptance: Record<string, RiskAcceptance>;
  cybersecurity_goals: Record<string, any>; // Complex structure, simplified for now
}

/**
 * Complete analysis results
 */
export interface AnalysisResult {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  status: AnalysisStatus;
  components: Record<string, ComponentAnalysisResult>;
  summary: {
    total_components: number;
    total_threats: number;
    critical_components: number;
    high_risk_threats: number;
  };
}

/**
 * Analysis API service
 */
export const analysisApi = {
  /**
   * Run analysis on components
   * @param analysisData - Analysis request data
   * @returns Promise with analysis metadata
   */
  async runAnalysis(analysisData: AnalysisCreate): Promise<Analysis> {
    return apiClient.post<Analysis>('/analysis', analysisData);
  },

  /**
   * Get all analyses
   * @returns Promise with array of analyses
   */
  async getAll(): Promise<Analysis[]> {
    return apiClient.get<Analysis[]>('/analysis');
  },

  /**
   * Get analysis by ID
   * @param id - Analysis ID
   * @returns Promise with analysis data
   */
  async getById(id: string): Promise<Analysis> {
    return apiClient.get<Analysis>(`/analysis/${id}`);
  },

  /**
   * Get analysis results by ID
   * @param id - Analysis ID
   * @returns Promise with analysis results
   */
  async getResults(id: string): Promise<AnalysisResult> {
    return apiClient.get<AnalysisResult>(`/analysis/${id}/results`);
  },

  /**
   * Get STRIDE analysis for a specific analysis
   * @param id - Analysis ID
   * @returns Promise with STRIDE analysis results
   */
  async getStrideAnalysis(id: string): Promise<Record<string, Record<string, StrideAnalysisResult>>> {
    return apiClient.get<Record<string, Record<string, StrideAnalysisResult>>>(`/analysis/${id}/stride`);
  },

  /**
   * Get compliance mappings for a specific analysis
   * @param id - Analysis ID
   * @returns Promise with compliance requirements
   */
  async getCompliance(id: string): Promise<Record<string, ComplianceRequirement[]>> {
    return apiClient.get<Record<string, ComplianceRequirement[]>>(`/analysis/${id}/compliance`);
  },

  /**
   * Get attack paths for a specific analysis
   * @param id - Analysis ID
   * @returns Promise with attack paths
   */
  async getAttackPaths(id: string): Promise<Record<string, AttackPath[]>> {
    return apiClient.get<Record<string, AttackPath[]>>(`/analysis/${id}/attack-paths`);
  },

  /**
   * Cancel a running analysis
   * @param id - Analysis ID
   * @returns Promise with updated analysis
   */
  async cancelAnalysis(id: string): Promise<Analysis> {
    return apiClient.post<Analysis>(`/analysis/${id}/cancel`);
  },

  /**
   * Delete an analysis
   * @param id - Analysis ID
   * @returns Promise with success response
   */
  async deleteAnalysis(id: string): Promise<void> {
    return apiClient.delete<void>(`/analysis/${id}`);
  },

  /**
   * Get analysis status
   * @param id - Analysis ID
   * @returns Promise with analysis status
   */
  async getStatus(id: string): Promise<{ status: AnalysisStatus; progress?: number }> {
    return apiClient.get<{ status: AnalysisStatus; progress?: number }>(`/analysis/${id}/status`);
  },

  /**
   * Get attacker feasibility assessments for a specific analysis
   * @param id - Analysis ID
   * @returns Promise with feasibility assessments
   */
  async getFeasibilityAssessments(id: string): Promise<Record<string, Record<string, FeasibilityAssessment>>> {
    return apiClient.get<Record<string, Record<string, FeasibilityAssessment>>>(`/analysis/${id}/feasibility`);
  },

  /**
   * Get risk acceptance assessments for a specific analysis
   * @param id - Analysis ID
   * @returns Promise with risk acceptance assessments
   */
  async getRiskAcceptance(id: string): Promise<Record<string, Record<string, RiskAcceptance>>> {
    return apiClient.get<Record<string, Record<string, RiskAcceptance>>>(`/analysis/${id}/risk-acceptance`);
  }
};

export default analysisApi;
