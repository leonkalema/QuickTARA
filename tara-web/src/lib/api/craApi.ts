/**
 * CRA Compliance API Client
 *
 * Depends on: lib/types/cra.ts, lib/config.ts, lib/stores/auth.ts
 * Used by: features/cra/*, routes/cra/*
 */
import type {
  CraAssessment,
  CraAssessmentListResponse,
  CreateAssessmentRequest,
  UpdateAssessmentRequest,
  ClassifyRequest,
  ClassificationResult,
  ProductCategory,
  UpdateRequirementRequest,
  CraRequirementStatusRecord,
  CraRequirementDefinition,
  RequirementGuidance,
  DataProfileQuestion,
  DataProfile,
  DataProfileResponse,
  CreateCompensatingControlRequest,
  UpdateCompensatingControlRequest,
  CompensatingControl,
  CompensatingControlCatalogItem,
  AutoMapResponse,
  ClassificationQuestionsResponse,
  GapAnalysisResponse,
  InventoryItem,
  InventorySummary,
  SbomListItem,
  SbomDetail,
  SbomUploadResponse,
  CraIncident,
  IncidentCreateRequest,
  IncidentUpdateRequest,
  IncidentListResponse,
  DeadlinePhase,
  EnisaExport,
} from '../types/cra';
import { API_BASE_URL } from '$lib/config';
import { browser } from '$app/environment';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

class CraApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'CraApiError';
  }
}

function getAuthHeaders(): HeadersInit {
  const auth = get(authStore);
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  const tokenFromStorage: string | null = browser ? localStorage.getItem('auth_token') : null;
  const token: string | null = auth.token ?? tokenFromStorage;
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    throw new CraApiError(`API Error: ${response.status} - ${errorText}`, response.status);
  }
  return response.json();
}

