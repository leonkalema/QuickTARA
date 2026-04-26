import type { Asset, CreateAssetRequest, AssetsResponse } from '../types/asset';
import { apiFetch } from '$lib/api/apiClient';

interface GetAllParams {
  skip?: number;
  limit?: number;
  scope_id?: string;
  asset_type?: string;
}

interface GetByProductParams {
  skip?: number;
  limit?: number;
}

export const assetApi = {
  async getAll(params?: GetAllParams): Promise<AssetsResponse> {
    const q = new URLSearchParams();
    if (params?.skip)       q.set('skip',       params.skip.toString());
    if (params?.limit)      q.set('limit',      params.limit.toString());
    if (params?.scope_id)   q.set('scope_id',   params.scope_id);
    if (params?.asset_type) q.set('asset_type', params.asset_type);
    return apiFetch<AssetsResponse>(`/assets?${q}`);
  },

  async getById(id: string): Promise<Asset> {
    return apiFetch<Asset>(`/assets/${id}`);
  },

  async create(asset: CreateAssetRequest): Promise<Asset> {
    return apiFetch<Asset>('/assets', {
      method: 'POST',
      body: JSON.stringify(asset),
    });
  },

  async update(id: string, asset: Partial<CreateAssetRequest>): Promise<Asset> {
    return apiFetch<Asset>(`/assets/${id}`, {
      method: 'PUT',
      body: JSON.stringify(asset),
    });
  },

  async delete(id: string): Promise<void> {
    return apiFetch<void>(`/assets/${id}`, { method: 'DELETE' });
  },

  async getByProduct(productId: string, params?: GetByProductParams): Promise<AssetsResponse> {
    const q = new URLSearchParams();
    if (params?.skip)  q.set('skip',  params.skip.toString());
    if (params?.limit) q.set('limit', params.limit.toString());
    return apiFetch<AssetsResponse>(`/assets/product/${productId}?${q}`);
  },

  async getHistory(id: string): Promise<Asset[]> {
    return apiFetch<Asset[]>(`/assets/${id}/history`);
  },
};
