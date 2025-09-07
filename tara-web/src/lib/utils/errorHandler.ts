/**
 * Enhanced error handling utilities for frontend
 */

export interface APIError {
  message: string;
  error_type: string;
  field_errors?: Record<string, string>;
  valid_types?: string[];
  operation?: string;
}

export interface APIResponse<T = any> {
  success?: boolean;
  message?: string;
  data?: T;
  error_type?: string;
  field_errors?: Record<string, string>;
}

export class NetworkError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends Error {
  constructor(message: string, public fieldErrors: Record<string, string>) {
    super(message);
    this.name = 'ValidationError';
  }
}

export function parseAPIError(error: any): APIError {
  // Handle fetch/network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      message: 'Network connection failed. Please check your internet connection.',
      error_type: 'network_error'
    };
  }

  // Handle timeout errors
  if (error.name === 'AbortError') {
    return {
      message: 'Request timed out. Please try again.',
      error_type: 'timeout_error'
    };
  }

  // Handle HTTP response errors
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data || {};

    switch (status) {
      case 400:
        return {
          message: data.message || 'Invalid request parameters',
          error_type: data.error_type || 'bad_request',
          field_errors: data.field_errors,
          valid_types: data.valid_types
        };
      
      case 401:
        return {
          message: 'Authentication required. Please log in.',
          error_type: 'authentication_required'
        };
      
      case 403:
        return {
          message: 'You do not have permission to perform this action.',
          error_type: 'permission_denied'
        };
      
      case 404:
        return {
          message: data.message || 'Resource not found',
          error_type: data.error_type || 'not_found',
          field_errors: data.field_errors
        };
      
      case 409:
        return {
          message: data.message || 'Resource already exists',
          error_type: data.error_type || 'conflict',
          field_errors: data.field_errors
        };
      
      case 422:
        return {
          message: data.message || 'Validation failed',
          error_type: data.error_type || 'validation_error',
          field_errors: data.field_errors
        };
      
      case 429:
        return {
          message: 'Too many requests. Please wait a moment and try again.',
          error_type: 'rate_limit'
        };
      
      case 500:
        return {
          message: data.message || 'Server error occurred. Please try again later.',
          error_type: data.error_type || 'server_error'
        };
      
      default:
        return {
          message: data.message || `Request failed with status ${status}`,
          error_type: data.error_type || 'unknown_error'
        };
    }
  }

  // Handle unknown errors
  return {
    message: error.message || 'An unexpected error occurred',
    error_type: 'unknown_error'
  };
}

export function getErrorMessage(error: APIError): string {
  // Return field-specific error if available
  if (error.field_errors) {
    const firstError = Object.values(error.field_errors)[0];
    if (firstError) return firstError;
  }
  
  return error.message;
}

export function getFieldError(error: APIError, fieldName: string): string | undefined {
  return error.field_errors?.[fieldName];
}

export function hasFieldErrors(error: APIError): boolean {
  return !!(error.field_errors && Object.keys(error.field_errors).length > 0);
}

export function isRetryableError(error: APIError): boolean {
  const retryableTypes = [
    'network_error',
    'timeout_error',
    'server_error',
    'rate_limit'
  ];
  
  return retryableTypes.includes(error.error_type);
}

export async function withRetry<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let lastError: any;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error;
      const apiError = parseAPIError(error);
      
      // Don't retry non-retryable errors
      if (!isRetryableError(apiError)) {
        throw error;
      }
      
      // Don't retry on last attempt
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delayMs * attempt));
    }
  }
  
  throw lastError;
}

export function createAbortController(timeoutMs: number = 30000): AbortController {
  const controller = new AbortController();
  
  setTimeout(() => {
    controller.abort();
  }, timeoutMs);
  
  return controller;
}
