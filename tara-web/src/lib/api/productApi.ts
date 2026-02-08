import type { Product, CreateProductRequest, ProductsResponse } from '../types/product';
import { API_BASE_URL } from '$lib/config';
import { browser } from '$app/environment';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

class ProductApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ProductApiError';
  }
}

function getAuthHeaders(): HeadersInit {
  const auth = get(authStore);
  const headers: HeadersInit = {
    'Content-Type': 'application/json'
  };
  const tokenFromStorage: string | null = browser ? localStorage.getItem('auth_token') : null;
  const token: string | null = auth.token ?? tokenFromStorage;
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    throw new ProductApiError(
      `API Error: ${response.status} - ${errorText}`,
      response.status
    );
  }
  return response.json();
}

export const productApi = {
  /**
   * Get all products with optional filtering
   */
  async getAll(params?: {
    skip?: number;
    limit?: number;
    product_type?: string;
    status?: string;
  }): Promise<ProductsResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.product_type) searchParams.set('product_type', params.product_type);
    if (params?.status) searchParams.set('status', params.status);

    const response = await fetch(`${API_BASE_URL}/products?${searchParams}`, {
      headers: getAuthHeaders()
    });
    return handleResponse<ProductsResponse>(response);
  },

  /**
   * Get a specific product by ID
   */
  async getById(id: string): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Product>(response);
  },

  /**
   * Create a new product
   */
  async create(product: CreateProductRequest): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/products`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(product),
    });
    return handleResponse<Product>(response);
  },

  /**
   * Update an existing product
   */
  async update(id: string, product: Partial<CreateProductRequest>): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(product),
    });
    return handleResponse<Product>(response);
  },

  /**
   * Delete a product
   */
  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) {
      throw new ProductApiError(`Failed to delete product: ${response.status}`);
    }
  },

  /**
   * Get product statistics
   */
  async getStats(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/products/stats`, {
      headers: getAuthHeaders()
    });
    return handleResponse(response);
  }
};
