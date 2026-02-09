<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { notifications } from '$lib/stores/notificationStore';
  import { threatScenarioApi } from '$lib/api/threatScenarioApi';
  import { selectedProduct } from '$lib/stores/productStore';
  import type { ThreatScenario, CreateThreatScenarioRequest } from '$lib/types/threatScenario';
  import type { DamageScenario } from '$lib/types/damageScenario';
  import ConfirmDialog from '../../../components/ConfirmDialog.svelte';
  import DamageScenarioTagSelector from './DamageScenarioTagSelector.svelte';
  import ThreatCatalogPicker from './ThreatCatalogPicker.svelte';
  import { authStore } from '$lib/stores/auth';
  import WorkflowBadge from '../../audit/components/WorkflowBadge.svelte';

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
  let validationErrors: Record<string, string> = {};

  // Catalog picker
  let showCatalogPicker = false;

  function handleCatalogSelect(event: CustomEvent) {
    const selected = event.detail;
    newScenario.name = selected.name;
    newScenario.description = selected.description;
    newScenario.attack_vector = selected.attack_vector;
    showCatalogPicker = false;
  }

  // Delete confirmation
  let showDeleteDialog = false;
  let scenarioToDelete: ThreatScenario | null = null;
  let isDeleting = false;
  let canDelete = false;
  $: {
    const state: any = $authStore;
    const isSuperuser = !!state?.user?.is_superuser;
    canDelete = isSuperuser || authStore.hasRole('tool_admin') || authStore.hasRole('org_admin');
  }

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

  function validateForm(): boolean {
    validationErrors = {};
    if (!newScenario.name.trim()) {
      validationErrors['name'] = 'Threat scenario name is required';
    }
    if (!newScenario.damage_scenario_ids.length && !newScenario.damage_scenario_id) {
      validationErrors['damage'] = 'Select at least one damage scenario';
    }
    if (!$selectedProduct?.scope_id) {
      validationErrors['product'] = 'Select a product first';
    }
    return Object.keys(validationErrors).length === 0;
  }

  async function addNewScenario() {
    if (!validateForm()) return;

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
    if (!canDelete) return;
    scenarioToDelete = scenario;
    showDeleteDialog = true;
  }

  async function deleteThreatScenario() {
    if (!canDelete || !scenarioToDelete) return;
    
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

  async function acceptScenario(scenario: ThreatScenario) {
    try {
      await threatScenarioApi.acceptScenario(scenario.threat_scenario_id);
      const index = threatScenarios.findIndex(s => s.threat_scenario_id === scenario.threat_scenario_id);
      if (index !== -1) {
        threatScenarios[index] = { ...threatScenarios[index], status: 'accepted' };
        threatScenarios = [...threatScenarios];
      }
      notifications.show('Threat scenario accepted', 'success');
    } catch (error) {
      notifications.show('Failed to accept scenario', 'error');
    }
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
    <form on:submit|preventDefault={addNewScenario} class="p-5 rounded-lg mb-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
      <div class="grid grid-cols-1 gap-4 mb-4">
        <div>
        <input bind:value={newScenario.name} placeholder="Threat scenario name *"
          class="px-3 py-2 rounded-md w-full text-sm" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid {validationErrors['name'] ? 'var(--color-error)' : 'var(--color-border-default)'};" />
        {#if validationErrors['name']}
          <p class="text-xs mt-1" style="color: var(--color-error);">{validationErrors['name']}</p>
        {/if}
      </div>
        
        <!-- Use the new tag selector component -->
        <div class="{validationErrors['damage'] ? 'rounded-md' : ''}" style="{validationErrors['damage'] ? 'box-shadow: 0 0 0 1px var(--color-error);' : ''}">
          <DamageScenarioTagSelector 
            bind:selectedDamageScenarios={newScenario.damage_scenario_ids}
            placeholder="Select damage scenarios that this threat could cause..."
          />
        </div>
        {#if validationErrors['damage']}
          <p class="text-xs mt-1" style="color: var(--color-error);">{validationErrors['damage']}</p>
        {/if}
        {#if validationErrors['product']}
          <p class="text-xs mt-1" style="color: var(--color-error);">{validationErrors['product']}</p>
        {/if}
      </div>
      
      <textarea bind:value={newScenario.description} placeholder="Description" class="w-full px-3 py-2 rounded-md mb-3 text-sm" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" rows="2"></textarea>
      <input bind:value={newScenario.attack_vector} placeholder="Attack vector" class="w-full px-3 py-2 rounded-md mb-4 text-sm" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
      
      <div class="flex gap-2 mb-4">
        <button type="button" on:click={() => showCatalogPicker = true}
          class="px-3 py-2 rounded-md font-medium text-xs flex items-center gap-2" style="background: var(--color-info); color: var(--color-text-inverse);">
          &#128737; Pick from MITRE Catalog
        </button>
      </div>

      <div class="flex gap-2">
        <button type="submit" class="px-3 py-2 rounded-md font-medium text-sm" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">
          Add Threat Scenario
        </button>
        <button type="button" on:click={resetForm} class="px-3 py-2 rounded-md font-medium text-sm" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);">
          Cancel
        </button>
      </div>
    </form>
  {/if}

  <!-- Table -->
  <div class="rounded-lg overflow-hidden" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <div class="overflow-x-auto">
      <table class="min-w-full" style="border-collapse: separate;">
        <thead style="background: var(--color-bg-elevated);">
          <tr>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider w-1/5" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Name</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider w-1/5" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Damage Scenario</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider w-1/6" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Attack Vector</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider w-1/3" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Description</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider w-1/12" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each threatScenarios as scenario (scenario.threat_scenario_id)}
            <tr style="border-bottom: 1px solid var(--color-border-subtle);">
              <td class="px-6 py-4">
                {#if editingCell?.scenarioId === scenario.threat_scenario_id && editingCell?.field === 'name'}
                  <input
                    bind:value={editingValue}
                    on:keydown={(e) => handleKeyPress(e, scenario, 'name')}
                    class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
                    disabled={isSaving}
                  />
                {:else}
                  <div class="text-xs font-medium cursor-pointer px-2 py-1 rounded break-words flex items-center gap-2" style="color: var(--color-text-primary);" 
                       on:click={() => startEdit(scenario, 'name')}>
                    {scenario.name}
                    {#if scenario.status === 'draft'}
                      <span class="px-1.5 py-0.5 text-[10px] rounded font-normal" style="background: var(--color-warning-bg); color: var(--color-warning);">Draft</span>
                    {/if}
                  </div>
                {/if}
              </td>
              <td class="px-6 py-4">
                {#await getLinkedDamageScenarios(scenario.threat_scenario_id)}
                  <span class="text-xs" style="color: var(--color-text-tertiary);">Loading...</span>
                {:then linkedIds}
                  <div class="text-xs" style="color: var(--color-text-primary);">
                    {#if linkedIds.length > 0}
                      <div class="flex flex-wrap gap-1">
                        {#each linkedIds as damageId}
                          <span 
                            class="inline-block text-[10px] px-2 py-0.5 rounded-full cursor-help" style="background: var(--color-info-bg); color: var(--color-info);"
                            title={getDamageScenarioName(damageId)}
                          >
                            {damageId}
                          </span>
                        {/each}
                      </div>
                    {:else}
                      <span class="italic" style="color: var(--color-text-tertiary);">No linked scenarios</span>
                    {/if}
                  </div>
                {:catch error}
                  <span class="text-xs" style="color: var(--color-error);">Error loading</span>
                {/await}
              </td>
              <td class="px-6 py-4">
                {#if editingCell?.scenarioId === scenario.threat_scenario_id && editingCell?.field === 'attack_vector'}
                  <input
                    bind:value={editingValue}
                    on:keydown={(e) => handleKeyPress(e, scenario, 'attack_vector')}
                    class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
                    disabled={isSaving}
                  />
                {:else}
                  <div class="text-xs cursor-pointer px-2 py-1 rounded" style="color: var(--color-text-secondary);"
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
                    class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
                    rows="2"
                    disabled={isSaving}
                  ></textarea>
                {:else}
                  <div class="text-xs cursor-pointer px-2 py-1 rounded max-w-xs" style="color: var(--color-text-secondary);"
                       on:click={() => startEdit(scenario, 'description')}>
                    {scenario.description || 'Click to add description'}
                  </div>
                {/if}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2 flex-wrap">
                  <WorkflowBadge
                    artifactType="threat_scenario"
                    artifactId={scenario.threat_scenario_id}
                    scopeId={$selectedProduct?.scope_id || ''}
                  />
                  {#if scenario.status === 'draft'}
                    <button on:click={() => acceptScenario(scenario)} class="font-medium text-xs" style="color: var(--color-success);">Accept</button>
                  {/if}
                  {#if canDelete}
                    <button on:click={() => confirmDelete(scenario)} class="text-xs" style="color: var(--color-error);">Delete</button>
                  {/if}
                </div>
              </td>
            </tr>
          {/each}
          
          {#if threatScenarios.length === 0}
            <tr>
              <td colspan="5" class="px-4 py-10 text-center text-xs" style="color: var(--color-text-tertiary);">
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
<ThreatCatalogPicker bind:isOpen={showCatalogPicker} on:select={handleCatalogSelect} />

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
