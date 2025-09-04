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
    <div class="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Add Threat Scenario</h3>
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
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Threat Scenario Name *
            </label>
            <input
              type="text"
              bind:value={newThreatScenario.name}
              placeholder="e.g., Firmware injection via OBD-II"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <!-- Attack Vector -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Attack Vector *
            </label>
            <input
              type="text"
              bind:value={newThreatScenario.attack_vector}
              placeholder="e.g., OBD-II, CAN Bus, Physical Access"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Threat Description *
            </label>
            <textarea
              bind:value={newThreatScenario.description}
              placeholder="Describe how an attacker could cause this damage scenario..."
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button
            on:click={closeModal}
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            on:click={saveThreatScenario}
            disabled={!canSave() || isSaving}
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSaving ? 'Creating...' : 'Create Threat Scenario'}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
