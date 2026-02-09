<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { threatScenarioApi } from '../lib/api/threatScenarioApi';
  import { notifications } from '../lib/stores/notificationStore';
  import type { CreateThreatScenarioRequest, ThreatScenario } from '../lib/types/threatScenario';
  
  export let isOpen = false;
  export let damageScenarioId: string;
  export let productId: string;
  export let productVersion: number = 1;
  
  const dispatch = createEventDispatcher();
  
  let newThreatScenario: CreateThreatScenarioRequest = {
    damage_scenario_id: damageScenarioId,
    name: '',
    description: '',
    attack_vector: '',
    scope_id: productId,
    scope_version: productVersion
  };
  
  let isSaving = false;
  
  $: {
    if (isOpen) {
      newThreatScenario.damage_scenario_id = damageScenarioId;
      newThreatScenario.scope_id = productId;
      newThreatScenario.scope_version = productVersion;
    }
  }
  
  function resetForm() {
    newThreatScenario = {
      damage_scenario_id: damageScenarioId,
      name: '',
      description: '',
      attack_vector: '',
      scope_id: productId,
      scope_version: productVersion
    };
  }
  
  function closeModal() {
    isOpen = false;
    resetForm();
  }
  
  async function saveThreatScenario() {
    if (!canSave()) return;
    
    isSaving = true;
    try {
      const created = await threatScenarioApi.createThreatScenario(newThreatScenario);
      notifications.show(`Threat scenario ${created.threat_scenario_id} created successfully`, 'success');
      dispatch('threatScenarioCreated', created);
      closeModal();
    } catch (error) {
      console.error('Error creating threat scenario:', error);
      notifications.show('Failed to create threat scenario', 'error');
    } finally {
      isSaving = false;
    }
  }
  
  function canSave(): boolean {
    return newThreatScenario.name.trim() !== '' && 
           newThreatScenario.description.trim() !== '' &&
           newThreatScenario.attack_vector.trim() !== '';
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
    <div class="relative top-20 mx-auto p-5 w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
      <div class="mt-3">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">Add Threat Scenario</h3>
          <button
            on:click={closeModal}
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <!-- Threat Scenario Name -->
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
              Threat Scenario Name *
            </label>
            <input
              type="text"
              bind:value={newThreatScenario.name}
              placeholder="e.g., Firmware injection via OBD-II"
              class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
            />
          </div>
          
          <!-- Attack Vector -->
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
              Attack Vector *
            </label>
            <input
              type="text"
              bind:value={newThreatScenario.attack_vector}
              placeholder="e.g., OBD-II, CAN Bus, Physical Access"
              class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
            />
          </div>
          
          <!-- Description -->
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
              Threat Description *
            </label>
            <textarea
              bind:value={newThreatScenario.description}
              placeholder="Describe how an attacker could cause this damage scenario..."
              rows="4"
              class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
            ></textarea>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button
            on:click={closeModal}
            class="px-4 py-2 text-xs font-medium rounded-md" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
          >
            Cancel
          </button>
          <button
            on:click={saveThreatScenario}
            disabled={!canSave() || isSaving}
            class="px-4 py-2 text-xs font-medium rounded-md disabled:opacity-50 disabled:cursor-not-allowed" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
          >
            {isSaving ? 'Creating...' : 'Create Threat Scenario'}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
