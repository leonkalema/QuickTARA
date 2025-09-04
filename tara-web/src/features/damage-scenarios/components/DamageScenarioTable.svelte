<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { damageScenarioApi } from '../../../lib/api/damageScenarioApi';
  import { notifications } from '../../../lib/stores/notificationStore';
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
  export let productId: string;

  const dispatch = createEventDispatcher();

  let editingCell: { scenarioId: string; field: string } | null = null;
  let editingValue = '';
  let newScenario: CreateDamageScenarioRequest = {
    name: '',
    description: '',
    primary_component_id: '',
    confidentiality_impact: false,
    integrity_impact: false,
    availability_impact: false,
    damage_category: DamageCategory.OPERATIONAL,
    impact_type: ImpactType.DIRECT,
    severity: SeverityLevel.MEDIUM,
    scope_id: productId
  };
  let isAddingNew = false;
  let isSaving = false;

  $: newScenario.scope_id = productId;

  function startEdit(scenario: DamageScenario, field: string) {
    editingCell = { scenarioId: scenario.scenario_id, field };
    editingValue = getFieldValue(scenario, field);
  }

  function getFieldValue(scenario: DamageScenario, field: string): string {
    switch (field) {
      case 'name': return scenario.name;
      case 'description': return scenario.description || '';
      case 'primary_component_id': return scenario.primary_component_id;
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
      const updatedScenario = await damageScenarioApi.update(scenario.damage_scenario_id, updateData);
      
      // Update local scenario
      const index = damageScenarios.findIndex(ds => ds.damage_scenario_id === scenario.damage_scenario_id);
      if (index !== -1) {
        damageScenarios[index] = updatedScenario;
        damageScenarios = [...damageScenarios];
      }
      
      dispatch('damageScenarioUpdated', updatedScenario);
      notifications.show('Damage scenario updated successfully', 'success');
    } catch (error) {
      console.error('Error updating damage scenario:', error);
      notifications.show('Failed to update damage scenario', 'error');
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

  function toggleCIAProperty(property: CIAProperty) {
    if (newScenario.affected_cia?.includes(property)) {
      newScenario.affected_cia = newScenario.affected_cia.filter(p => p !== property);
    } else {
      newScenario.affected_cia = [...(newScenario.affected_cia || []), property];
    }
  }

  function toggleExistingCIA(scenario: DamageScenario, property: CIAProperty) {
    const currentCIA = scenario.affected_cia || [];
    const newCIA = currentCIA.includes(property) 
      ? currentCIA.filter(p => p !== property)
      : [...currentCIA, property];
    
    // Save immediately
    saveEditCIA(scenario, newCIA);
  }

  async function saveEditCIA(scenario: DamageScenario, newCIA: CIAProperty[]) {
    isSaving = true;
    try {
      const updatedScenario = await damageScenarioApi.update(scenario.damage_scenario_id, { affected_cia: newCIA });
      
      const index = damageScenarios.findIndex(ds => ds.damage_scenario_id === scenario.damage_scenario_id);
      if (index !== -1) {
        damageScenarios[index] = updatedScenario;
        damageScenarios = [...damageScenarios];
      }
      
      dispatch('damageScenarioUpdated', updatedScenario);
    } catch (error) {
      console.error('Error updating CIA properties:', error);
      notifications.show('Failed to update CIA properties', 'error');
    } finally {
      isSaving = false;
    }
  }

  async function addNewScenario() {
    if (!newScenario.name?.trim() || !newScenario.asset_id || !newScenario.affected_cia?.length) {
      notifications.show('Name, asset, and at least one CIA property are required', 'error');
      return;
    }

    isSaving = true;
    try {
      const scenarioData: CreateDamageScenarioRequest = {
        name: newScenario.name,
        description: newScenario.description || '',
        asset_id: newScenario.asset_id,
        scope_id: productId,
        affected_cia: newScenario.affected_cia,
        threat_scenario_text: newScenario.threat_scenario_text || ''
      };

      const createdScenario = await damageScenarioApi.create(scenarioData);
      damageScenarios = [...damageScenarios, createdScenario];
      
      // Reset form
      newScenario = {
        name: '',
        description: '',
        asset_id: '',
        affected_cia: [],
        threat_scenario_text: '',
        scope_id: productId
      };
      
      dispatch('damageScenarioCreated', createdScenario);
      notifications.show('Damage scenario created successfully', 'success');
      isAddingNew = false;
    } catch (error) {
      console.error('Error creating damage scenario:', error);
      notifications.show('Failed to create damage scenario', 'error');
    } finally {
      isSaving = false;
    }
  }

  function cancelNewScenario() {
    newScenario = {
      name: '',
      description: '',
      asset_id: '',
      affected_cia: [],
      threat_scenario_text: '',
      scope_id: productId
    };
    isAddingNew = false;
  }

  function getAssetName(assetId: string): string {
    const asset = assets.find(a => a.asset_id === assetId);
    return asset ? asset.name : 'Unknown Asset';
  }

  function getCIABadgeColor(property: CIAProperty): string {
    switch (property) {
      case CIAProperty.CONFIDENTIALITY: return 'text-blue-700 bg-blue-100';
      case CIAProperty.INTEGRITY: return 'text-green-700 bg-green-100';
      case CIAProperty.AVAILABILITY: return 'text-red-700 bg-red-100';
      default: return 'text-gray-700 bg-gray-100';
    }
  }

  // Load threat scenarios when component mounts
  loadThreatScenarios();
</script>

<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
  <!-- Table Header -->
  <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-medium text-gray-900">Damage Scenarios</h3>
      <button
        on:click={() => isAddingNew = true}
        class="px-3 py-1.5 bg-slate-600 text-white text-sm rounded-md hover:bg-slate-700 transition-colors"
      >
        + Add Damage Scenario
      </button>
    </div>
  </div>

  <!-- Table -->
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-48">
            Name
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-40">
            Asset
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-32">
            Affected CIA
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-64">
            Description
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-64">
            Threat Scenario
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <!-- Existing Damage Scenarios -->
        {#each damageScenarios as scenario (scenario.damage_scenario_id)}
          <tr class="hover:bg-gray-50">
            <!-- Name -->
            <td class="px-4 py-3">
              {#if editingCell?.scenarioId === scenario.damage_scenario_id && editingCell?.field === 'name'}
                <input
                  type="text"
                  bind:value={editingValue}
                  on:keydown={(e) => handleKeyPress(e, scenario, 'name')}
                  on:blur={() => saveEdit(scenario, 'name')}
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  disabled={isSaving}
                  autofocus
                />
              {:else}
                <button
                  on:click={() => startEdit(scenario, 'name')}
                  class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors font-medium text-gray-900"
                >
                  {scenario.name}
                </button>
              {/if}
            </td>

            <!-- Asset -->
            <td class="px-4 py-3">
              {#if editingCell?.scenarioId === scenario.damage_scenario_id && editingCell?.field === 'asset_id'}
                <select
                  bind:value={editingValue}
                  on:change={() => saveEdit(scenario, 'asset_id')}
                  on:blur={() => saveEdit(scenario, 'asset_id')}
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  disabled={isSaving}
                  autofocus
                >
                  {#each assets as asset}
                    <option value={asset.asset_id}>{asset.name}</option>
                  {/each}
                </select>
              {:else}
                <button
                  on:click={() => startEdit(scenario, 'asset_id')}
                  class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors text-sm"
                >
                  {getAssetName(scenario.asset_id)}
                </button>
              {/if}
            </td>

            <!-- Affected CIA -->
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                {#each Object.values(CIAProperty) as property}
                  <button
                    on:click={() => toggleExistingCIA(scenario, property)}
                    class="px-2 py-1 text-xs font-medium rounded-full transition-colors {
                      scenario.affected_cia?.includes(property) 
                        ? getCIABadgeColor(property)
                        : 'text-gray-400 bg-gray-100 hover:bg-gray-200'
                    }"
                  >
                    {property.charAt(0)}
                  </button>
                {/each}
              </div>
            </td>

            <!-- Description -->
            <td class="px-4 py-3">
              {#if editingCell?.scenarioId === scenario.damage_scenario_id && editingCell?.field === 'description'}
                <textarea
                  bind:value={editingValue}
                  on:keydown={(e) => e.key === 'Enter' && e.ctrlKey && saveEdit(scenario, 'description')}
                  on:blur={() => saveEdit(scenario, 'description')}
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                  rows="2"
                  disabled={isSaving}
                  autofocus
                ></textarea>
              {:else}
                <button
                  on:click={() => startEdit(scenario, 'description')}
                  class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors text-sm text-gray-600"
                >
                  {scenario.description || 'Click to add...'}
                </button>
              {/if}
            </td>

            <!-- Threat Scenario -->
            <td class="px-4 py-3">
              {#if editingCell?.scenarioId === scenario.damage_scenario_id && editingCell?.field === 'threat_scenario_text'}
                <textarea
                  bind:value={editingValue}
                  on:keydown={(e) => e.key === 'Enter' && e.ctrlKey && saveEdit(scenario, 'threat_scenario_text')}
                  on:blur={() => saveEdit(scenario, 'threat_scenario_text')}
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                  rows="2"
                  disabled={isSaving}
                  autofocus
                ></textarea>
              {:else}
                <button
                  on:click={() => startEdit(scenario, 'threat_scenario_text')}
                  class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors text-sm text-gray-600"
                >
                  {scenario.threat_scenario_text || 'Click to add...'}
                </button>
              {/if}
            </td>
          </tr>
        {/each}

        <!-- Add New Scenario Row -->
        {#if isAddingNew}
          <tr class="bg-blue-50 border-2 border-blue-200">
            <!-- Name -->
            <td class="px-4 py-3">
              <input
                type="text"
                bind:value={newScenario.name}
                placeholder="Scenario name..."
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                autofocus
              />
            </td>

            <!-- Asset -->
            <td class="px-4 py-3">
              <select
                bind:value={newScenario.asset_id}
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Select asset...</option>
                {#each assets as asset}
                  <option value={asset.asset_id}>{asset.name}</option>
                {/each}
              </select>
            </td>

            <!-- Affected CIA -->
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                {#each Object.values(CIAProperty) as property}
                  <button
                    type="button"
                    on:click={() => toggleCIAProperty(property)}
                    class="px-2 py-1 text-xs font-medium rounded-full transition-colors {
                      newScenario.affected_cia?.includes(property) 
                        ? getCIABadgeColor(property)
                        : 'text-gray-400 bg-gray-100 hover:bg-gray-200'
                    }"
                  >
                    {property.charAt(0)}
                  </button>
                {/each}
              </div>
            </td>

            <!-- Description -->
            <td class="px-4 py-3">
              <textarea
                bind:value={newScenario.description}
                placeholder="Describe the damage scenario..."
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                rows="2"
              ></textarea>
            </td>

            <!-- Threat Scenario -->
            <td class="px-4 py-3">
              <textarea
                bind:value={newScenario.threat_scenario_text}
                placeholder="Describe the threat scenario..."
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                rows="2"
              ></textarea>
            </td>
          </tr>
          
          <!-- Action Row -->
          <tr class="bg-blue-50">
            <td colspan="5" class="px-4 py-3">
              <div class="flex justify-end space-x-2">
                <button
                  on:click={cancelNewScenario}
                  class="px-3 py-1.5 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded text-sm transition-colors"
                  disabled={isSaving}
                >
                  Cancel
                </button>
                <button
                  on:click={addNewScenario}
                  disabled={isSaving || !newScenario.name?.trim() || !newScenario.asset_id || !newScenario.affected_cia?.length}
                  class="px-3 py-1.5 bg-slate-600 text-white rounded text-sm hover:bg-slate-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
                >
                  {#if isSaving}
                    <div class="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                    <span>Saving...</span>
                  {:else}
                    <span>Save Scenario</span>
                  {/if}
                </button>
              </div>
            </td>
          </tr>
        {/if}
      </tbody>
    </table>
  </div>

  <!-- Empty State -->
  {#if damageScenarios.length === 0 && !isAddingNew}
    <div class="text-center py-12">
      <div class="text-gray-400 text-6xl mb-4">⚠️</div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No damage scenarios yet</h3>
      <p class="text-gray-500 mb-4">Start by adding your first damage scenario for this product.</p>
      <button
        on:click={() => isAddingNew = true}
        class="px-4 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700 transition-colors"
      >
        Add First Damage Scenario
      </button>
    </div>
  {/if}
</div>
