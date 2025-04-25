/**
 * API Client Setup for QuickTARA
 * Configures the base API client with error handling, authentication, and request/response interceptors
 */

import { apiBaseUrl } from '../config';

/**
 * Standard API response type
 */
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
}

/**
 * API error structure
 */
export class ApiError extends Error {
  public status: number;
  public data?: any;
  public errors?: string[];

  constructor(message: string, status: number, data?: any, errors?: string[]) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.errors = errors;
  }
}

/**
 * Enum for HTTP methods
 */
export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
  PATCH = 'PATCH'
}

/**
 * Request options
 */
export interface RequestOptions {
  method: HttpMethod;
  headers?: Record<string, string>;
  body?: any;
  isFormData?: boolean;
}

/**
 * Base API client for making HTTP requests
 */
export const apiClient = {
  /**
   * Base API URL for constructing absolute URLs
   */
  API_BASE_URL: apiBaseUrl,

  /**
   * Send a request to the API
   * @param endpoint - API endpoint path
   * @param options - Request options
   * @returns Promise with response data
   */
  async request<T>(endpoint: string, options: RequestOptions): Promise<T> {
    const url = `${apiBaseUrl}${endpoint}`;

    // Default headers
    const headers: Record<string, string> = {
      'Accept': 'application/json',
      ...options.headers || {}
    };

    // Handle body based on content type
    let body: string | FormData | undefined = undefined;
    
    if (options.body) {
      if (options.isFormData) {
        body = options.body;
      } else {
        headers['Content-Type'] = 'application/json';
        body = JSON.stringify(options.body);
      }
    }

    try {
      const response = await fetch(url, {
        method: options.method,
        headers,
        body,
        credentials: 'same-origin', // Only send credentials for same-origin requests
      });

      // Handle non-2xx responses
      if (!response.ok) {
        let errorData: any = {};
        let errorMessage = `API Error: ${response.status} ${response.statusText}`;

        try {
          errorData = await response.json();
          if (errorData.detail || errorData.message) {
            errorMessage = errorData.detail || errorData.message;
          }
        } catch (e) {
          // If we can't parse the error as JSON, use the status text
        }

        throw new ApiError(
          errorMessage,
          response.status,
          errorData,
          Array.isArray(errorData.errors) ? errorData.errors : undefined
        );
      }

      // Handle empty responses
      if (response.status === 204) {
        return {} as T;
      }

      // Parse JSON response
      return await response.json() as T;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Handle network errors or other issues
      throw new ApiError(
        error instanceof Error ? error.message : 'Unknown API error occurred',
        0 // No status code for network errors
      );
    }
  },

  /**
   * GET request
   * @param endpoint - API endpoint
   * @param headers - Optional additional headers
   * @returns Promise with response data
   */
  async get<T>(endpoint: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, {
      method: HttpMethod.GET,
      headers
    });
  },

  /**
   * POST request
   * @param endpoint - API endpoint
   * @param body - Request body
   * @param headers - Optional additional headers
   * @returns Promise with response data
   */
  async post<T>(endpoint: string, body?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, {
      method: HttpMethod.POST,
      body,
      headers: {
        // Add Cache-Control header to prevent service worker caching
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache',
        ...headers
      }
    });
  },

  /**
   * PUT request
   * @param endpoint - API endpoint
   * @param body - Request body
   * @param headers - Optional additional headers
   * @returns Promise with response data
   */
  async put<T>(endpoint: string, body?: any, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, {
      method: HttpMethod.PUT,
      body,
      headers: {
        // Add Cache-Control header to prevent service worker caching
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache',
        ...headers
      }
    });
  },

  /**
   * DELETE request
   * @param endpoint - API endpoint
   * @param headers - Optional additional headers
   * @returns Promise with response data
   */
  async delete<T>(endpoint: string, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, {
      method: HttpMethod.DELETE,
      headers: {
        // Add Cache-Control header to prevent service worker caching
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'Pragma': 'no-cache',
        ...headers
      }
    });
  },

  /**
   * Form data POST request (for file uploads)
   * @param endpoint - API endpoint
   * @param formData - Form data to send
   * @param headers - Optional additional headers
   * @returns Promise with response data
   */
  async uploadForm<T>(endpoint: string, formData: FormData, headers?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, {
      method: HttpMethod.POST,
      body: formData,
      isFormData: true,
      headers
    });
  }
};

// Export default for convenience
export default apiClient;
