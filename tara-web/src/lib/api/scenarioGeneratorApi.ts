/**
 * API client for auto-generating damage + threat scenarios from assets.
 *
 * Purpose: Frontend client for POST /api/analysis/generate-scenarios/{scope_id}
 * Depends on: $lib/config
 * Used by: threat-scenarios page, assets page (generate button)
 */
import { API_BASE_URL } from '$lib/config';

/** Summary returned after auto-generation */
export interface GenerationResult {
  readonly scope_id: string;
  readonly product_name: string;
  readonly assets_processed: number;
  readonly damage_scenarios_created: number;
  readonly threat_scenarios_created: number;
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
   * Auto-generate damage and threat scenarios for all assets in a product.
   * @param scopeId - The product scope ID
   */
  async generateScenarios(scopeId: string): Promise<GenerationResult> {
    const response = await fetch(
      `${API_BASE_URL}/analysis/generate-scenarios/${scopeId}`,
      { method: 'POST' },
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new ScenarioGeneratorApiError(
        `Scenario generation failed: ${errorText}`,
        response.status,
      );
    }

    return response.json();
  },
};
