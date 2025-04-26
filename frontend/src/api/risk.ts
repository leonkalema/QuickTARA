import axios from 'axios';
import { apiBaseUrl } from '../config';
import { handleApiError, safeApiCall } from '../utils/error-handler';
import { ApiError } from '../api';

// Types for risk framework
export interface ImpactDefinition {
  category: 'safety' | 'financial' | 'operational' | 'privacy' | 'reputation' | 'compliance';
  level: 'negligible' | 'minor' | 'moderate' | 'major' | 'critical';
  description: string;
  numerical_value: number; // 1-5
  examples: string[];
}

export interface LikelihoodDefinition {
  level: 'rare' | 'unlikely' | 'possible' | 'likely' | 'almost_certain';
  description: string;
  numerical_value: number; // 1-5
  probability_range?: { min: number; max: number }; // 0-1
  examples: string[];
}

export interface RiskMatrixCell {
  impact: number; // 1-5
  likelihood: number; // 1-5
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  numerical_score: number; // 1-25
}

export interface RiskMatrix {
  matrix: RiskMatrixCell[];
  description: string;
}

export interface RiskThreshold {
  level: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  requires_approval: boolean;
  approvers: string[];
  max_acceptable_score: number; // 1-25
}

export interface RiskFramework {
  framework_id: string;
  name: string;
  description?: string;
  version: string;
  impact_definitions: Record<string, ImpactDefinition[]>;
  likelihood_definitions: LikelihoodDefinition[];
  risk_matrix: RiskMatrix;
  risk_thresholds: RiskThreshold[];
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface RiskFrameworkCreate {
  name: string;
  description?: string;
  version: string;
  impact_definitions: Record<string, ImpactDefinition[]>;
  likelihood_definitions: LikelihoodDefinition[];
  risk_matrix: RiskMatrix;
  risk_thresholds: RiskThreshold[];
}

export interface RiskFrameworkUpdate {
  name?: string;
  description?: string;
  version?: string;
  impact_definitions?: Record<string, ImpactDefinition[]>;
  likelihood_definitions?: LikelihoodDefinition[];
  risk_matrix?: RiskMatrix;
  risk_thresholds?: RiskThreshold[];
  is_active?: boolean;
}

export interface RiskFrameworkList {
  frameworks: RiskFramework[];
  total: number;
}

// API Functions
export const getRiskFrameworks = async (skip = 0, limit = 100): Promise<RiskFrameworkList> => {
  return safeApiCall(async (): Promise<RiskFrameworkList> => {
    const response = await axios.get(`${apiBaseUrl}/risk?skip=${skip}&limit=${limit}`);
    return response.data;
  }) as Promise<RiskFrameworkList>;
};

export const getActiveRiskFramework = async (): Promise<RiskFramework> => {
  const result = await safeApiCall(async (): Promise<RiskFramework> => {
    const response = await axios.get(`${apiBaseUrl}/risk/active`);
    return response.data;
  });
  
  if (!result) {
    throw new ApiError('No active risk framework found', 404);
  }
  
  return result;
};

export const getRiskFramework = async (frameworkId: string): Promise<RiskFramework> => {
  const result = await safeApiCall(async (): Promise<RiskFramework> => {
    const response = await axios.get(`${apiBaseUrl}/risk/${frameworkId}`);
    return response.data;
  });
  
  if (!result) {
    throw new ApiError(`Risk framework with ID ${frameworkId} not found`, 404);
  }
  
  return result;
};

export const createRiskFramework = async (framework: RiskFrameworkCreate): Promise<RiskFramework> => {
  const result = await safeApiCall(async (): Promise<RiskFramework> => {
    const response = await axios.post(`${apiBaseUrl}/risk`, framework);
    return response.data;
  });
  
  if (!result) {
    throw new ApiError('Failed to create risk framework', 500);
  }
  
  return result;
};

export const updateRiskFramework = async (
  frameworkId: string,
  framework: RiskFrameworkUpdate
): Promise<RiskFramework> => {
  const result = await safeApiCall(async (): Promise<RiskFramework> => {
    const response = await axios.put(`${apiBaseUrl}/risk/${frameworkId}`, framework);
    return response.data;
  });
  
  if (!result) {
    throw new ApiError(`Failed to update risk framework with ID ${frameworkId}`, 500);
  }
  
  return result;
};

export const setRiskFrameworkActive = async (frameworkId: string, active = true): Promise<RiskFramework> => {
  const result = await safeApiCall(async (): Promise<RiskFramework> => {
    const response = await axios.put(`${apiBaseUrl}/risk/${frameworkId}/active?active=${active}`);
    return response.data;
  });
  
  if (!result) {
    throw new ApiError(`Failed to set risk framework ${frameworkId} active state to ${active}`, 500);
  }
  
  return result;
};

export const deleteRiskFramework = async (frameworkId: string): Promise<void> => {
  await safeApiCall(async (): Promise<void> => {
    await axios.delete(`${apiBaseUrl}/risk/${frameworkId}`);
  });
};
