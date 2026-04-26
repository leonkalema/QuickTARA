import type { Product, CreateProductRequest, ProductsResponse } from '../types/product';
import { apiFetch } from './apiClient';

export const productApi = {
  async getAll(params?: {
    skip?: number;
    limit?: number;
    product_type?: string;
    status?: string;
  }): Promise<ProductsResponse> {
    const q = new URLSearchParams();
    if (params?.skip) q.set('skip', params.skip.toString());
    if (params?.limit) q.set('limit', params.limit.toString());
    if (params?.product_type) q.set('product_type', params.product_type);
    if (params?.status) q.set('status', params.status);
    return apiFetch<ProductsResponse>(`/products?${q}`);
  },

  getById: (id: string): Promise<Product> =>
    apiFetch<Product>(`/products/${id}`),

  create: (product: CreateProductRequest): Promise<Product> =>
    apiFetch<Product>('/products', { method: 'POST', body: JSON.stringify(product) }),

  update: (id: string, product: Partial<CreateProductRequest>): Promise<Product> =>
    apiFetch<Product>(`/products/${id}`, { method: 'PUT', body: JSON.stringify(product) }),

  delete: (id: string): Promise<void> =>
    apiFetch<void>(`/products/${id}`, { method: 'DELETE' }),

  getStats: (): Promise<Record<string, unknown>> =>
    apiFetch<Record<string, unknown>>('/products/stats'),
};
