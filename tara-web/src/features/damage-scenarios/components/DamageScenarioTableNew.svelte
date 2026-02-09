<script lang="ts">
  import { notifications } from '$lib/stores/notificationStore';
  import type { CreateDamageScenarioRequest, DamageScenario } from '$lib/types/damageScenario';
  import { damageScenarioApi } from '$lib/api/damageScenarioApi';
  import { selectedProduct } from '$lib/stores/productStore';
  import { onMount, createEventDispatcher } from 'svelte';
  import { getOverallSfopRating, getSfopBadgeStyle, getCIABadgeStyle, getSfopImpacts } from '$lib/utils/sfopUtils';
  import ConfirmDialog from '../../../components/ConfirmDialog.svelte';
  import { authStore } from '$lib/stores/auth';
  import WorkflowBadge from '../../audit/components/WorkflowBadge.svelte';

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
  let canDelete = false;
  $: {
    const state: any = $authStore;
    const isSuperuser = !!state?.user?.is_superuser;
    canDelete = isSuperuser || authStore.hasRole('tool_admin') || authStore.hasRole('org_admin');
  }

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
    if (!canDelete) return;
    scenarioToDelete = scenario;
    showDeleteDialog = true;
  }

  async function deleteDamageScenario() {
    if (!canDelete || !scenarioToDelete) return;
    
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

  async function acceptScenario(scenario: DamageScenario) {
    try {
      const updated = await damageScenarioApi.acceptScenario(scenario.scenario_id);
      const index = damageScenarios.findIndex(s => s.scenario_id === scenario.scenario_id);
      if (index !== -1) {
        damageScenarios[index] = { ...damageScenarios[index], status: 'accepted' };
        damageScenarios = [...damageScenarios];
      }
      notifications.show('Scenario accepted', 'success');
    } catch (error) {
      notifications.show('Failed to accept scenario', 'error');
    }
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
    <form on:submit|preventDefault={addNewScenario} class="p-5 rounded-lg mb-6" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
      <div class="grid grid-cols-2 gap-3 mb-3">
        <input bind:value={newScenario.name} placeholder="Scenario name *" class="px-3 py-2 rounded-md text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" required />
        <select bind:value={newScenario.primary_component_id} class="px-3 py-2 rounded-md text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" required>
          <option value="">Select asset... *</option>
          {#each assets as asset}<option value={asset.asset_id}>{asset.name}</option>{/each}
        </select>
      </div>
      <textarea bind:value={newScenario.description} placeholder="Description *" class="w-full px-3 py-2 rounded-md mb-3 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" rows="2" required></textarea>
      <div class="grid grid-cols-4 gap-2 mb-3">
        <select bind:value={safety_impact} class="px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" required>
          <option value="">Safety *</option>
          <option value="negligible">Negligible</option>
          <option value="moderate">Moderate</option>
          <option value="major">Major</option>
          <option value="severe">Severe</option>
        </select>
        <select bind:value={financial_impact} class="px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" required>
          <option value="">Financial *</option>
          <option value="negligible">Negligible</option>
          <option value="moderate">Moderate</option>
          <option value="major">Major</option>
          <option value="severe">Severe</option>
        </select>
        <select bind:value={operational_impact} class="px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" required>
          <option value="">Operational *</option>
          <option value="negligible">Negligible</option>
          <option value="moderate">Moderate</option>
          <option value="major">Major</option>
          <option value="severe">Severe</option>
        </select>
        <select bind:value={privacy_impact} class="px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" required>
          <option value="">Privacy *</option>
          <option value="negligible">Negligible</option>
          <option value="moderate">Moderate</option>
          <option value="major">Major</option>
          <option value="severe">Severe</option>
        </select>
      </div>
      <div class="flex space-x-4 mb-3">
        <label class="flex items-center text-xs" style="color: var(--color-text-secondary);">
          <input type="checkbox" bind:checked={newScenario.confidentiality_impact} class="mr-1" />C
        </label>
        <label class="flex items-center text-xs" style="color: var(--color-text-secondary);">
          <input type="checkbox" bind:checked={newScenario.integrity_impact} class="mr-1" />I
        </label>
        <label class="flex items-center text-xs" style="color: var(--color-text-secondary);">
          <input type="checkbox" bind:checked={newScenario.availability_impact} class="mr-1" />A
        </label>
      </div>
      <div class="flex justify-end space-x-2">
        <button type="button" on:click={resetForm} class="px-3 py-1 rounded text-xs" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);">Cancel</button>
        <button type="submit" class="px-3 py-1 rounded text-xs disabled:opacity-50 disabled:cursor-not-allowed" style="background: var(--color-accent-primary); color: var(--color-text-inverse);" disabled={!formValid}>Create</button>
      </div>
    </form>
  {/if}

  {#if damageScenarios.length === 0}
    <div class="text-center py-8 text-xs" style="color: var(--color-text-tertiary);">
      No damage scenarios created yet.
    </div>
  {:else}
    <div class="overflow-x-auto">
      <table class="min-w-full">
        <thead style="background: var(--color-bg-elevated);">
          <tr>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Name</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Asset</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">CIA</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">SFOP</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Overall</th>
            <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each damageScenarios as scenario}
            <tr style="border-bottom: 1px solid var(--color-border-subtle);">
              <td class="px-4 py-3">
                {#if editingCell?.scenarioId === scenario.scenario_id && editingCell?.field === 'name'}
                  <input bind:value={editingValue} on:keydown={(e) => handleKeyPress(e, scenario, 'name')} on:blur={() => saveEdit(scenario, 'name')} class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);" disabled={isSaving} autofocus />
                {:else}
                  <button on:click={() => startEdit(scenario, 'name')} class="text-left w-full px-2 py-1 rounded transition-colors">
                    <div class="text-xs font-medium flex items-center gap-2" style="color: var(--color-text-primary);">
                      {scenario.name}
                      {#if scenario.status === 'draft'}
                        <span class="px-1.5 py-0.5 text-[10px] rounded font-normal" style="background: color-mix(in srgb, var(--color-status-draft-text, #f59e0b) 15%, transparent); color: var(--color-status-draft-text, #f59e0b);">Draft</span>
                      {/if}
                    </div>
                  </button>
                {/if}
                {#if editingCell?.scenarioId === scenario.scenario_id && editingCell?.field === 'description'}
                  <textarea bind:value={editingValue} on:keydown={(e) => e.key === 'Enter' && e.ctrlKey && saveEdit(scenario, 'description')} on:blur={() => saveEdit(scenario, 'description')} class="w-full px-2 py-1 rounded resize-none mt-1 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);" rows="2" disabled={isSaving}></textarea>
                {:else if scenario.description}
                  <button on:click={() => startEdit(scenario, 'description')} class="text-left w-full px-2 py-1 rounded mt-1 transition-colors">
                    <div class="text-xs max-w-xs break-words" style="color: var(--color-text-tertiary);">{scenario.description}</div>
                  </button>
                {:else}
                  <button on:click={() => startEdit(scenario, 'description')} class="text-left w-full px-2 py-1 rounded mt-1 italic text-xs transition-colors" style="color: var(--color-text-tertiary);">Add description...</button>
                {/if}
              </td>
              <td class="px-4 py-3 text-sm">
                {#if editingCell?.scenarioId === scenario.scenario_id && editingCell?.field === 'primary_component_id'}
                  <select bind:value={editingValue} on:change={() => saveEdit(scenario, 'primary_component_id')} on:blur={() => saveEdit(scenario, 'primary_component_id')} class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);" disabled={isSaving} autofocus>
                    <option value="">No asset</option>
                    {#each assets as asset}<option value={asset.asset_id}>{asset.name}</option>{/each}
                  </select>
                {:else}
                  <button on:click={() => startEdit(scenario, 'primary_component_id')} class="text-left w-full px-2 py-1 rounded text-xs transition-colors" style="color: var(--color-text-secondary);">
                    {scenario.primary_component_id ? getAssetName(scenario.primary_component_id) : 'No asset'}
                  </button>
                {/if}
              </td>
              <td class="px-4 py-3">
                <div class="flex space-x-1">
                  <span class="px-2 py-1 text-[10px] rounded" style="{getCIABadgeStyle(scenario.confidentiality_impact)}">C</span>
                  <span class="px-2 py-1 text-[10px] rounded" style="{getCIABadgeStyle(scenario.integrity_impact)}">I</span>
                  <span class="px-2 py-1 text-[10px] rounded" style="{getCIABadgeStyle(scenario.availability_impact)}">A</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <div class="space-y-1">
                  {#each Object.entries(getSfopImpacts(scenario)) as [key, value]}
                    <div class="flex items-center space-x-1">
                      <span class="text-[10px] w-5" style="color: var(--color-text-tertiary);">{key.charAt(0).toUpperCase()}</span>
                      <span class="px-1 py-0.5 text-[10px] rounded" style="{getSfopBadgeStyle(value)}">{value}</span>
                    </div>
                  {/each}
                </div>
              </td>
              <td class="px-4 py-3">
                <span class="px-2 py-1 text-[10px] font-medium rounded" style="{getSfopBadgeStyle(getOverallSfopRating(scenario))}">{getOverallSfopRating(scenario)}</span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2 flex-wrap">
                  <WorkflowBadge
                    artifactType="damage_scenario"
                    artifactId={scenario.scenario_id}
                    scopeId={$selectedProduct?.scope_id || ''}
                  />
                  {#if scenario.status === 'draft'}
                    <button on:click={() => acceptScenario(scenario)} class="text-xs font-medium" style="color: var(--color-status-accepted-text, #10b981);">Accept</button>
                  {/if}
                  {#if canDelete}
                    <button on:click={() => confirmDelete(scenario)} class="text-xs" style="color: var(--color-error);">Delete</button>
                  {/if}
                </div>
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
