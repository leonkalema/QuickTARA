<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { notifications } from '$lib/stores/notificationStore';
  import { threatScenarioApi } from '$lib/api/threatScenarioApi';
  import { selectedProduct } from '$lib/stores/productStore';
  import type { ThreatScenario, CreateThreatScenarioRequest } from '$lib/types/threatScenario';
  import type { DamageScenario } from '$lib/types/damageScenario';
  import ConfirmDialog from '../../../components/ConfirmDialog.svelte';
  import DamageScenarioTagSelector from './DamageScenarioTagSelector.svelte';

  export let threatScenarios: ThreatScenario[] = [];
  export let damageScenarios: DamageScenario[] = [];
  export let isAddingNew: boolean = false;

  const dispatch = createEventDispatcher();

  // Form state
  let newScenario = {
    name: '',
    description: '',
    attack_vector: '',
    damage_scenario_id: '',
    damage_scenario_ids: []
  };

  // Delete confirmation
  let showDeleteDialog = false;
  let scenarioToDelete: ThreatScenario | null = null;
  let isDeleting = false;

  // Inline editing
  let editingCell: { scenarioId: string; field: string } | null = null;
  let editingValue = '';
  let isSaving = false;

  function resetForm() {
    newScenario = {
      name: '',
      description: '',
      attack_vector: '',
      damage_scenario_id: '',
      damage_scenario_ids: []
    };
    dispatch('cancelAdd');
  }

  async function addNewScenario() {
    if (!newScenario.name.trim()) {
      notifications.show('Please enter a threat scenario name', 'error');
      return;
    }

    if (!newScenario.damage_scenario_ids.length && !newScenario.damage_scenario_id) {
      notifications.show('Please select at least one damage scenario', 'error');
      return;
    }

    if (!$selectedProduct?.scope_id) {
      notifications.show('Please select a product first', 'error');
      return;
    }

    try {
      const scenarioData: CreateThreatScenarioRequest = {
        ...newScenario,
        scope_id: $selectedProduct.scope_id,
        scope_version: 1
      };

      const response = await threatScenarioApi.createThreatScenario(scenarioData);
      threatScenarios = [...threatScenarios, response];
      resetForm();
      notifications.show('Threat scenario created successfully', 'success');
      dispatch('scenarioAdded', response);
    } catch (error) {
      console.error('Error creating threat scenario:', error);
      notifications.show('Failed to create threat scenario', 'error');
    }
  }

  function getDamageScenarioName(damageScenarioId: string): string {
    const scenario = damageScenarios.find(ds => ds.scenario_id === damageScenarioId);
    return scenario?.name || 'Unknown';
  }

  async function getLinkedDamageScenarios(threatScenarioId: string): Promise<string[]> {
    try {
      return await threatScenarioApi.getLinkedDamageScenarios(threatScenarioId);
    } catch (error) {
      console.error('Error fetching linked damage scenarios:', error);
      return [];
    }
  }

  function getDamageScenarioNames(damageScenarioIds: string[]): string {
    if (!damageScenarioIds || damageScenarioIds.length === 0) return 'None';
    
    const names = damageScenarioIds.map(id => {
      const scenario = damageScenarios.find(ds => ds.scenario_id === id);
      return scenario?.name || 'Unknown';
    });
    
    return names.join(', ');
  }

  function confirmDelete(scenario: ThreatScenario) {
    scenarioToDelete = scenario;
    showDeleteDialog = true;
  }

  async function deleteThreatScenario() {
    if (!scenarioToDelete) return;
    
    isDeleting = true;
    try {
      await threatScenarioApi.deleteThreatScenario(scenarioToDelete.threat_scenario_id);
      threatScenarios = threatScenarios.filter(s => s.threat_scenario_id !== scenarioToDelete!.threat_scenario_id);
      notifications.show('Threat scenario deleted successfully', 'success');
      dispatch('scenarioDeleted', { threat_scenario_id: scenarioToDelete.threat_scenario_id });
      
      showDeleteDialog = false;
      scenarioToDelete = null;
    } catch (error) {
      console.error('Error deleting threat scenario:', error);
      notifications.show('Failed to delete threat scenario', 'error');
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
  function startEdit(scenario: ThreatScenario, field: string) {
    editingCell = { scenarioId: scenario.threat_scenario_id, field };
    editingValue = getFieldValue(scenario, field);
  }

  function getFieldValue(scenario: ThreatScenario, field: string): string {
    switch (field) {
      case 'name': return scenario.name;
      case 'description': return scenario.description || '';
      case 'attack_vector': return scenario.attack_vector || '';
      default: return '';
    }
  }

  async function saveEdit(scenario: ThreatScenario, field: string) {
    if (!editingCell || editingValue === getFieldValue(scenario, field)) {
      cancelEdit();
      return;
    }

    isSaving = true;
    try {
      const updates = { [field]: editingValue };
      const updatedScenario = await threatScenarioApi.updateThreatScenario(scenario.threat_scenario_id, updates);
      
      const index = threatScenarios.findIndex(s => s.threat_scenario_id === scenario.threat_scenario_id);
      if (index !== -1) {
        threatScenarios[index] = updatedScenario;
        threatScenarios = [...threatScenarios];
      }
      
      notifications.show('Threat scenario updated successfully', 'success');
      cancelEdit();
    } catch (error) {
      console.error('Error updating threat scenario:', error);
      notifications.show('Failed to update threat scenario', 'error');
    } finally {
      isSaving = false;
    }
  }

  function cancelEdit() {
    editingCell = null;
    editingValue = '';
  }

  function handleKeyPress(event: KeyboardEvent, scenario: ThreatScenario, field: string) {
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
      <div class="grid grid-cols-1 gap-4 mb-4">
        <input bind:value={newScenario.name} placeholder="Threat scenario name *" class="px-3 py-2 border rounded-md" />
        
        <!-- Use the new tag selector component -->
        <DamageScenarioTagSelector 
          bind:selectedDamageScenarios={newScenario.damage_scenario_ids}
          placeholder="Select damage scenarios that this threat could cause..."
        />
      </div>
      
      <textarea bind:value={newScenario.description} placeholder="Description" class="w-full px-3 py-2 border rounded-md mb-3" rows="2"></textarea>
      <input bind:value={newScenario.attack_vector} placeholder="Attack vector" class="w-full px-3 py-2 border rounded-md mb-4" />
      
      <div class="flex gap-2">
        <button type="submit" class="bg-black hover:bg-gray-800 text-white px-4 py-2 rounded-md font-medium">
          Add Threat Scenario
        </button>
        <button type="button" on:click={resetForm} class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md font-medium">
          Cancel
        </button>
      </div>
    </form>
  {/if}

  <!-- Table -->
  <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Damage Scenario</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Attack Vector</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          {#each threatScenarios as scenario (scenario.threat_scenario_id)}
            <tr class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                {#if editingCell?.scenarioId === scenario.threat_scenario_id && editingCell?.field === 'name'}
                  <input
                    bind:value={editingValue}
                    on:keydown={(e) => handleKeyPress(e, scenario, 'name')}
                    class="w-full px-2 py-1 border rounded text-sm"
                    disabled={isSaving}
                  />
                {:else}
                  <div class="text-sm font-medium text-gray-900 cursor-pointer hover:bg-gray-100 px-2 py-1 rounded" 
                       on:click={() => startEdit(scenario, 'name')}>
                    {scenario.name}
                  </div>
                {/if}
              </td>
              <td class="px-6 py-4">
                {#await getLinkedDamageScenarios(scenario.threat_scenario_id)}
                  <span class="text-sm text-gray-500">Loading...</span>
                {:then linkedIds}
                  <div class="text-sm text-gray-900">
                    {#if linkedIds.length > 0}
                      <div class="flex flex-wrap gap-1">
                        {#each linkedIds as damageId}
                          <span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                            {getDamageScenarioName(damageId)}
                          </span>
                        {/each}
                      </div>
                    {:else}
                      <span class="text-gray-500 italic">No damage scenarios linked</span>
                    {/if}
                  </div>
                {:catch error}
                  <span class="text-sm text-red-500">Error loading scenarios</span>
                {/await}
              </td>
              <td class="px-6 py-4">
                {#if editingCell?.scenarioId === scenario.threat_scenario_id && editingCell?.field === 'attack_vector'}
                  <input
                    bind:value={editingValue}
                    on:keydown={(e) => handleKeyPress(e, scenario, 'attack_vector')}
                    class="w-full px-2 py-1 border rounded text-sm"
                    disabled={isSaving}
                  />
                {:else}
                  <div class="text-sm text-gray-900 cursor-pointer hover:bg-gray-100 px-2 py-1 rounded" 
                       on:click={() => startEdit(scenario, 'attack_vector')}>
                    {scenario.attack_vector || 'Click to add'}
                  </div>
                {/if}
              </td>
              <td class="px-6 py-4">
                {#if editingCell?.scenarioId === scenario.threat_scenario_id && editingCell?.field === 'description'}
                  <textarea
                    bind:value={editingValue}
                    on:keydown={(e) => handleKeyPress(e, scenario, 'description')}
                    class="w-full px-2 py-1 border rounded text-sm"
                    rows="2"
                    disabled={isSaving}
                  ></textarea>
                {:else}
                  <div class="text-sm text-gray-900 cursor-pointer hover:bg-gray-100 px-2 py-1 rounded max-w-xs" 
                       on:click={() => startEdit(scenario, 'description')}>
                    {scenario.description || 'Click to add description'}
                  </div>
                {/if}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button
                  on:click={() => confirmDelete(scenario)}
                  class="text-red-600 hover:text-red-900 ml-4"
                >
                  Delete
                </button>
              </td>
            </tr>
          {/each}
          
          {#if threatScenarios.length === 0}
            <tr>
              <td colspan="5" class="px-6 py-12 text-center text-gray-500">
                No threat scenarios found. Add one above to get started.
              </td>
            </tr>
          {/if}
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- Delete Confirmation Dialog -->
<ConfirmDialog
  isOpen={showDeleteDialog}
  title="Delete Threat Scenario"
  message="Are you sure you want to delete this threat scenario? This action cannot be undone."
  confirmText="Delete"
  cancelText="Cancel"
  loading={isDeleting}
  on:confirm={deleteThreatScenario}
  on:cancel={handleDeleteCancel}
/>
