/**
 * Main API module
 * Exports all API client services
 */

import apiClient from './index';
import scopeApi from './scope';
import componentApi from './components';
import analysisApi from './analysis';
import reportsApi from './reports';
import reviewApi from './review';
import settingsApi from './settings';

/**
 * Central API client that combines all API services
 */
export const api = {
  /**
   * Base API client for custom requests
   */
  client: apiClient,

  /**
   * System scope definition API
   */
  scope: scopeApi,

  /**
   * Component management API
   */
  components: componentApi,

  /**
   * Analysis and threat assessment API
   */
  analysis: analysisApi,

  /**
   * Report generation and management API
   */
  reports: reportsApi,

  /**
   * Risk review workflow API
   */
  review: reviewApi,

  /**
   * Settings and configuration API
   */
  settings: settingsApi,
};

// Export individual services for direct imports
export { apiClient, scopeApi, componentApi, analysisApi, reportsApi, reviewApi, settingsApi };

// Default export for convenience
export default api;
