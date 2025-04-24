/**
 * Review API client
 * Handles all API calls related to risk review workflow
 */

import apiClient from './index';

/**
 * Risk treatment decision types
 */
export enum RiskTreatmentDecision {
  ACCEPT = 'Accept',
  ACCEPT_WITH_CONTROLS = 'Accept with Controls',
  TRANSFER = 'Transfer',
  AVOID = 'Avoid',
  MITIGATE = 'Mitigate'
}

/**
 * Risk severity levels
 */
export enum RiskSeverity {
  NEGLIGIBLE = 'Negligible',
  LOW = 'Low',
  MEDIUM = 'Medium',
  HIGH = 'High',
  CRITICAL = 'Critical'
}

/**
 * Stakeholder role/concern
 */
export enum StakeholderConcern {
  COMPLIANCE = 'Regulatory Compliance',
  SAFETY = 'Safety Impact',
  PRIVACY = 'Privacy & Data Protection',
  FINANCIAL = 'Financial Impact',
  REPUTATION = 'Reputation & Brand',
  OPERATIONAL = 'Operational Continuity'
}

/**
 * Evidence reference
 */
export interface Evidence {
  id?: string;
  type: string;
  description: string;
  reference: string;
  date_added?: string;
}

/**
 * Risk treatment review decision
 */
export interface RiskReviewDecision {
  id?: string;
  analysis_id: string;
  component_id: string;
  threat_name: string;
  original_decision: RiskTreatmentDecision;
  final_decision: RiskTreatmentDecision;
  justification: string;
  reviewer_name: string;
  reviewed_at?: string;
  approval_status: 'Pending' | 'Approved' | 'Rejected';
  conditions?: string[];
  evidence?: Evidence[];
  comments?: string;
  reassessment_date?: string;
}

/**
 * Review status summary
 */
export interface ReviewStatus {
  total_risks: number;
  reviewed_risks: number;
  pending_risks: number;
  approved_risks: number;
  rejected_risks: number;
  completion_percentage: number;
}

/**
 * Review API service
 */
export const reviewApi = {
  /**
   * Get all risk decisions for review for an analysis
   * @param analysisId - Analysis ID
   * @returns Promise with array of risk decisions
   */
  async getDecisions(analysisId: string): Promise<RiskReviewDecision[]> {
    return apiClient.get<RiskReviewDecision[]>(`/review/${analysisId}`);
  },

  /**
   * Get risk decisions for a specific component
   * @param analysisId - Analysis ID
   * @param componentId - Component ID
   * @returns Promise with array of risk decisions
   */
  async getComponentDecisions(analysisId: string, componentId: string): Promise<RiskReviewDecision[]> {
    return apiClient.get<RiskReviewDecision[]>(`/review/${analysisId}/component/${componentId}`);
  },

  /**
   * Get a specific risk decision
   * @param decisionId - Decision ID
   * @returns Promise with risk decision
   */
  async getDecision(decisionId: string): Promise<RiskReviewDecision> {
    return apiClient.get<RiskReviewDecision>(`/review/decision/${decisionId}`);
  },

  /**
   * Submit a risk treatment decision review
   * @param decision - Updated risk decision
   * @returns Promise with updated risk decision
   */
  async submitDecision(decision: RiskReviewDecision): Promise<RiskReviewDecision> {
    if (decision.id) {
      // Update existing decision
      return apiClient.put<RiskReviewDecision>(`/review/decision/${decision.id}`, decision);
    } else {
      // Create new decision
      return apiClient.post<RiskReviewDecision>(`/review/${decision.analysis_id}/decision`, decision);
    }
  },

  /**
   * Submit evidence for a risk decision
   * @param decisionId - Decision ID
   * @param evidence - Evidence data
   * @returns Promise with updated evidence
   */
  async submitEvidence(decisionId: string, evidence: Evidence): Promise<Evidence> {
    if (evidence.id) {
      // Update existing evidence
      return apiClient.put<Evidence>(`/review/decision/${decisionId}/evidence/${evidence.id}`, evidence);
    } else {
      // Create new evidence
      return apiClient.post<Evidence>(`/review/decision/${decisionId}/evidence`, evidence);
    }
  },

  /**
   * Delete evidence from a risk decision
   * @param decisionId - Decision ID
   * @param evidenceId - Evidence ID
   * @returns Promise with success response
   */
  async deleteEvidence(decisionId: string, evidenceId: string): Promise<void> {
    return apiClient.delete<void>(`/review/decision/${decisionId}/evidence/${evidenceId}`);
  },

  /**
   * Get the overall review status for an analysis
   * @param analysisId - Analysis ID
   * @returns Promise with review status
   */
  async getReviewStatus(analysisId: string): Promise<ReviewStatus> {
    return apiClient.get<ReviewStatus>(`/review/${analysisId}/status`);
  },

  /**
   * Approve all pending reviews for an analysis
   * @param analysisId - Analysis ID
   * @param approverName - Name of the approver
   * @returns Promise with updated review status
   */
  async approveAll(analysisId: string, approverName: string): Promise<ReviewStatus> {
    return apiClient.post<ReviewStatus>(`/review/${analysisId}/approve-all`, { approver_name: approverName });
  },

  /**
   * Finalize the review process for an analysis
   * This marks the review as complete and ready for final reporting
   * @param analysisId - Analysis ID
   * @returns Promise with success response
   */
  async finalizeReview(analysisId: string): Promise<void> {
    return apiClient.post<void>(`/review/${analysisId}/finalize`, {});
  },

  /**
   * Get a list of required approvers for a risk decision
   * based on its severity and impact categories
   * @param decisionId - Decision ID
   * @returns Promise with array of stakeholder concerns
   */
  async getRequiredApprovers(decisionId: string): Promise<StakeholderConcern[]> {
    return apiClient.get<StakeholderConcern[]>(`/review/decision/${decisionId}/required-approvers`);
  },

  /**
   * Add a comment to a risk decision
   * @param decisionId - Decision ID
   * @param comment - Comment text
   * @param author - Comment author
   * @returns Promise with updated decision
   */
  async addComment(decisionId: string, comment: string, author: string): Promise<RiskReviewDecision> {
    return apiClient.post<RiskReviewDecision>(`/review/decision/${decisionId}/comment`, {
      comment,
      author
    });
  }
};

export default reviewApi;
