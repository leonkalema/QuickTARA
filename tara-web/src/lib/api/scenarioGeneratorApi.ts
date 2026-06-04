/**
 * API client for auto-generating damage + threat scenarios from assets.
 *
 * Purpose: Frontend client for scenario generation endpoints
 * Depends on: $lib/api/apiClient
 * Used by: threat-scenarios page, damage-scenarios page
 */
import { apiFetch } from './apiClient';

/** Preview before generating (no DB writes) */
export interface GenerationPreview {
  readonly scope_id: string;
  readonly product_name: string;
  readonly assets_count: number;
  readonly scenarios_to_generate: number;
  readonly existing_drafts: number;
}

/** Result from damage scenario generation (Step 1) */
export interface DamageGenerationResult {
  readonly scope_id: string;
  readonly product_name: string;
  readonly assets_processed: number;
  readonly damage_scenarios_created: number;
  readonly drafts_replaced: number;
}

/** Result from threat scenario generation (Step 2) */
export interface ThreatGenerationResult {
  readonly scope_id: string;
  readonly product_name: string;
  readonly assets_processed: number;
  readonly damage_scenarios_used: number;
  readonly threat_scenarios_created: number;
  readonly drafts_replaced: number;
}

/** Threat catalog statistics */
export interface CatalogStats {
  readonly total: number;
  readonly mitre_attack_ics: number;
  readonly custom: number;
}

export const scenarioGeneratorApi = {
  /** Check if auto-generated damage drafts already exist for this product. */
  async hasAutoDamageDrafts(scopeId: string): Promise<boolean> {
    try {
      const data = await apiFetch<{ has_drafts: boolean }>(
        `/analysis/has-auto-damage-drafts/${scopeId}`,
      );
      return data.has_drafts === true;
    } catch { return false; }
  },

  /** Check if auto-generated threat drafts already exist for this product. */
  async hasAutoThreatDrafts(scopeId: string): Promise<boolean> {
    try {
      const data = await apiFetch<{ has_drafts: boolean }>(
        `/analysis/has-auto-threat-drafts/${scopeId}`,
      );
      return data.has_drafts === true;
    } catch { return false; }
  },

  /** Get threat catalog statistics (total count etc.). */
  async getCatalogStats(): Promise<CatalogStats> {
    return apiFetch<CatalogStats>('/threat/catalog/stats');
  },

  /** Preview how many damage scenarios would be generated (no DB writes). */
  async previewDamageGeneration(scopeId: string): Promise<GenerationPreview> {
    return apiFetch<GenerationPreview>(`/analysis/preview-damage-generation/${scopeId}`);
  },

  /** Step 1: Auto-generate damage scenarios from assets (CIA-based). */
  async generateDamageScenarios(scopeId: string): Promise<DamageGenerationResult> {
    return apiFetch<DamageGenerationResult>(
      `/analysis/generate-damage-scenarios/${scopeId}`,
      { method: 'POST' },
    );
  },

  /** Step 2: Auto-generate threat scenarios from existing damage scenarios. */
  async generateThreatScenarios(scopeId: string): Promise<ThreatGenerationResult> {
    return apiFetch<ThreatGenerationResult>(
      `/analysis/generate-threat-scenarios/${scopeId}`,
      { method: 'POST' },
    );
  },
};
