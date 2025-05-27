/**
 * Assets API client
 */
import apiClient from './index';

/**
 * Asset type enumeration
 */
export enum AssetType {
  FIRMWARE = 'Firmware',
  SOFTWARE = 'Software',
  CONFIGURATION = 'Configuration',
  CALIBRATION = 'Calibration',
  DATA = 'Data',
  DIAGNOSTIC = 'Diagnostic',
  COMMUNICATION = 'Communication',
  HARDWARE = 'Hardware',
  INTERFACE = 'Interface',
  OTHER = 'Other'
}

/**
 * Security level enumeration
 */
export enum SecurityLevel {
  HIGH = 'High',
  MEDIUM = 'Medium',
  LOW = 'Low',
  NOT_APPLICABLE = 'N/A'
}

/**
 * Asset interface
 */
export interface Asset {
  asset_id: string;
  name: string;
  description?: string;
  asset_type: AssetType;
  data_types?: string[];
  storage_location?: string;
  scope_id: string;
  scope_version?: number;
  confidentiality: SecurityLevel;
  integrity: SecurityLevel;
  availability: SecurityLevel;
  authenticity_required: boolean;
  authorization_required: boolean;
  version: number;
  is_current: boolean;
  revision_notes?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

/**
 * AssetCreate interface - for creating new assets
 */
export interface AssetCreate {
  asset_id?: string;
  name: string;
  description?: string;
  asset_type: AssetType;
  data_types?: string[];
  storage_location?: string;
  scope_id: string;
  scope_version?: number;
  confidentiality: SecurityLevel;
  integrity: SecurityLevel;
  availability: SecurityLevel;
  authenticity_required: boolean;
  authorization_required: boolean;
}

/**
 * AssetUpdate interface - for updating existing assets
 */
export interface AssetUpdate {
  name?: string;
  description?: string;
  asset_type?: AssetType;
  data_types?: string[];
  storage_location?: string;
  scope_id?: string;
  scope_version?: number;
  confidentiality?: SecurityLevel;
  integrity?: SecurityLevel;
  availability?: SecurityLevel;
  authenticity_required?: boolean;
  authorization_required?: boolean;
}

/**
 * AssetList interface - for listing assets
 */
export interface AssetList {
  assets: Asset[];
  total: number;
}

/**
 * Assets API methods
 */
export const assetApi = {
  /**
   * Get a list of all assets with optional filtering
   */
  async getAll(skip = 0, limit = 100, scopeId?: string, assetType?: string): Promise<AssetList> {
    try {
      let queryParams = `?skip=${skip}&limit=${limit}`;
      
      if (scopeId) {
        queryParams += `&scope_id=${scopeId}`;
      }
      
      if (assetType) {
        queryParams += `&asset_type=${assetType}`;
      }
      
      return await apiClient.get(`/assets${queryParams}`);
    } catch (error) {
      console.error('Error fetching assets:', error);
      throw error;
    }
  },

  /**
   * Get a specific asset by ID
   */
  async getById(assetId: string): Promise<Asset> {
    try {
      return await apiClient.get(`/assets/${assetId}`);
    } catch (error) {
      console.error(`Error fetching asset ${assetId}:`, error);
      throw error;
    }
  },

  /**
   * Get all assets for a specific product
   */
  async getByProduct(scopeId: string, skip = 0, limit = 100): Promise<AssetList> {
    try {
      const queryParams = `?scope_id=${scopeId}&skip=${skip}&limit=${limit}`;
      return await apiClient.get(`/assets${queryParams}`);
    } catch (error) {
      console.error(`Error fetching assets for product ${scopeId}:`, error);
      throw error;
    }
  },

  /**
   * Create a new asset
   */
  async create(asset: AssetCreate): Promise<Asset> {
    try {
      return await apiClient.post('/assets', asset);
    } catch (error) {
      console.error('Error creating asset:', error);
      throw error;
    }
  },

  /**
   * Update an existing asset
   */
  async update(assetId: string, asset: AssetUpdate): Promise<Asset> {
    try {
      return await apiClient.put(`/assets/${assetId}`, asset);
    } catch (error) {
      console.error(`Error updating asset ${assetId}:`, error);
      throw error;
    }
  },

  /**
   * Delete an asset
   */
  async delete(assetId: string): Promise<void> {
    try {
      return await apiClient.delete(`/assets/${assetId}`);
    } catch (error) {
      console.error(`Error deleting asset ${assetId}:`, error);
      throw error;
    }
  }
};

export default assetApi;
