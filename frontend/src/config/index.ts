/**
 * Application configuration
 * Central location for configuration values
 */

/**
 * API base URL
 * In production, this would typically be loaded from environment variables
 */
export const API_BASE_URL = 'http://localhost:8080/api';

/**
 * Configuration for different environments
 */
export const config = {
  development: {
    apiBaseUrl: 'http://localhost:8080/api',
    debugEnabled: true,
  },
  production: {
    apiBaseUrl: '/api', // Relative URL for production deployment
    debugEnabled: false,
  },
  test: {
    apiBaseUrl: 'http://localhost:8080/api',
    debugEnabled: true,
  }
};

/**
 * Current environment
 * In production, this would be set by the build process
 */
export const environment = import.meta.env.MODE || 'development';

/**
 * Current configuration based on environment
 */
export const currentConfig = config[environment as keyof typeof config] || config.development;

/**
 * Export individual config values for convenience
 */
export const {
  apiBaseUrl,
  debugEnabled,
} = currentConfig;

export default currentConfig;
