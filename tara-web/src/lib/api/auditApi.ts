import { API_BASE_URL } from '$lib/config';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

function getAuthHeaders(contentType?: string): HeadersInit {
  const auth = get(authStore);
  const headers: Record<string, string> = {};
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`;
  if (contentType) headers['Content-Type'] = contentType;
  return headers;
}

/** Audit log entry */
export interface AuditLogEntry {
  id: number;
  artifact_type: string;
  artifact_id: string;
  scope_id: string | null;
  action: string;
  performed_by: string;
  performed_at: string;
  field_changed: string | null;
  old_value: string | null;
  new_value: string | null;
  change_summary: string | null;
}

export interface AuditLogListResponse {
  logs: AuditLogEntry[];
  total: number;
}

/** Approval workflow */
export interface ApprovalWorkflow {
  id: number;
  artifact_type: string;
  artifact_id: string;
  scope_id: string | null;
  current_state: string;
  created_by: string;
  assigned_reviewer: string | null;
  reviewed_by: string | null;
  approved_by: string | null;
  released_by: string | null;
  review_notes: string | null;
  approval_notes: string | null;
  rejection_reason: string | null;
  created_at: string;
  updated_at: string;
}

/** Sign-off record */
export interface Signoff {
  id: number;
  workflow_id: number;
  signer: string;
  signer_role: string;
  action: string;
  comment: string | null;
  signed_at: string;
}

/** TARA snapshot */
export interface TaraSnapshot {
  snapshot_id: string;
  scope_id: string;
  version: number;
  version_label: string | null;
  asset_count: number;
  damage_scenario_count: number;
  threat_scenario_count: number;
  attack_path_count: number;
  risk_treatment_count: number;
  workflow_state: string | null;
  created_by: string;
  created_at: string;
  notes: string | null;
}

export interface TaraSnapshotDetail extends TaraSnapshot {
  snapshot_data: Record<string, unknown>;
}

/** Evidence attachment */
export interface EvidenceAttachment {
  evidence_id: string;
  artifact_type: string;
  artifact_id: string;
  scope_id: string | null;
  filename: string;
  file_size: number | null;
  mime_type: string | null;
  evidence_type: string;
  title: string;
  description: string | null;
  uploaded_by: string;
  uploaded_at: string;
}

export const auditApi = {
  /** Get audit logs with optional filters */
  async getLogs(params: {
    scope_id?: string;
    artifact_type?: string;
    artifact_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<AuditLogListResponse> {
    const query = new URLSearchParams();
    if (params.scope_id) query.set('scope_id', params.scope_id);
    if (params.artifact_type) query.set('artifact_type', params.artifact_type);
    if (params.artifact_id) query.set('artifact_id', params.artifact_id);
    if (params.limit) query.set('limit', String(params.limit));
    if (params.offset) query.set('offset', String(params.offset));
    const res = await fetch(`${API_BASE_URL}/audit/logs?${query}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to fetch audit logs: ${res.statusText}`);
    return res.json();
  },

  /** Create or get workflow for an artifact (user identity from JWT) */
  async createWorkflow(
    artifactType: string, artifactId: string, scopeId?: string
  ): Promise<ApprovalWorkflow> {
    const query = new URLSearchParams();
    if (scopeId) query.set('scope_id', scopeId);
    const qs = query.toString() ? `?${query}` : '';
    const res = await fetch(`${API_BASE_URL}/audit/workflows/${artifactType}/${artifactId}${qs}`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to create workflow');
    }
    return res.json();
  },

  /** Get workflow for an artifact (returns null if none exists) */
  async getWorkflow(artifactType: string, artifactId: string): Promise<ApprovalWorkflow | null> {
    const res = await fetch(`${API_BASE_URL}/audit/workflows/${artifactType}/${artifactId}`, {
      headers: getAuthHeaders(),
    });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`Failed to fetch workflow: ${res.statusText}`);
    return res.json();
  },

  /** Transition workflow state (user identity from JWT) */
  async transitionWorkflow(
    artifactType: string, artifactId: string,
    targetState: string, notes?: string
  ): Promise<ApprovalWorkflow> {
    const res = await fetch(
      `${API_BASE_URL}/audit/workflows/${artifactType}/${artifactId}/transition`,
      {
        method: 'POST',
        headers: getAuthHeaders('application/json'),
        body: JSON.stringify({ target_state: targetState, notes }),
      }
    );
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Transition failed');
    }
    return res.json();
  },

  /** List workflows for a product scope */
  async listWorkflowsByScope(scopeId: string, state?: string): Promise<ApprovalWorkflow[]> {
    const query = state ? `?state=${state}` : '';
    const res = await fetch(`${API_BASE_URL}/audit/workflows/scope/${scopeId}${query}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to fetch workflows: ${res.statusText}`);
    return res.json();
  },

  /** Add a sign-off (signer identity from JWT) */
  async addSignoff(
    workflowId: number, signerRole: string, action: string, comment?: string
  ): Promise<Signoff> {
    const res = await fetch(`${API_BASE_URL}/audit/signoffs/${workflowId}`, {
      method: 'POST',
      headers: getAuthHeaders('application/json'),
      body: JSON.stringify({ signer_role: signerRole, action, comment }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Failed to add signoff');
    }
    return res.json();
  },

  /** List sign-offs for a workflow */
  async getSignoffs(workflowId: number): Promise<Signoff[]> {
    const res = await fetch(`${API_BASE_URL}/audit/signoffs/${workflowId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to fetch signoffs: ${res.statusText}`);
    return res.json();
  },

  /** Create a TARA snapshot */
  async createSnapshot(
    scopeId: string, createdBy: string, versionLabel?: string, notes?: string
  ): Promise<TaraSnapshot> {
    const res = await fetch(`${API_BASE_URL}/audit/snapshots`, {
      method: 'POST',
      headers: getAuthHeaders('application/json'),
      body: JSON.stringify({ scope_id: scopeId, created_by: createdBy, version_label: versionLabel, notes }),
    });
    if (!res.ok) throw new Error(`Failed to create snapshot: ${res.statusText}`);
    return res.json();
  },

  /** List snapshots for a product */
  async listSnapshots(scopeId: string): Promise<TaraSnapshot[]> {
    const res = await fetch(`${API_BASE_URL}/audit/snapshots/scope/${scopeId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to fetch snapshots: ${res.statusText}`);
    return res.json();
  },

  /** Get snapshot detail with full data */
  async getSnapshotDetail(snapshotId: string): Promise<TaraSnapshotDetail> {
    const res = await fetch(`${API_BASE_URL}/audit/snapshots/${snapshotId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to fetch snapshot: ${res.statusText}`);
    return res.json();
  },

  /** Upload evidence */
  async uploadEvidence(
    artifactType: string, artifactId: string, evidenceType: string,
    title: string, uploadedBy: string, file: File,
    scopeId?: string, description?: string
  ): Promise<EvidenceAttachment> {
    const form = new FormData();
    form.append('artifact_type', artifactType);
    form.append('artifact_id', artifactId);
    form.append('evidence_type', evidenceType);
    form.append('title', title);
    form.append('uploaded_by', uploadedBy);
    form.append('file', file);
    if (scopeId) form.append('scope_id', scopeId);
    if (description) form.append('description', description);
    const auth = get(authStore);
    const evidenceHeaders: Record<string, string> = {};
    if (auth.token) evidenceHeaders['Authorization'] = `Bearer ${auth.token}`;
    const res = await fetch(`${API_BASE_URL}/audit/evidence`, {
      method: 'POST', body: form, headers: evidenceHeaders,
    });
    if (!res.ok) throw new Error(`Failed to upload evidence: ${res.statusText}`);
    return res.json();
  },

  /** List evidence for an artifact */
  async listEvidence(artifactType: string, artifactId: string): Promise<EvidenceAttachment[]> {
    const res = await fetch(`${API_BASE_URL}/audit/evidence/${artifactType}/${artifactId}`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error(`Failed to fetch evidence: ${res.statusText}`);
    return res.json();
  },

  /** Delete evidence */
  async deleteEvidence(evidenceId: string, deletedBy: string): Promise<void> {
    const res = await fetch(
      `${API_BASE_URL}/audit/evidence/${evidenceId}?deleted_by=${deletedBy}`,
      { method: 'DELETE', headers: getAuthHeaders() }
    );
    if (!res.ok) throw new Error(`Failed to delete evidence: ${res.statusText}`);
  },
};
