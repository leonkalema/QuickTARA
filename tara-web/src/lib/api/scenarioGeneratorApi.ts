/**
 * API client for auto-generating damage + threat scenarios from assets.
 *
 * Purpose: Frontend client for POST /api/analysis/generate-scenarios/{scope_id}
 * Depends on: $lib/config
 * Used by: threat-scenarios page, assets page (generate button)
 */
import { API_BASE_URL } from '$lib/config';

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

class ScenarioGeneratorApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = 'ScenarioGeneratorApiError';
  }
}

export const scenarioGeneratorApi = {
  /**
   * Preview how many scenarios would be generated (no DB writes).
   */
  async previewDamageGeneration(scopeId: string): Promise<GenerationPreview> {
    const response = await fetch(
      `${API_BASE_URL}/analysis/preview-damage-generation/${scopeId}`,
    );
    if (!response.ok) {
      const errorText = await response.text();
      throw new ScenarioGeneratorApiError(`Preview failed: ${errorText}`, response.status);
    }
    return response.json();
  },

  /**
   * Step 1: Auto-generate damage scenarios from assets (CIA-based).
   * Called from the Damage Scenarios page.
   */
  async generateDamageScenarios(scopeId: string): Promise<DamageGenerationResult> {
    const response = await fetch(
      `${API_BASE_URL}/analysis/generate-damage-scenarios/${scopeId}`,
      { method: 'POST' },
    );
    if (!response.ok) {
      const errorText = await response.text();
      throw new ScenarioGeneratorApiError(
        `Damage scenario generation failed: ${errorText}`,
        response.status,
      );
    }
    return response.json();
  },

  /**
   * Step 2: Auto-generate threat scenarios from existing damage scenarios.
   * Called from the Threat Scenarios page. Requires damage scenarios to exist.
   */
  async generateThreatScenarios(scopeId: string): Promise<ThreatGenerationResult> {
    const response = await fetch(
      `${API_BASE_URL}/analysis/generate-threat-scenarios/${scopeId}`,
      { method: 'POST' },
    );
    if (!response.ok) {
      const errorText = await response.text();
      throw new ScenarioGeneratorApiError(
        `Threat scenario generation failed: ${errorText}`,
        response.status,
      );
    }
    return response.json();
  },
};
