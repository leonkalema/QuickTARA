import type { Asset, CreateAssetRequest, AssetsResponse, AssetApiError } from '../types/asset';

const API_BASE = 'http://127.0.0.1:8080/api';

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`HTTP ${response.status}: ${errorText}`);
  }
  return response.json();
}

export const assetApi = {
  /**
   * Get all assets with optional filtering
   */
  async getAll(params?: {
    skip?: number;
    limit?: number;
    scope_id?: string;
    asset_type?: string;
  }): Promise<AssetsResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.scope_id) searchParams.set('scope_id', params.scope_id);
    if (params?.asset_type) searchParams.set('asset_type', params.asset_type);

    const response = await fetch(`${API_BASE}/assets?${searchParams}`);
    return handleResponse<AssetsResponse>(response);
  },

  /**
   * Get a specific asset by ID
   */
  async getById(id: string): Promise<Asset> {
    const response = await fetch(`${API_BASE}/assets/${id}`);
    return handleResponse<Asset>(response);
  },

  /**
   * Create a new asset
   */
  async create(asset: CreateAssetRequest): Promise<Asset> {
    const response = await fetch(`${API_BASE}/assets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(asset),
    });
    return handleResponse<Asset>(response);
  },

  /**
   * Update an existing asset
   */
  async update(id: string, asset: Partial<CreateAssetRequest>): Promise<Asset> {
    const response = await fetch(`${API_BASE}/assets/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(asset),
    });
    return handleResponse<Asset>(response);
  },

  /**
   * Delete an asset
   */
  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/assets/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to delete asset: ${response.status}`);
    }
  },

  /**
   * Get assets by product ID
   */
  async getByProduct(productId: string, params?: {
    skip?: number;
    limit?: number;
  }): Promise<AssetsResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());

    const response = await fetch(`${API_BASE}/assets/product/${productId}?${searchParams}`);
    return handleResponse<AssetsResponse>(response);
  },

  /**
   * Get asset history
   */
  async getHistory(id: string): Promise<Asset[]> {
    const response = await fetch(`${API_BASE}/assets/${id}/history`);
    return handleResponse<Asset[]>(response);
  }
};
