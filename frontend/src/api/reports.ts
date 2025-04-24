/**
 * Reports API client
 * Handles all API calls related to report generation and management
 */

import apiClient from './index';

/**
 * Supported report formats
 */
export enum ReportFormat {
  TXT = 'txt',
  JSON = 'json',
  XLSX = 'xlsx',
  PDF = 'pdf',
}

/**
 * Report generation request
 */
export interface ReportRequest {
  analysis_id: string;
  format: ReportFormat;
  include_review_status?: boolean;
  include_justifications?: boolean;
  custom_title?: string;
}

/**
 * Report metadata
 */
export interface Report {
  id: string;
  analysis_id: string;
  format: ReportFormat;
  created_at: string;
  filename: string;
  size: number;
  title?: string;
}

/**
 * Reports API service
 */
export const reportsApi = {
  /**
   * Generate a new report
   * @param reportRequest - Report generation request
   * @returns Promise with generated report metadata
   */
  async generateReport(reportRequest: ReportRequest): Promise<Report> {
    return apiClient.post<Report>('/reports', reportRequest);
  },

  /**
   * Get all reports
   * @returns Promise with array of report metadata
   */
  async getAll(): Promise<Report[]> {
    return apiClient.get<Report[]>('/reports');
  },

  /**
   * Get reports for a specific analysis
   * @param analysisId - Analysis ID
   * @returns Promise with array of report metadata
   */
  async getByAnalysisId(analysisId: string): Promise<Report[]> {
    return apiClient.get<Report[]>(`/reports?analysis_id=${analysisId}`);
  },

  /**
   * Get report metadata by ID
   * @param id - Report ID
   * @returns Promise with report metadata
   */
  async getById(id: string): Promise<Report> {
    return apiClient.get<Report>(`/reports/${id}`);
  },

  /**
   * Delete a report
   * @param id - Report ID
   * @returns Promise with success response
   */
  async deleteReport(id: string): Promise<void> {
    return apiClient.delete<void>(`/reports/${id}`);
  },

  /**
   * Get URL for downloading a report
   * This returns a direct URL to download the file rather than
   * processing the response in JavaScript
   * @param id - Report ID
   * @returns URL for downloading the report
   */
  getDownloadUrl(id: string): string {
    return `${apiClient.API_BASE_URL}/reports/${id}/download`;
  },

  /**
   * Generate and download a report in one step
   * This will trigger the browser's download functionality
   * @param reportRequest - Report generation request
   */
  async generateAndDownload(reportRequest: ReportRequest): Promise<void> {
    const report = await this.generateReport(reportRequest);
    window.location.href = this.getDownloadUrl(report.id);
  },

  /**
   * Preview a report (for formats that support preview)
   * @param id - Report ID
   * @returns Promise with report content (text or HTML)
   */
  async previewReport(id: string): Promise<string> {
    return apiClient.get<string>(`/reports/${id}/preview`);
  },

  /**
   * Get available report templates
   * @returns Promise with array of template names
   */
  async getTemplates(): Promise<string[]> {
    return apiClient.get<string[]>('/reports/templates');
  }
};

export default reportsApi;
