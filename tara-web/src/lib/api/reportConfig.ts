import { API_BASE_URL } from '$lib/config';

export type ReportAudience = 'internal' | 'external' | 'auditor';
export type ReportDetailLevel = 'full' | 'summary';
export type ReportClassification = 'public' | 'internal' | 'confidential';

export type SectionKey =
	| 'document_control'
	| 'executive_summary'
	| 'scope_and_assumptions'
	| 'methodology'
	| 'assessment_status'
	| 'iso_compliance'
	| 'cra_compliance'
	| 'asset_inventory'
	| 'damage_scenarios'
	| 'threat_scenarios'
	| 'attack_paths'
	| 'risk_summary'
	| 'risk_register'
	| 'treatment_summary'
	| 'cybersecurity_goals'
	| 'open_issues'
	| 'traceability';

export interface ReportMetadata {
	author: string | null;
	approver: string | null;
	reference: string | null;
}

export interface ReportConfig {
	audience: ReportAudience;
	detail_level: ReportDetailLevel;
	classification: ReportClassification;
	sections: Record<SectionKey, boolean>;
	metadata: ReportMetadata;
}

export interface TemplateSummary {
	template_id: string;
	name: string;
	is_builtin: boolean;
}

interface TemplateListResponse {
	templates: TemplateSummary[];
}

const SECTION_KEYS: SectionKey[] = [
	'document_control',
	'executive_summary',
	'iso_compliance',
	'cra_compliance',
	'risk_summary',
	'asset_inventory',
	'damage_scenarios',
	'threat_scenarios',
	'attack_paths',
	'cybersecurity_goals',
	'traceability'
];

/**
 * Per-audience section visibility.
 *
 * internal  — Full working document. All sections, full detail.
 *
 * external  — For customers, suppliers, or public disclosure.
 *             NEVER include: attack paths (attacker roadmap), traceability
 *             (exposes internal architecture decisions), CRA compliance gaps
 *             (unresolved regulatory exposure), or damage/threat scenario
 *             detail (sensitive IP). Include: executive summary, high-level
 *             asset overview, ISO compliance statement, risk decisions only.
 *
 * auditor   — For ISO 21434 / type-approval assessors verifying process
 *             compliance. Needs traceability and clause mapping to check
 *             work products. Excludes attack paths (not needed for audit)
 *             and CRA gaps (separate regulatory track).
 */
const AUDIENCE_SECTIONS: Record<ReportAudience, Record<SectionKey, boolean>> = {
	internal: {
		document_control:      true,
		executive_summary:     true,
		scope_and_assumptions: true,
		methodology:           true,
		assessment_status:     true,
		iso_compliance:        true,
		cra_compliance:        true,
		asset_inventory:       true,
		damage_scenarios:      true,
		threat_scenarios:      true,
		attack_paths:          true,
		risk_summary:          true,
		risk_register:         true,
		treatment_summary:     true,
		cybersecurity_goals:   true,
		open_issues:           true,
		traceability:          true,
	},
	external: {
		document_control:      true,
		executive_summary:     true,
		scope_and_assumptions: true,
		methodology:           true,
		assessment_status:     true,
		iso_compliance:        true,
		cra_compliance:        false,  // internal regulatory gaps
		asset_inventory:       true,
		damage_scenarios:      false,  // sensitive IP
		threat_scenarios:      false,  // attack roadmap
		attack_paths:          false,  // attacker guide
		risk_summary:          true,
		risk_register:         true,
		treatment_summary:     true,
		cybersecurity_goals:   true,
		open_issues:           true,
		traceability:          false,  // internal architecture
	},
	auditor: {
		document_control:      true,
		executive_summary:     true,
		scope_and_assumptions: true,
		methodology:           true,
		assessment_status:     true,
		iso_compliance:        true,
		cra_compliance:        false,  // separate regulatory track
		asset_inventory:       true,
		damage_scenarios:      true,
		threat_scenarios:      true,
		attack_paths:          false,  // not needed for process audit
		risk_summary:          true,
		risk_register:         true,
		treatment_summary:     true,
		cybersecurity_goals:   true,
		open_issues:           true,
		traceability:          true,
	},
};

const AUDIENCE_DEFAULTS: Record<ReportAudience, { detail: ReportDetailLevel; classification: ReportClassification }> = {
	internal: { detail: 'full', classification: 'internal' },
	external: { detail: 'summary', classification: 'confidential' },
	auditor: { detail: 'full', classification: 'confidential' }
};

function authHeaders(): Record<string, string> {
	return {
		'Content-Type': 'application/json',
		Authorization: `Bearer ${localStorage.getItem('auth_token') ?? ''}`
	};
}

/** Build a default config for an audience, mirroring the backend presets. */
export function defaultConfigForAudience(audience: ReportAudience): ReportConfig {
	const sections = { ...AUDIENCE_SECTIONS[audience] };
	const meta = AUDIENCE_DEFAULTS[audience];
	return {
		audience,
		detail_level: meta.detail,
		classification: meta.classification,
		sections,
		metadata: { author: null, approver: null, reference: null }
	};
}

/** Generate a PDF for a scope from a config; returns the response blob. */
export async function generatePdf(scopeId: string, config: ReportConfig): Promise<Blob> {
	const response = await fetch(`${API_BASE_URL}/reports/${scopeId}/pdf`, {
		method: 'POST',
		headers: authHeaders(),
		body: JSON.stringify(config)
	});
	if (!response.ok) {
		const detail = await response.text().catch(() => response.statusText);
		throw new Error(detail);
	}
	return response.blob();
}

export async function listTemplates(): Promise<TemplateSummary[]> {
	const response = await fetch(`${API_BASE_URL}/reports/templates`, {
		headers: authHeaders()
	});
	if (!response.ok) {
		throw new Error(`Failed to load templates (${response.status})`);
	}
	const data: TemplateListResponse = await response.json();
	return data.templates;
}

export async function createTemplate(name: string, config: ReportConfig): Promise<TemplateSummary> {
	const response = await fetch(`${API_BASE_URL}/reports/templates`, {
		method: 'POST',
		headers: authHeaders(),
		body: JSON.stringify({ name, config })
	});
	if (!response.ok) {
		const detail = await response.text().catch(() => response.statusText);
		throw new Error(detail);
	}
	return response.json();
}

export async function deleteTemplate(templateId: string): Promise<void> {
	const response = await fetch(`${API_BASE_URL}/reports/templates/${encodeURIComponent(templateId)}`, {
		method: 'DELETE',
		headers: authHeaders()
	});
	if (!response.ok && response.status !== 204) {
		const detail = await response.text().catch(() => response.statusText);
		throw new Error(detail);
	}
}
