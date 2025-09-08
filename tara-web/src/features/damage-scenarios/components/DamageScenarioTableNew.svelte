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
  export let isAddingNew: boolean = false;

  const dispatch = createEventDispatcher();

  // Inline editing state
  let editingCell: { scenarioId: string; field: string } | null = null;
  let editingValue = '';
  let isSaving = false;

  // Form state
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
  
  // Form validity (all fields mandatory for add form)
  $: formValid =
    newScenario.name.trim().length > 0 &&
    newScenario.description.trim().length > 0 &&
    !!newScenario.primary_component_id &&
    (newScenario.confidentiality_impact || newScenario.integrity_impact || newScenario.availability_impact) &&
    !!safety_impact && !!financial_impact && !!operational_impact && !!privacy_impact;
  
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
    dispatch('cancelAdd');
  }

  async function addNewScenario() {
    if (!$selectedProduct?.scope_id) {
      notifications.show('Please select a product first', 'error');
      return;
    }

    // Mandatory fields validation
    if (!newScenario.name.trim()) {
      notifications.show('Scenario name is required', 'error');
      return;
    }
    if (!newScenario.description.trim()) {
      notifications.show('Description is required', 'error');
      return;
    }
    if (!newScenario.primary_component_id) {
      notifications.show('Asset selection is required', 'error');
      return;
    }
    if (!newScenario.confidentiality_impact && !newScenario.integrity_impact && !newScenario.availability_impact) {
      notifications.show('Select at least one CIA property (C, I, or A)', 'error');
      return;
    }
    if (!safety_impact || !financial_impact || !operational_impact || !privacy_impact) {
      notifications.show('All SFOP impact ratings (Safety, Financial, Operational, Privacy) are required', 'error');
      return;
    }

    try {
      const scenarioData: CreateDamageScenarioRequest = {
        ...newScenario,
        scope_id: $selectedProduct.scope_id,
        impact_rating: {
          safety: (safety_impact || 'negligible') as any,
          financial: (financial_impact || 'negligible') as any,
          operational: (operational_impact || 'negligible') as any,
          privacy: (privacy_impact || 'negligible') as any
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

  // Inline editing functions
  function startEdit(scenario: DamageScenario, field: string) {
    editingCell = { scenarioId: scenario.scenario_id, field };
    editingValue = getFieldValue(scenario, field);
  }

  function getFieldValue(scenario: DamageScenario, field: string): string {
    switch (field) {
      case 'name': return scenario.name;
      case 'description': return scenario.description || '';
      case 'primary_component_id': return scenario.primary_component_id || '';
      default: return '';
    }
  }

  async function saveEdit(scenario: DamageScenario, field: string) {
    if (!editingCell || editingValue === getFieldValue(scenario, field)) {
      cancelEdit();
      return;
    }

    isSaving = true;
    try {
      const updateData: any = { [field]: editingValue };
      const updatedScenario = await damageScenarioApi.updateDamageScenario(scenario.scenario_id, updateData);
      
      // Update local scenario
      const index = damageScenarios.findIndex(s => s.scenario_id === scenario.scenario_id);
      if (index !== -1) {
        damageScenarios[index] = updatedScenario;
        damageScenarios = [...damageScenarios];
      }
      
      dispatch('scenarioUpdated', updatedScenario);
      notifications.show('Scenario updated successfully', 'success');
    } catch (error) {
      console.error('Error updating scenario:', error);
      notifications.show('Failed to update scenario', 'error');
    } finally {
      isSaving = false;
      cancelEdit();
    }
  }

  function cancelEdit() {
    editingCell = null;
    editingValue = '';
  }

  function handleKeyPress(event: KeyboardEvent, scenario: DamageScenario, field: string) {
    if (event.key === 'Enter') {
      saveEdit(scenario, field);
    } else if (event.key === 'Escape') {
      cancelEdit();
    }
  }
</script>

<div class="space-y-6">

  {#if isAddingNew}
    <form on:submit|preventDefault={addNewScenario} class="bg-white p-6 rounded-lg border border-gray-200 shadow-sm mb-6">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <input bind:value={newScenario.name} placeholder="Scenario name *" class="px-3 py-2 border rounded-md" required />
        <select bind:value={newScenario.primary_component_id} class="px-3 py-2 border rounded-md" required>
          <option value="">Select asset... *</option>
          {#each assets as asset}<option value={asset.asset_id}>{asset.name}</option>{/each}
        </select>
      </div>
      <textarea bind:value={newScenario.description} placeholder="Description *" class="w-full px-3 py-2 border rounded-md mb-3" rows="2" required></textarea>
      <div class="grid grid-cols-4 gap-2 mb-3">
        <select bind:value={safety_impact} class="px-2 py-1 border rounded text-sm" required>
          <option value="">Safety *</option>
          <option value="negligible">Negligible</option>
          <option value="moderate">Moderate</option>
          <option value="major">Major</option>
          <option value="severe">Severe</option>
        </select>
        <select bind:value={financial_impact} class="px-2 py-1 border rounded text-sm" required>
          <option value="">Financial *</option>
          <option value="negligible">Negligible</option>
          <option value="moderate">Moderate</option>
          <option value="major">Major</option>
          <option value="severe">Severe</option>
        </select>
        <select bind:value={operational_impact} class="px-2 py-1 border rounded text-sm" required>
          <option value="">Operational *</option>
          <option value="negligible">Negligible</option>
          <option value="moderate">Moderate</option>
          <option value="major">Major</option>
          <option value="severe">Severe</option>
        </select>
        <select bind:value={privacy_impact} class="px-2 py-1 border rounded text-sm" required>
          <option value="">Privacy *</option>
          <option value="negligible">Negligible</option>
          <option value="moderate">Moderate</option>
          <option value="major">Major</option>
          <option value="severe">Severe</option>
        </select>
      </div>
      <div class="flex space-x-4 mb-3">
        <label class="flex items-center text-sm">
          <input type="checkbox" bind:checked={newScenario.confidentiality_impact} class="mr-1" />C
        </label>
        <label class="flex items-center text-sm">
          <input type="checkbox" bind:checked={newScenario.integrity_impact} class="mr-1" />I
        </label>
        <label class="flex items-center text-sm">
          <input type="checkbox" bind:checked={newScenario.availability_impact} class="mr-1" />A
        </label>
      </div>
      <div class="flex justify-end space-x-2">
        <button type="button" on:click={resetForm} class="px-3 py-1 border rounded text-sm hover:bg-gray-50">Cancel</button>
        <button type="submit" class="px-3 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed" disabled={!formValid}>Create</button>
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
              <td class="px-4 py-3">
                {#if editingCell?.scenarioId === scenario.scenario_id && editingCell?.field === 'name'}
                  <input bind:value={editingValue} on:keydown={(e) => handleKeyPress(e, scenario, 'name')} on:blur={() => saveEdit(scenario, 'name')} class="w-full px-2 py-1 border border-blue-300 rounded" disabled={isSaving} autofocus />
                {:else}
                  <button on:click={() => startEdit(scenario, 'name')} class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded">
                    <div class="text-sm font-medium text-gray-900">{scenario.name}</div>
                  </button>
                {/if}
                {#if editingCell?.scenarioId === scenario.scenario_id && editingCell?.field === 'description'}
                  <textarea bind:value={editingValue} on:keydown={(e) => e.key === 'Enter' && e.ctrlKey && saveEdit(scenario, 'description')} on:blur={() => saveEdit(scenario, 'description')} class="w-full px-2 py-1 border border-blue-300 rounded resize-none mt-1" rows="2" disabled={isSaving}></textarea>
                {:else if scenario.description}
                  <button on:click={() => startEdit(scenario, 'description')} class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded mt-1">
                    <div class="text-sm text-gray-500 max-w-xs break-words">{scenario.description}</div>
                  </button>
                {:else}
                  <button on:click={() => startEdit(scenario, 'description')} class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded mt-1 text-gray-400 italic">Add description...</button>
                {/if}
              </td>
              <td class="px-4 py-3 text-sm">
                {#if editingCell?.scenarioId === scenario.scenario_id && editingCell?.field === 'primary_component_id'}
                  <select bind:value={editingValue} on:change={() => saveEdit(scenario, 'primary_component_id')} on:blur={() => saveEdit(scenario, 'primary_component_id')} class="w-full px-2 py-1 border border-blue-300 rounded" disabled={isSaving} autofocus>
                    <option value="">No asset</option>
                    {#each assets as asset}<option value={asset.asset_id}>{asset.name}</option>{/each}
                  </select>
                {:else}
                  <button on:click={() => startEdit(scenario, 'primary_component_id')} class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded">
                    {scenario.primary_component_id ? getAssetName(scenario.primary_component_id) : 'No asset'}
                  </button>
                {/if}
              </td>
              <td class="px-4 py-3">
                <div class="flex space-x-1">
                  <span class="px-2 py-1 text-xs rounded {getCIABadgeClass(scenario.confidentiality_impact)}">C</span>
                  <span class="px-2 py-1 text-xs rounded {getCIABadgeClass(scenario.integrity_impact)}">I</span>
                  <span class="px-2 py-1 text-xs rounded {getCIABadgeClass(scenario.availability_impact)}">A</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="space-y-1">
                  {#each Object.entries(getSfopImpacts(scenario)) as [key, value]}
                    <div class="flex items-center space-x-1">
                      <span class="text-xs w-6">{key.charAt(0).toUpperCase()}</span>
                      <span class="px-1 py-0.5 text-xs rounded {getSfopBadgeClass(value)}">{value}</span>
                    </div>
                  {/each}
                </div>
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 text-xs rounded {getSfopBadgeClass(getOverallSfopRating(scenario))}">{getOverallSfopRating(scenario)}</span>
              </td>
              <td class="px-4 py-3">
                <button on:click={() => confirmDelete(scenario)} class="text-red-600 hover:text-red-900 text-sm">Delete</button>
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
