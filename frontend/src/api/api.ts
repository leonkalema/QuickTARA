/**
 * Main API module
 * Exports all API client services
 */

import apiClient from './index';
import componentApi from './components';
import analysisApi from './analysis';
import reportsApi from './reports';
import reviewApi from './review';

/**
 * Central API client that combines all API services
 */
export const api = {
  /**
   * Base API client for custom requests
   */
  client: apiClient,

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
};

// Export individual services for direct imports
export { apiClient, componentApi, analysisApi, reportsApi, reviewApi };

// Default export for convenience
export default api;
