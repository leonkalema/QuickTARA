/**
 * Product API client (replacing System Scope API)
 */
import apiClient from './index';

/**
 * Product type enumeration
 */
export enum ProductType {
  ECU = 'ECU',
  GATEWAY = 'Gateway',
  SENSOR = 'Sensor',
  ACTUATOR = 'Actuator',
  NETWORK = 'Network',
  EXTERNAL_DEVICE = 'ExternalDevice',
  OTHER = 'Other'
}

/**
 * Safety level enumeration
 */
export enum SafetyLevel {
  QM = 'QM',
  ASIL_A = 'ASIL A',
  ASIL_B = 'ASIL B',
  ASIL_C = 'ASIL C',
  ASIL_D = 'ASIL D'
}

/**
 * Trust zone enumeration
 */
export enum TrustZone {
  CRITICAL = 'Critical',
  BOUNDARY = 'Boundary',
  STANDARD = 'Standard',
  UNTRUSTED = 'Untrusted'
}

/**
 * Product interface (formerly SystemScope)
 */
export interface Product {
  scope_id: string;
  name: string;
  product_type: ProductType;
  description?: string;
  boundaries?: string[];
  objectives?: string[];
  stakeholders?: string[];
  safety_level: SafetyLevel;
  interfaces?: string[];
  access_points?: string[];
  location: string;
  trust_zone: TrustZone;
  version: number;
  is_current: boolean;
  revision_notes?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

/**
 * ProductCreate interface - for creating new products
 */
export interface ProductCreate {
  name: string;
  product_type: ProductType;
  description?: string;
  boundaries?: string[];
  objectives?: string[];
  stakeholders?: string[];
  safety_level: SafetyLevel;
  interfaces?: string[];
  access_points?: string[];
  location: string;
  trust_zone: TrustZone;
  scope_id?: string;
}

/**
 * ProductUpdate interface - for updating existing products
 */
export interface ProductUpdate {
  name?: string;
  product_type?: ProductType;
  description?: string;
  boundaries?: string[];
  objectives?: string[];
  stakeholders?: string[];
  safety_level?: SafetyLevel;
  interfaces?: string[];
  access_points?: string[];
  location?: string;
  trust_zone?: TrustZone;
}

/**
 * ProductList interface - for listing products
 */
export interface ProductList {
  scopes: Product[]; // Note: API still returns "scopes" as the key
  total: number;
}

/**
 * Product API methods (same interface as old scopeApi)
 */
export const productApi = {
  /**
   * Get a list of all products
   */
  async getAll(skip = 0, limit = 100): Promise<ProductList> {
    try {
      const queryParams = `?skip=${skip}&limit=${limit}`;
      return await apiClient.get(`/products${queryParams}`);
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  },

  /**
   * Get a specific product by ID
   */
  async getById(scopeId: string): Promise<Product> {
    try {
      return await apiClient.get(`/products/${scopeId}`);
    } catch (error) {
      console.error(`Error fetching product ${scopeId}:`, error);
      throw error;
    }
  },

  /**
   * Create a new product
   */
  async create(product: ProductCreate): Promise<Product> {
    try {
      return await apiClient.post('/products', product);
    } catch (error) {
      console.error('Error creating product:', error);
      throw error;
    }
  },

  /**
   * Update an existing product
   */
  async update(scopeId: string, product: ProductUpdate): Promise<Product> {
    try {
      return await apiClient.put(`/products/${scopeId}`, product);
    } catch (error) {
      console.error(`Error updating product ${scopeId}:`, error);
      throw error;
    }
  },

  /**
   * Delete a product
   */
  async delete(scopeId: string): Promise<void> {
    try {
      return await apiClient.delete(`/products/${scopeId}`);
    } catch (error) {
      console.error(`Error deleting product ${scopeId}:`, error);
      throw error;
    }
  }
};

// For backward compatibility, reexport the same API under the scopeApi name
export const scopeApi = productApi;

export default productApi;
