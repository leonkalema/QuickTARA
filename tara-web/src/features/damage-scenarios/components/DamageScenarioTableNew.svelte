<script lang="ts">
  import { notifications } from '$lib/stores/notificationStore';
  import type { CreateDamageScenarioRequest, DamageScenario } from '$lib/types/damageScenario';
  import { damageScenarioApi } from '$lib/api/damageScenarioApi';
  import { selectedProduct } from '$lib/stores/productStore';
  import { onMount, createEventDispatcher } from 'svelte';
  import { getOverallSfopRating, getSfopBadgeClass, getCIABadgeClass, getSfopImpacts } from '$lib/utils/sfopUtils';
  import ConfirmDialog from '../../../components/ConfirmDialog.svelte';

  export let damageScenarios: DamageScenario[] = [];
  export let assets: any[] = [];

  const dispatch = createEventDispatcher();

  // Form state
  let isAddingNew = false;
  let newScenario = {
    name: '',
    description: '',
    damage_category: 'Safety',
    impact_type: 'Direct',
    severity: 'Low',
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
  
  // Delete confirmation dialog
  let showDeleteDialog = false;
  let scenarioToDelete: DamageScenario | null = null;
  let isDeleting = false;

  // Update scope when product changes
  $: if ($selectedProduct?.scope_id) {
    newScenario.scope_id = $selectedProduct.scope_id;
  }

  function resetForm() {
    newScenario = {
      name: '',
      description: '',
      damage_category: 'Safety',
      impact_type: 'Direct',
      severity: 'Low',
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

    if (!newScenario.confidentiality_impact && !newScenario.integrity_impact && !newScenario.availability_impact) {
      notifications.show('Please select at least one CIA security property', 'error');
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

  function getAssetName(assetId: string): string {
    const asset = assets.find(a => a.asset_id === assetId);
    return asset?.name || 'Unknown Asset';
  }

  function confirmDelete(scenario: DamageScenario) {
    scenarioToDelete = scenario;
    showDeleteDialog = true;
  }

  async function deleteDamageScenario() {
    if (!scenarioToDelete) return;
    
    isDeleting = true;

    try {
      await damageScenarioApi.deleteDamageScenario(scenarioToDelete.scenario_id);
      damageScenarios = damageScenarios.filter(s => s.scenario_id !== scenarioToDelete!.scenario_id);
      notifications.show('Damage scenario deleted successfully', 'success');
      dispatch('scenarioDeleted', { scenario_id: scenarioToDelete.scenario_id });
      
      // Reset dialog state
      showDeleteDialog = false;
      scenarioToDelete = null;
    } catch (error) {
      console.error('Error deleting damage scenario:', error);
      notifications.show('Failed to delete damage scenario', 'error');
    } finally {
      isDeleting = false;
    }
  }

  function handleDeleteCancel() {
    showDeleteDialog = false;
    scenarioToDelete = null;
    isDeleting = false;
  }
</script>

<div class="space-y-6">
  <div class="flex justify-end items-center">
    <button
      on:click={() => isAddingNew = !isAddingNew}
      class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
    >
      {isAddingNew ? 'Cancel' : 'Add New Scenario'}
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

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">CIA Security Properties *</label>
        <div class="flex space-x-6">
          <label class="flex items-center">
            <input
              type="checkbox"
              bind:checked={newScenario.confidentiality_impact}
              class="mr-2 h-4 w-4 text-indigo-600 border-gray-300 rounded"
            />
            <span class="text-sm text-gray-700">Confidentiality</span>
          </label>
          <label class="flex items-center">
            <input
              type="checkbox"
              bind:checked={newScenario.integrity_impact}
              class="mr-2 h-4 w-4 text-indigo-600 border-gray-300 rounded"
            />
            <span class="text-sm text-gray-700">Integrity</span>
          </label>
          <label class="flex items-center">
            <input
              type="checkbox"
              bind:checked={newScenario.availability_impact}
              class="mr-2 h-4 w-4 text-indigo-600 border-gray-300 rounded"
            />
            <span class="text-sm text-gray-700">Availability</span>
          </label>
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
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SFOP</th>
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
                <div class="space-y-1">
                  {#each Object.entries(getSfopImpacts(scenario)) as [key, value]}
                    <div class="flex items-center space-x-2">
                      <span class="text-xs font-medium w-8">{key.charAt(0).toUpperCase()}</span>
                      <span class="px-2 py-1 text-xs rounded {getSfopBadgeClass(value)}">{value}</span>
                    </div>
                  {/each}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs rounded {getSfopBadgeClass(getOverallSfopRating(scenario))}">
                  {getOverallSfopRating(scenario)}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  on:click={() => confirmDelete(scenario)}
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

<!-- Delete Confirmation Dialog -->
<ConfirmDialog
  bind:isOpen={showDeleteDialog}
  title="Delete Damage Scenario"
  message={scenarioToDelete ? `Are you sure you want to delete "${scenarioToDelete.name}"? This action cannot be undone.` : ''}
  confirmText="Delete"
  cancelText="Cancel"
  variant="danger"
  loading={isDeleting}
  on:confirm={deleteDamageScenario}
  on:cancel={handleDeleteCancel}
/>