export const craApi = {
  // ── Assessments ──────────────────────────────────────────────

  async listAssessments(skip = 0, limit = 100): Promise<CraAssessmentListResponse> {
    const params = new URLSearchParams({ skip: String(skip), limit: String(limit) });
    const res = await fetch(`${API_BASE_URL}/cra/assessments?${params}`, { headers: getAuthHeaders() });
    return handleResponse<CraAssessmentListResponse>(res);
  },

  async getAssessment(id: string): Promise<CraAssessment> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/${id}`, { headers: getAuthHeaders() });
    return handleResponse<CraAssessment>(res);
  },

  async getAssessmentByProduct(productId: string): Promise<CraAssessment | null> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/product/${productId}`, { headers: getAuthHeaders() });
    if (res.status === 404) return null;
    return handleResponse<CraAssessment>(res);
  },

  async createAssessment(payload: CreateAssessmentRequest): Promise<CraAssessment> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<CraAssessment>(res);
  },

  async updateAssessment(id: string, payload: UpdateAssessmentRequest): Promise<CraAssessment> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/${id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<CraAssessment>(res);
  },

  async deleteAssessment(id: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new CraApiError(`Failed to delete assessment: ${res.status}`, res.status);
  },

  // ── Product Categories & Classification ─────────────────────

  async getProductCategories(): Promise<ProductCategory[]> {
    const res = await fetch(`${API_BASE_URL}/cra/product-categories`, { headers: getAuthHeaders() });
    return handleResponse<ProductCategory[]>(res);
  },

  async classify(assessmentId: string, payload: ClassifyRequest): Promise<ClassificationResult> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/${assessmentId}/classify`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<ClassificationResult>(res);
  },

  async getClassificationQuestions(): Promise<ClassificationQuestionsResponse> {
    const res = await fetch(`${API_BASE_URL}/cra/classification-questions`, { headers: getAuthHeaders() });
    return handleResponse<ClassificationQuestionsResponse>(res);
  },

  // ── Auto-mapping ─────────────────────────────────────────────

  async autoMap(assessmentId: string): Promise<AutoMapResponse> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/${assessmentId}/auto-map`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    return handleResponse<AutoMapResponse>(res);
  },

  // ── Requirements ─────────────────────────────────────────────

  async getRequirements(): Promise<CraRequirementDefinition[]> {
    const res = await fetch(`${API_BASE_URL}/cra/requirements`, { headers: getAuthHeaders() });
    return handleResponse<CraRequirementDefinition[]>(res);
  },

  async updateRequirement(statusId: string, payload: UpdateRequirementRequest): Promise<CraRequirementStatusRecord> {
    const res = await fetch(`${API_BASE_URL}/cra/requirements/${statusId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<CraRequirementStatusRecord>(res);
  },

  async getAllGuidance(): Promise<RequirementGuidance[]> {
    const res = await fetch(`${API_BASE_URL}/cra/guidance`, { headers: getAuthHeaders() });
    return handleResponse<RequirementGuidance[]>(res);
  },

  async getGuidance(requirementId: string): Promise<RequirementGuidance> {
    const res = await fetch(`${API_BASE_URL}/cra/guidance/${requirementId}`, { headers: getAuthHeaders() });
    return handleResponse<RequirementGuidance>(res);
  },

  // ── Data Classification ────────────────────────────────────

  async getDataClassificationQuestions(): Promise<DataProfileQuestion[]> {
    const res = await fetch(`${API_BASE_URL}/cra/data-classification-questions`, { headers: getAuthHeaders() });
    return handleResponse<DataProfileQuestion[]>(res);
  },

  async getDataProfile(assessmentId: string): Promise<DataProfileResponse> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/${assessmentId}/data-profile`, { headers: getAuthHeaders() });
    return handleResponse<DataProfileResponse>(res);
  },

  async updateDataProfile(assessmentId: string, profile: DataProfile): Promise<DataProfileResponse> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/${assessmentId}/data-profile`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(profile),
    });
    return handleResponse<DataProfileResponse>(res);
  },

  // ── Compensating Controls ────────────────────────────────────

  async getCompensatingControls(assessmentId: string): Promise<CompensatingControl[]> {
    const res = await fetch(`${API_BASE_URL}/cra/compensating-controls/${assessmentId}`, { headers: getAuthHeaders() });
    return handleResponse<CompensatingControl[]>(res);
  },

  async createCompensatingControl(assessmentId: string, payload: CreateCompensatingControlRequest): Promise<CompensatingControl> {
    const params = new URLSearchParams({ assessment_id: assessmentId });
    const res = await fetch(`${API_BASE_URL}/cra/compensating-controls?${params}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<CompensatingControl>(res);
  },

  async updateCompensatingControl(controlId: string, payload: UpdateCompensatingControlRequest): Promise<CompensatingControl> {
    const res = await fetch(`${API_BASE_URL}/cra/compensating-controls/${controlId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<CompensatingControl>(res);
  },

  async deleteCompensatingControl(controlId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/cra/compensating-controls/${controlId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new CraApiError(errData.detail || 'Failed to delete control', res.status);
    }
  },

  // ── Catalog ──────────────────────────────────────────────────

  async getCompensatingControlsCatalog(): Promise<CompensatingControlCatalogItem[]> {
    const res = await fetch(`${API_BASE_URL}/cra/compensating-controls-catalog`, { headers: getAuthHeaders() });
    return handleResponse<CompensatingControlCatalogItem[]>(res);
  },

  // ── Gap Analysis ──────────────────────────────────────────────────

  async getGapAnalysis(assessmentId: string): Promise<GapAnalysisResponse> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/${assessmentId}/gap-analysis`, { headers: getAuthHeaders() });
    return handleResponse<GapAnalysisResponse>(res);
  },

  // ── Inventory ──────────────────────────────────────────────────

  async getInventory(assessmentId: string): Promise<InventoryItem[]> {
    const res = await fetch(`${API_BASE_URL}/cra/inventory/${assessmentId}`, { headers: getAuthHeaders() });
    return handleResponse<InventoryItem[]>(res);
  },

  async getInventorySummary(assessmentId: string): Promise<InventorySummary> {
    const res = await fetch(`${API_BASE_URL}/cra/inventory/${assessmentId}/summary`, { headers: getAuthHeaders() });
    return handleResponse<InventorySummary>(res);
  },

  async createInventoryItem(data: {
    assessment_id: string;
    sku: string;
    firmware_version?: string;
    units_in_stock?: number;
    units_in_field?: number;
    oem_customer?: string;
    target_market?: string;
    last_production_date?: string;
    notes?: string;
  }): Promise<InventoryItem> {
    const res = await fetch(`${API_BASE_URL}/cra/inventory`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<InventoryItem>(res);
  },

  async updateInventoryItem(itemId: string, data: Partial<{
    sku: string;
    firmware_version: string;
    units_in_stock: number;
    units_in_field: number;
    oem_customer: string;
    target_market: string;
    last_production_date: string;
    notes: string;
  }>): Promise<InventoryItem> {
    const res = await fetch(`${API_BASE_URL}/cra/inventory/${itemId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<InventoryItem>(res);
  },

  async deleteInventoryItem(itemId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/cra/inventory/${itemId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new CraApiError(errData.detail || 'Failed to delete inventory item', res.status);
    }
  },

  // ── SBOM (CRA Art. 13(6)) ─────────────────────────────────

  async listSboms(assessmentId: string): Promise<SbomListItem[]> {
    const res = await fetch(`${API_BASE_URL}/cra/assessments/${assessmentId}/sboms`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<SbomListItem[]>(res);
  },

  async getSbom(sbomId: string): Promise<SbomDetail> {
    const res = await fetch(`${API_BASE_URL}/cra/sboms/${sbomId}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<SbomDetail>(res);
  },

  async uploadSbom(assessmentId: string, file: File): Promise<SbomUploadResponse> {
    const auth = get(authStore);
    const tokenFromStorage: string | null = browser ? localStorage.getItem('auth_token') : null;
    const token: string | null = auth.token ?? tokenFromStorage;
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const form = new FormData();
    form.append('file', file);

    const res = await fetch(`${API_BASE_URL}/cra/assessments/${assessmentId}/sboms`, {
      method: 'POST',
      headers,
      body: form,
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      const detail = typeof errData.detail === 'string'
        ? errData.detail
        : Array.isArray(errData.detail?.errors)
          ? errData.detail.errors.join('; ')
          : 'Failed to upload SBOM';
      throw new CraApiError(detail, res.status);
    }
    return res.json();
  },

  async deleteSbom(sbomId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/cra/sboms/${sbomId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new CraApiError(errData.detail || 'Failed to delete SBOM', res.status);
    }
  },

  // ── Incidents (CRA Art. 14) ────────────────────────────────

  async listIncidents(filters: {
    assessmentId?: string;
    incidentStatus?: string;
  } = {}): Promise<IncidentListResponse> {
    const params = new URLSearchParams();
    if (filters.assessmentId) params.set('assessment_id', filters.assessmentId);
    if (filters.incidentStatus) params.set('incident_status', filters.incidentStatus);
    const qs = params.toString();
    const res = await fetch(`${API_BASE_URL}/cra/incidents${qs ? `?${qs}` : ''}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<IncidentListResponse>(res);
  },

  async getIncident(incidentId: string): Promise<CraIncident> {
    const res = await fetch(`${API_BASE_URL}/cra/incidents/${incidentId}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<CraIncident>(res);
  },

  async createIncident(payload: IncidentCreateRequest): Promise<CraIncident> {
    const res = await fetch(`${API_BASE_URL}/cra/incidents`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<CraIncident>(res);
  },

  async updateIncident(incidentId: string, payload: IncidentUpdateRequest): Promise<CraIncident> {
    const res = await fetch(`${API_BASE_URL}/cra/incidents/${incidentId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse<CraIncident>(res);
  },

  async submitIncidentPhase(incidentId: string, phase: DeadlinePhase): Promise<CraIncident> {
    const res = await fetch(`${API_BASE_URL}/cra/incidents/${incidentId}/submit`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ phase }),
    });
    return handleResponse<CraIncident>(res);
  },

  async getEnisaExport(incidentId: string, phase: DeadlinePhase): Promise<EnisaExport> {
    const params = new URLSearchParams({ phase });
    const res = await fetch(
      `${API_BASE_URL}/cra/incidents/${incidentId}/enisa-export?${params}`,
      { headers: getAuthHeaders() },
    );
    return handleResponse<EnisaExport>(res);
  },

  async deleteIncident(incidentId: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/cra/incidents/${incidentId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new CraApiError(errData.detail || 'Failed to delete incident', res.status);
    }
  },
};
