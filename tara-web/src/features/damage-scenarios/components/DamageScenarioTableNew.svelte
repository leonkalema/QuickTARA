<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { damageScenarioApi } from '../../../lib/api/damageScenarioApi';
  import { notifications } from '../../../lib/stores/notificationStore';
  import { selectedProduct } from '../../../lib/stores/productStore';
  import { 
    DamageCategory,
    ImpactType,
    SeverityLevel,
    type DamageScenario, 
    type CreateDamageScenarioRequest
  } from '../../../lib/types/damageScenario';
  import type { Asset } from '../../../lib/types/asset';

  export let damageScenarios: DamageScenario[] = [];
  export let assets: Asset[] = [];
  
  const dispatch = createEventDispatcher();

  // Form state
  let isAddingNew = false;
  let newScenario = {
    name: '',
    description: '',
    damage_category: DamageCategory.SAFETY,
    impact_type: ImpactType.DIRECT,
    severity: SeverityLevel.LOW,
    confidentiality_impact: false,
    integrity_impact: false,
    availability_impact: false,
    primary_component_id: '',
    scope_id: $selectedProduct?.scope_id || '',
    version: '1.0',
    revision_notes: 'Initial version'
  };

  // SFOP impact ratings
  let safety_impact = '';
  let financial_impact = '';
  let operational_impact = '';
  let privacy_impact = '';

  // Update scope when product changes
  $: if ($selectedProduct?.scope_id) {
    newScenario.scope_id = $selectedProduct.scope_id;
  }

  function resetForm() {
    newScenario = {
      name: '',
      description: '',
      damage_category: DamageCategory.SAFETY,
      impact_type: ImpactType.DIRECT,
      severity: SeverityLevel.LOW,
      confidentiality_impact: false,
      integrity_impact: false,
      availability_impact: false,
      primary_component_id: '',
      scope_id: $selectedProduct?.scope_id || '',
      version: '1.0',
      revision_notes: 'Initial version'
    };
    
    safety_impact = '';
    financial_impact = '';
    operational_impact = '';
    privacy_impact = '';
    isAddingNew = false;
  }

  async function addNewScenario() {
    if (!newScenario.name.trim()) {
      notifications.show('Please enter a scenario name', 'error');
      return;
    }

    if (!$selectedProduct?.scope_id) {
      notifications.show('Please select a product first', 'error');
      return;
    }

    try {
      const scenarioData: CreateDamageScenarioRequest = {
        ...newScenario,
        scope_id: $selectedProduct.scope_id,
        impact_rating: {
          safety: safety_impact || 'negligible',
          financial: financial_impact || 'negligible',
          operational: operational_impact || 'negligible',
          privacy: privacy_impact || 'negligible'
        }
      };

      const response = await damageScenarioApi.createDamageScenario(scenarioData);
      damageScenarios = [...damageScenarios, response];
      resetForm();
      notifications.show('Damage scenario created successfully', 'success');
      dispatch('scenarioAdded', response);
    } catch (error) {
      console.error('Error creating damage scenario:', error);
      notifications.show('Failed to create damage scenario', 'error');
    }
  }

  function getOverallSfopRating(scenario: any): string {
    const impacts = [
      scenario.safety_impact,
      scenario.financial_impact,
      scenario.operational_impact,
      scenario.privacy_impact
    ].filter(impact => impact && impact !== 'negligible');

    if (impacts.length === 0) return 'negligible';

    const severityOrder = ['negligible', 'moderate', 'major', 'severe'];
    let maxSeverity = 0;
    
    impacts.forEach(impact => {
      const index = severityOrder.indexOf(impact);
      if (index > maxSeverity) {
        maxSeverity = index;
      }
    });

    return severityOrder[maxSeverity];
  }

  function getSfopBadgeClass(impact: string): string {
    switch (impact) {
      case 'severe': return 'bg-red-100 text-red-800';
      case 'major': return 'bg-orange-100 text-orange-800';
      case 'moderate': return 'bg-yellow-100 text-yellow-800';
      case 'negligible': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  function getCIABadgeClass(isActive: boolean): string {
    return isActive 
      ? 'bg-red-100 text-red-800 border border-red-200' 
      : 'bg-gray-100 text-gray-500 border border-gray-200';
  }

  function getAssetName(assetId: string): string {
    const asset = assets.find(a => a.asset_id === assetId);
    return asset?.name || 'Unknown Asset';
  }

  async function deleteDamageScenario(scenario: DamageScenario) {
    if (!confirm(`Are you sure you want to delete "${scenario.name}"?`)) {
      return;
    }

    try {
      await damageScenarioApi.deleteDamageScenario(scenario.scenario_id);
      damageScenarios = damageScenarios.filter(s => s.scenario_id !== scenario.scenario_id);
      notifications.show('Damage scenario deleted successfully', 'success');
      dispatch('scenarioDeleted', scenario.scenario_id);
    } catch (error) {
      console.error('Error deleting damage scenario:', error);
      notifications.show('Failed to delete damage scenario', 'error');
    }
  }
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h3 class="text-lg font-medium text-gray-900">Damage Scenarios</h3>
    <button
      on:click={() => isAddingNew = !isAddingNew}
      class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
    >
      {isAddingNew ? 'Cancel' : 'Add Scenario'}
    </button>
  </div>

  {#if isAddingNew}
    <form on:submit|preventDefault={addNewScenario} class="bg-gray-50 p-6 rounded-lg">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Scenario Name *</label>
          <input
            bind:value={newScenario.name}
            placeholder="Enter scenario name"
            class="w-full px-3 py-2 border border-gray-300 rounded-md"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Primary Asset</label>
          <select
            bind:value={newScenario.primary_component_id}
            class="w-full px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">Select an asset...</option>
            {#each assets as asset}
              <option value={asset.asset_id}>{asset.name}</option>
            {/each}
          </select>
        </div>
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          bind:value={newScenario.description}
          placeholder="Describe the damage scenario"
          class="w-full px-3 py-2 border border-gray-300 rounded-md"
          rows="3"
        ></textarea>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Safety Impact</label>
          <select bind:value={safety_impact} class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option value="">Select...</option>
            <option value="negligible">Negligible</option>
            <option value="moderate">Moderate</option>
            <option value="major">Major</option>
            <option value="severe">Severe</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Financial Impact</label>
          <select bind:value={financial_impact} class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option value="">Select...</option>
            <option value="negligible">Negligible</option>
            <option value="moderate">Moderate</option>
            <option value="major">Major</option>
            <option value="severe">Severe</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Operational Impact</label>
          <select bind:value={operational_impact} class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option value="">Select...</option>
            <option value="negligible">Negligible</option>
            <option value="moderate">Moderate</option>
            <option value="major">Major</option>
            <option value="severe">Severe</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Privacy Impact</label>
          <select bind:value={privacy_impact} class="w-full px-3 py-2 border border-gray-300 rounded-md">
            <option value="">Select...</option>
            <option value="negligible">Negligible</option>
            <option value="moderate">Moderate</option>
            <option value="major">Major</option>
            <option value="severe">Severe</option>
          </select>
        </div>
      </div>

      <div class="flex justify-end space-x-3">
        <button
          type="button"
          on:click={resetForm}
          class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Create Scenario
        </button>
      </div>
    </form>
  {/if}

  {#if damageScenarios.length === 0}
    <div class="text-center py-8 text-gray-500">
      No damage scenarios created yet.
    </div>
  {:else}
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">CIA</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SFOP Impact</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Overall</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          {#each damageScenarios as scenario}
            <tr>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{scenario.name}</div>
                {#if scenario.description}
                  <div class="text-sm text-gray-500 max-w-xs break-words">{scenario.description}</div>
                {/if}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {scenario.primary_component_id ? getAssetName(scenario.primary_component_id) : 'No asset'}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex space-x-1">
                  <span class="px-2 py-1 text-xs rounded {getCIABadgeClass(scenario.confidentiality_impact)}">C</span>
                  <span class="px-2 py-1 text-xs rounded {getCIABadgeClass(scenario.integrity_impact)}">I</span>
                  <span class="px-2 py-1 text-xs rounded {getCIABadgeClass(scenario.availability_impact)}">A</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex space-x-1">
                  {#if scenario.safety_impact}
                    <span class="px-2 py-1 text-xs rounded {getSfopBadgeClass(scenario.safety_impact)}">S</span>
                  {/if}
                  {#if scenario.financial_impact}
                    <span class="px-2 py-1 text-xs rounded {getSfopBadgeClass(scenario.financial_impact)}">F</span>
                  {/if}
                  {#if scenario.operational_impact}
                    <span class="px-2 py-1 text-xs rounded {getSfopBadgeClass(scenario.operational_impact)}">O</span>
                  {/if}
                  {#if scenario.privacy_impact}
                    <span class="px-2 py-1 text-xs rounded {getSfopBadgeClass(scenario.privacy_impact)}">P</span>
                  {/if}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs rounded {getSfopBadgeClass(getOverallSfopRating(scenario))}">
                  {getOverallSfopRating(scenario)}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  on:click={() => deleteDamageScenario(scenario)}
                  class="text-red-600 hover:text-red-900"
                >
                  Delete
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>
