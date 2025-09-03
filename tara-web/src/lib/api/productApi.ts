import type { Product, CreateProductRequest, ProductsResponse } from '../types/product';

const API_BASE = 'http://127.0.0.1:8080/api';

class ProductApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ProductApiError';
  }
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

    const response = await fetch(`${API_BASE}/products?${searchParams}`);
    return handleResponse<ProductsResponse>(response);
  },

  /**
   * Get a specific product by ID
   */
  async getById(id: string): Promise<Product> {
    const response = await fetch(`${API_BASE}/products/${id}`);
    return handleResponse<Product>(response);
  },

  /**
   * Create a new product
   */
  async create(product: CreateProductRequest): Promise<Product> {
    const response = await fetch(`${API_BASE}/products`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(product),
    });
    return handleResponse<Product>(response);
  },

  /**
   * Update an existing product
   */
  async update(id: string, product: Partial<CreateProductRequest>): Promise<Product> {
    const response = await fetch(`${API_BASE}/products/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(product),
    });
    return handleResponse<Product>(response);
  },

  /**
   * Delete a product
   */
  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/products/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new ProductApiError(`Failed to delete product: ${response.status}`);
    }
  },

  /**
   * Get product statistics
   */
  async getStats(): Promise<any> {
    const response = await fetch(`${API_BASE}/products/stats`);
    return handleResponse(response);
  }
};
