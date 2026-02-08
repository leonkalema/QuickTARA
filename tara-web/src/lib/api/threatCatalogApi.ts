import { API_BASE_URL } from '$lib/config';

export interface ThreatCatalogItem {
	id: string;
	title: string;
	description: string;
	stride_category: string;
	applicable_component_types: string[];
	applicable_trust_zones: string[];
	attack_vectors: string[];
	typical_likelihood: number;
	typical_severity: number;
	mitigation_strategies: MitigationStrategy[];
	cwe_ids: string[];
	capec_ids: string[];
	examples: string[];
	source: string;
	source_version: string | null;
	mitre_technique_id: string | null;
	mitre_tactic: string | null;
	automotive_relevance: number;
	automotive_context: string | null;
	is_user_modified: boolean;
}

export interface MitigationStrategy {
	title: string;
	description: string;
	effectiveness: number;
	implementation_complexity: number;
	references: string[];
}

export interface ThreatCatalogListResponse {
	catalog_items: ThreatCatalogItem[];
	total: number;
}

class ThreatCatalogApiError extends Error {
	constructor(message: string, public status?: number) {
		super(message);
		this.name = 'ThreatCatalogApiError';
	}
}

export const threatCatalogApi = {
	async getItems(params?: {
		skip?: number;
		limit?: number;
		stride_category?: string;
		component_type?: string;
		trust_zone?: string;
	}): Promise<ThreatCatalogListResponse> {
		const searchParams = new URLSearchParams();
		if (params?.skip) searchParams.set('skip', String(params.skip));
		if (params?.limit) searchParams.set('limit', String(params.limit));
		if (params?.stride_category) searchParams.set('stride_category', params.stride_category);
		if (params?.component_type) searchParams.set('component_type', params.component_type);
		if (params?.trust_zone) searchParams.set('trust_zone', params.trust_zone);

		const query = searchParams.toString();
		const url = `${API_BASE_URL}/threat/catalog${query ? `?${query}` : ''}`;
		const resp = await fetch(url);
		if (!resp.ok) throw new ThreatCatalogApiError(`HTTP ${resp.status}`, resp.status);
		return resp.json();
	},

	async getItem(id: string): Promise<ThreatCatalogItem> {
		const resp = await fetch(`${API_BASE_URL}/threat/catalog/${id}`);
		if (!resp.ok) throw new ThreatCatalogApiError(`HTTP ${resp.status}`, resp.status);
		return resp.json();
	}
};
