/**
 * CRA Compliance TypeScript types
 *
 * Used by: lib/api/craApi.ts, features/cra/*, routes/cra/*
 */

export type CraClassification = 'default' | 'class_i' | 'class_ii' | 'critical';

export type CraProductType = 'current' | 'legacy_a' | 'legacy_b' | 'legacy_c';

export type CraAssessmentStatus = 'draft' | 'in_progress' | 'complete';

export type CraRequirementStatus = 'not_started' | 'partial' | 'compliant' | 'not_applicable';

export type CompensatingControlStatus = 'planned' | 'implemented' | 'verified';

export type GapSeverity = 'none' | 'low' | 'medium' | 'high' | 'critical';

export type CompliancePath = 'direct_patch' | 'compensating_control' | 'hybrid';

export type TargetMarket = 'eu' | 'non_eu' | 'global';

export interface InventoryItem {
  readonly id: string;
  readonly assessment_id: string;
  readonly sku: string;
  readonly firmware_version?: string;
  readonly units_in_stock: number;
  readonly units_in_field: number;
  readonly oem_customer?: string;
  readonly target_market: TargetMarket;
  readonly last_production_date?: string;
  readonly notes?: string;
  readonly created_at?: string;
  readonly updated_at?: string;
}

export interface InventorySummary {
  readonly total_skus: number;
  readonly total_units_in_stock: number;
  readonly total_units_in_field: number;
  readonly eu_units: number;
  readonly non_eu_units: number;
  readonly oems: string[];
}

export interface ClassificationQuestion {
  readonly id: string;
  readonly text: string;
  readonly hint: string;
}

export interface ClassificationResult {
  readonly classification: CraClassification;
  readonly conformity_assessment: string;
  readonly compliance_deadline: string;
  readonly cost_estimate_min: number;
  readonly cost_estimate_max: number;
  readonly automotive_exception: boolean;
  readonly rationale: string;
}

export interface CraRequirementDefinition {
  readonly id: string;
  readonly name: string;
  readonly article: string;
  readonly category: string;
}

export interface CraRequirementStatusRecord {
  readonly id: string;
  readonly assessment_id: string;
  readonly requirement_id: string;
  readonly requirement_name?: string;
  readonly requirement_article?: string;
  readonly requirement_category?: string;
  readonly status: CraRequirementStatus;
  readonly auto_mapped: boolean;
  readonly mapped_artifact_type?: string;
  readonly mapped_artifact_count: number;
  readonly owner?: string;
  readonly target_date?: string;
  readonly evidence_notes?: string;
  readonly evidence_links: string[];
  readonly gap_description?: string;
  readonly remediation_plan?: string;
  readonly gap_severity: GapSeverity;
  readonly residual_risk_level: GapSeverity;
  readonly created_at?: string;
  readonly updated_at?: string;
}

export interface MitigatedRequirementInfo {
  readonly requirement_status_id: string;
  readonly requirement_id: string;
  readonly requirement_name?: string;
}

export interface CompensatingControl {
  readonly id: string;
  readonly assessment_id: string;
  readonly control_id: string;
  readonly name: string;
  readonly description?: string;
  readonly implementation_status: CompensatingControlStatus;
  readonly supplier_actions?: string;
  readonly oem_actions?: string;
  readonly residual_risk?: string;
  readonly mitigated_requirements: MitigatedRequirementInfo[];
  readonly created_at?: string;
  readonly updated_at?: string;
}

export interface CraAssessment {
  readonly id: string;
  readonly product_id: string;
  readonly product_name?: string;
  readonly classification?: CraClassification;
  readonly classification_answers: Record<string, boolean>;
  readonly product_type: CraProductType;
  readonly compliance_path: CompliancePath;
  readonly compliance_deadline?: string;
  readonly assessment_date?: string;
  readonly assessor_id?: string;
  readonly status: CraAssessmentStatus;
  readonly overall_compliance_pct: number;
  readonly support_period_end?: string;
  readonly eoss_date?: string;
  readonly notes?: string;
  readonly automotive_exception: boolean;
  readonly created_at?: string;
  readonly updated_at?: string;
  readonly requirement_statuses: CraRequirementStatusRecord[];
  readonly compensating_controls: CompensatingControl[];
}

