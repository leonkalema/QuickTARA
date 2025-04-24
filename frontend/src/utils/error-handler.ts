/**
 * Error handling utilities for API requests
 */

import { ApiError } from '../api';

/**
 * Type for error handler callback
 */
export type ErrorHandler = (error: Error | ApiError) => void;

/**
 * Default error handler function that can be globally set
 */
let globalErrorHandler: ErrorHandler | null = null;

/**
 * Set global error handler
 * @param handler - Error handler function
 */
export const setGlobalErrorHandler = (handler: ErrorHandler): void => {
  globalErrorHandler = handler;
};

/**
 * Handle API errors with optional custom handler
 * @param error - Error to handle
 * @param customHandler - Optional custom error handler
 * @returns Boolean indicating if the error was handled
 */
export const handleApiError = (
  error: unknown,
  customHandler?: ErrorHandler
): boolean => {
  // Ensure it's an Error object
  if (!(error instanceof Error)) {
    console.error('Unknown error:', error);
    return false;
  }

  // If custom handler is provided, use it
  if (customHandler) {
    customHandler(error);
    return true;
  }

  // Use global handler if available
  if (globalErrorHandler) {
    globalErrorHandler(error);
    return true;
  }

  // Default error handling
  if (error instanceof ApiError) {
    console.error(`API Error (${error.status}): ${error.message}`, error.data);
  } else {
    console.error('Application Error:', error.message);
  }

  return false;
};

/**
 * Wrapper for async API calls with error handling
 * @param apiCall - Async API function to call
 * @param errorHandler - Optional custom error handler
 * @returns Promise with result or null on error
 */
export async function safeApiCall<T>(
  apiCall: () => Promise<T>,
  errorHandler?: ErrorHandler
): Promise<T | null> {
  try {
    return await apiCall();
  } catch (error) {
    handleApiError(error, errorHandler);
    return null;
  }
}

/**
 * Format API error message for display
 * @param error - Error object
 * @returns Formatted error message
 */
export const formatErrorMessage = (error: unknown): string => {
  if (error instanceof ApiError) {
    if (error.errors && error.errors.length > 0) {
      return error.errors.join('. ');
    }
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'Unknown error occurred';
};

export default {
  handleApiError,
  safeApiCall,
  formatErrorMessage,
  setGlobalErrorHandler
};
