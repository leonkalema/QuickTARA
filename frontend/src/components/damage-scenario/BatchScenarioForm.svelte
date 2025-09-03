<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Save, Trash2, Plus } from '@lucide/svelte';

  export let scenariosToCreate: Array<{
    componentId: string;
    name: string;
    description: string;
    confidentialityImpact: boolean;
    integrityImpact: boolean;
    availabilityImpact: boolean;
  }> = [];
  export let selectedAssets: string[] = [];
  export let isSaving = false;

  const dispatch = createEventDispatcher();

  function getAssetName(assetId: string): string {
    // This will be passed from parent or we can make it a prop
    return `Asset ${assetId}`;
  }

  function removeScenario(index: number) {
    scenariosToCreate.splice(index, 1);
    scenariosToCreate = [...scenariosToCreate];
  }

  function addScenarioForAsset(assetId: string) {
    scenariosToCreate.push({
      componentId: assetId,
      name: `Asset Damage Scenario ${scenariosToCreate.filter(s => s.componentId === assetId).length + 1}`,
      description: '',
      confidentialityImpact: false,
      integrityImpact: false,
      availabilityImpact: false
    });
    scenariosToCreate = [...scenariosToCreate];
  }

  function handleSubmit() {
    dispatch('submit');
  }

  function handleBack() {
    dispatch('back');
  }
</script>

<div class="space-y-4">
  <h3 class="text-md font-medium text-gray-900">Define Damage Scenarios</h3>
  <p class="text-sm text-gray-600">
    Configure the damage scenarios for the selected assets. 
    Each scenario must have at least one security property impacted.
  </p>
  
  <div class="space-y-6 max-h-[500px] overflow-y-auto pr-2">
    {#each scenariosToCreate as scenario, index}
      <div class="border rounded-lg p-4">
        <div class="flex justify-between items-start">
          <h4 class="font-medium text-gray-900">
            {getAssetName(scenario.componentId)}
          </h4>
          <button 
            on:click={() => removeScenario(index)} 
            class="text-gray-400 hover:text-red-500"
            title="Remove scenario"
          >
            <Trash2 size={16} />
          </button>
        </div>
        
        <!-- Name field -->
        <div class="mt-3">
          <label for="name-{index}" class="block text-sm font-medium text-gray-700 mb-1">
            Name
          </label>
          <input
            id="name-{index}"
            type="text"
            bind:value={scenario.name}
            class="form-input w-full rounded-md border-gray-300"
            placeholder="Scenario name"
          />
        </div>
        
        <!-- Description field -->
        <div class="mt-3">
          <label for="desc-{index}" class="block text-sm font-medium text-gray-700 mb-1">
            Description <span class="text-red-500">*</span>
          </label>
          <textarea
            id="desc-{index}"
            bind:value={scenario.description}
            rows="3"
            class="form-textarea w-full rounded-md border-gray-300"
            placeholder="Describe what could happen if security properties are compromised."
          ></textarea>
        </div>
        
        <!-- Security Properties -->
        <div class="mt-3">
          <span class="block text-sm font-medium text-gray-700 mb-1">
            Security Properties Impacted <span class="text-red-500">*</span>
          </span>
          <div class="flex space-x-4">
            <label class="inline-flex items-center">
              <input 
                type="checkbox" 
                bind:checked={scenario.confidentialityImpact}
                class="form-checkbox h-4 w-4 text-primary rounded border-gray-300"
              />
              <span class="ml-2 text-sm text-gray-700">Confidentiality</span>
            </label>
            
            <label class="inline-flex items-center">
              <input 
                type="checkbox" 
                bind:checked={scenario.integrityImpact}
                class="form-checkbox h-4 w-4 text-primary rounded border-gray-300"
              />
              <span class="ml-2 text-sm text-gray-700">Integrity</span>
            </label>
            
            <label class="inline-flex items-center">
              <input 
                type="checkbox" 
                bind:checked={scenario.availabilityImpact}
                class="form-checkbox h-4 w-4 text-primary rounded border-gray-300"
              />
              <span class="ml-2 text-sm text-gray-700">Availability</span>
            </label>
          </div>
        </div>
      </div>
    {/each}
  </div>
  
  <!-- Add more scenarios buttons -->
  <div class="flex flex-wrap gap-2">
    {#each selectedAssets as assetId}
      <button 
        type="button"
        on:click={() => addScenarioForAsset(assetId)}
        class="btn btn-sm btn-outline flex items-center gap-1"
      >
        <Plus size={14} /> Add for {getAssetName(assetId)}
      </button>
    {/each}
  </div>
  
  <!-- Actions -->
  <div class="flex justify-between pt-4 mt-4 border-t border-gray-200">
    <button 
      type="button"
      on:click={handleBack}
      class="btn btn-secondary flex items-center gap-1"
    >
      ← Back
    </button>
    
    <button 
      type="button"
      on:click={handleSubmit}
      class="btn btn-primary flex items-center gap-1"
      disabled={scenariosToCreate.length === 0 || isSaving}
    >
      {#if isSaving}
        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
        Saving...
      {:else}
        <Save size={16} /> Save All Scenarios
      {/if}
    </button>
  </div>
</div>