export interface CraAssessmentListItem {
  readonly id: string;
  readonly product_id: string;
  readonly product_name?: string;
  readonly classification?: CraClassification;
  readonly product_type: CraProductType;
  readonly status: CraAssessmentStatus;
  readonly overall_compliance_pct: number;
  readonly compliance_deadline?: string;
  readonly updated_at?: string;
}

export interface CraAssessmentListResponse {
  readonly assessments: CraAssessmentListItem[];
  readonly total: number;
}

export interface CreateAssessmentRequest {
  readonly product_id: string;
  readonly product_type: CraProductType;
  readonly notes?: string;
}

export interface UpdateAssessmentRequest {
  readonly status?: CraAssessmentStatus;
  readonly product_type?: CraProductType;
  readonly support_period_end?: string;
  readonly eoss_date?: string;
  readonly notes?: string;
}

export interface ClassifyRequest {
  readonly answers: Record<string, boolean>;
  readonly automotive_exception: boolean;
}

export interface UpdateRequirementRequest {
  readonly status?: CraRequirementStatus;
  readonly owner?: string;
  readonly target_date?: string;
  readonly evidence_notes?: string;
  readonly evidence_links?: string[];
  readonly gap_description?: string;
  readonly remediation_plan?: string;
  readonly gap_severity?: GapSeverity;
  readonly residual_risk_level?: GapSeverity;
}

export interface CreateCompensatingControlRequest {
  readonly control_id: string;
  readonly name: string;
  readonly description?: string;
  readonly implementation_status?: CompensatingControlStatus;
  readonly supplier_actions?: string;
  readonly oem_actions?: string;
  readonly residual_risk?: string;
  readonly mitigated_requirement_ids?: string[];
}

export interface UpdateCompensatingControlRequest {
  readonly name?: string;
  readonly description?: string;
  readonly implementation_status?: CompensatingControlStatus;
  readonly supplier_actions?: string;
  readonly oem_actions?: string;
  readonly residual_risk?: string;
  readonly mitigated_requirement_ids?: string[];
}

export interface AutoMapResponse {
  readonly mapped_count: number;
  readonly mappings: Array<{
    readonly requirement_id: string;
    readonly status: string;
    readonly artifact_type: string;
    readonly artifact_count: number;
    readonly evidence_notes: string;
  }>;
}

export interface ClassificationQuestionsResponse {
  readonly questions: ClassificationQuestion[];
  readonly automotive_exception_question: ClassificationQuestion;
}

export interface CompensatingControlCatalogItem {
  readonly control_id: string;
  readonly name: string;
  readonly category: string;
  readonly description: string;
  readonly applicability: string;
  readonly limitations: string;
  readonly applicable_requirements: string[];
}

export type RiskLevel = 'none' | 'low' | 'medium' | 'high' | 'critical';

export interface GapRequirementItem {
  readonly requirement_status_id: string;
  readonly requirement_id: string;
  readonly requirement_name: string;
  readonly category: string;
  readonly article: string;
  readonly status: CraRequirementStatus;
  readonly is_gap: boolean;
  readonly risk_level: RiskLevel;
  readonly suggested_controls: string[];
  readonly applied_controls: Array<{
    readonly control_id: string;
    readonly name: string;
    readonly status: string;
  }>;
  readonly tara_evidence: Array<{
    readonly type: string;
    readonly count: number;
    readonly notes: string;
  }>;
  readonly owner?: string;
  readonly target_date?: string;
}

export interface GapAnalysisSummary {
  readonly total: number;
  readonly compliant: number;
  readonly gaps: number;
  readonly critical_risk: number;
  readonly high_risk: number;
  readonly with_controls: number;
}

export interface GapAnalysisResponse {
  readonly assessment_id: string;
  readonly product_id: string;
  readonly product_type: CraProductType;
  readonly classification: CraClassification;
  readonly is_legacy: boolean;
  readonly requirements: GapRequirementItem[];
  readonly summary: GapAnalysisSummary;
}
