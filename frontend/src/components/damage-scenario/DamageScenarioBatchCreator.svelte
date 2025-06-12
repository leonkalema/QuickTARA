<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { 
      damageScenarioApi, 
      DamageCategory, 
      ImpactType,
      SeverityLevel
    } from '../../api/damage-scenarios';
    import { productApi as scopeApi, type Product as Scope } from '../../api/products';
    import { assetApi, type Asset } from '../../api/assets';
    import { safeApiCall } from '../../utils/error-handler';
    import { showSuccess, showError } from '../ToastManager.svelte';
    import { X, ChevronRight, ChevronLeft, Plus, Save, Trash2 } from '@lucide/svelte';
    
    // No props needed - using events instead
    
    // Step management
    let currentStep = 1;
    const totalSteps = 3;
    
    // Data loading state
    let isLoading = true;
    let isSaving = false;
    
    // Step 1: Scope Selection
    let scopes: Scope[] = [];
    let selectedScopeId: string = '';
    
    // Step 2: Asset Selection
    let assets: Asset[] = [];
    let selectedAssets: string[] = [];
    
    // Step 3: Damage Scenarios
    let scenariosToCreate: Array<{
      componentId: string;
      name: string;
      description: string;
      confidentialityImpact: boolean;
      integrityImpact: boolean;
      availabilityImpact: boolean;
    }> = [];
    
    const dispatch = createEventDispatcher();
    
    onMount(async () => {
      await loadScopes();
    });
    
    async function loadScopes() {
      isLoading = true;
      try {
        const result = await safeApiCall(() => scopeApi.getAll());
        if (result) {
          scopes = (result as any).scopes || [];
        }
      } catch (error) {
        console.error('Error loading products:', error);
        showError('Failed to load products.');
      } finally {
        isLoading = false;
      }
    }
    
    async function loadAssets() {
      if (!selectedScopeId) return;
      // Reset previous selections
      assets = [];
      selectedAssets = [];
      scenariosToCreate = [];
      
      isLoading = true;
      try {
        const res = await safeApiCall(() => assetApi.getByProduct(selectedScopeId, 0, 100));
        if (res && Array.isArray((res as any).assets)) {
          assets = (res as any).assets;
        } else if (Array.isArray(res)) {
          assets = res as Asset[];
        }
      } catch (error) {
        console.error('Error loading assets:', error);
        showError('Failed to load assets.');
      } finally {
        isLoading = false;
      }
    }
    
    async function handleScopeSelect() {
      if (!selectedScopeId) {
        showError('Please select a scope to continue.');
        return;
      }
      isLoading = true;
      await loadAssets();
      currentStep = 2;
      // loadAssets already resets isLoading on finish
    }
    
    function handleAssetSelect() {
      if (selectedAssets.length === 0) {
        showError('Please select at least one asset.');
        return;
      }
      
      // Initialize scenario templates for each selected asset
      scenariosToCreate = selectedAssets.map(assetId => {
        const asset = assets.find(a => a.asset_id === assetId);
        return {
          componentId: assetId,
          name: `${asset?.name || 'Asset'} Damage Scenario`,
          description: '',
          confidentialityImpact: false,
          integrityImpact: false,
          availabilityImpact: false
        };
      });
      
      currentStep = 3;
    }
    
    function addScenarioForAsset(assetId: string) {
      const asset = assets.find(a => a.asset_id === assetId);
      scenariosToCreate.push({
        componentId: assetId,
        name: `${asset?.name || 'Asset'} Damage Scenario ${
          scenariosToCreate.filter(s => s.componentId === assetId).length + 1
        }`,
        description: '',
        confidentialityImpact: false,
        integrityImpact: false,
        availabilityImpact: false
      });
      scenariosToCreate = [...scenariosToCreate];
    }
    
    function removeScenario(index: number) {
      scenariosToCreate.splice(index, 1);
      scenariosToCreate = [...scenariosToCreate];
    }
    
    async function handleSubmit() {
      // Validate that each scenario has at least one CIA impact
      const invalidScenarios = scenariosToCreate.filter(
        scenario => !scenario.confidentialityImpact && !scenario.integrityImpact && !scenario.availabilityImpact
      );
      
      if (invalidScenarios.length > 0) {
        showError('Each scenario must have at least one security property (CIA) impacted.');
        return;
      }
      
      // Validate descriptions
      const emptyDescriptions = scenariosToCreate.filter(
        scenario => !scenario.description.trim()
      );
      
      if (emptyDescriptions.length > 0) {
        showError('Please provide a description for all scenarios.');
        return;
      }
      
      isSaving = true;
      const createdScenarios = [];
      
      try {
        // Create each scenario
        for (const scenario of scenariosToCreate) {
          const scenarioData = {
            name: scenario.name,
            description: scenario.description,
            scope_id: selectedScopeId,
            primary_component_id: scenario.componentId,
            affected_component_ids: [scenario.componentId],
            confidentiality_impact: scenario.confidentialityImpact,
            integrity_impact: scenario.integrityImpact,
            availability_impact: scenario.availabilityImpact,
            // Default values for other required fields
            damage_category: DamageCategory.OPERATIONAL,
            impact_type: ImpactType.DIRECT,
            severity: SeverityLevel.MEDIUM
          };
          
          const result = await safeApiCall(() => damageScenarioApi.create(scenarioData));
          if (result) {
            createdScenarios.push(result);
          }
        }
        
        showSuccess(`Created ${createdScenarios.length} damage scenarios.`);
        dispatch('complete');
      } catch (error) {
        console.error('Error saving scenarios:', error);
        showError('Failed to save some damage scenarios.');
      } finally {
        isSaving = false;
      }
    }
    
    function getAssetName(assetId: string): string {
      const asset = assets.find(a => a.asset_id === assetId);
      return asset ? asset.name : 'Unknown Asset';
    }
    
    function cancel() {
      dispatch('cancel');
    }
  </script>
  <div class="bg-white p-6 rounded-lg shadow-md border border-gray-200 w-full mb-6 space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center border-b border-gray-200 pb-4">
      <h2 class="text-xl font-semibold text-gray-900">Create Damage Scenarios</h2>
      <button on:click={cancel} class="text-gray-400 hover:text-gray-500">
        <X size={20} />
      </button>
    </div>
    
    <!-- Progress Bar -->
    <div class="pt-2">
      <div class="flex items-center mb-4">
        <div class="flex-1">
          <div class="relative">
            <div class="h-2 bg-gray-200 rounded-full">
              <div 
                class="h-2 bg-primary rounded-full transition-all duration-300"
                style="width: {(currentStep / totalSteps) * 100}%"
              ></div>
            </div>
            <div class="absolute top-0 left-0 flex justify-between w-full transform -translate-y-full">
              <span class={`text-xs font-medium ${currentStep >= 1 ? 'text-primary' : 'text-gray-500'}`}>
                1. Select Scope
              </span>
              <span class={`text-xs font-medium ${currentStep >= 2 ? 'text-primary' : 'text-gray-500'}`}>
                2. Select Assets
              </span>
              <span class={`text-xs font-medium ${currentStep >= 3 ? 'text-primary' : 'text-gray-500'}`}>
                3. Define Scenarios
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Content -->
    <div>
      {#if isLoading}
        <div class="flex justify-center items-center h-40">
          <div class="loader"></div>
        </div>
      {:else}
        {#if currentStep === 1}
          <div class="space-y-4">
            <h3 class="text-md font-medium text-gray-900">Select a Scope</h3>
            <p class="text-sm text-gray-600">
              Choose the scope for which you want to create damage scenarios.
            </p>
            
            {#if scopes.length === 0}
              <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <p class="text-sm text-yellow-700">
                  No scopes available. Please create a scope first.
                </p>
              </div>
            {:else}
              <div class="grid grid-cols-1 gap-4 max-h-96 overflow-y-auto">
                {#each scopes as scope}
                  <div 
                    class="border rounded-lg p-4 cursor-pointer transition-colors
                      ${selectedScopeId === scope.scope_id ? 
                        'border-primary bg-primary-50' : 
                        'border-gray-200 hover:bg-gray-50'}"
                    on:click={() => selectedScopeId = scope.scope_id}
                  >
                    <div class="flex items-center justify-between">
                      <div>
                        <h4 class="font-medium text-gray-900">{scope.name}</h4>
                      </div>
                      
                      <div class="flex items-center h-5">
                        <input
                          type="radio"
                          name="scope"
                          value={scope.scope_id}
                          bind:group={selectedScopeId}
                          class="form-radio h-4 w-4 text-primary border-gray-300"
                        />
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
          
          <!-- Step 1 Actions -->
          <div class="flex justify-end space-x-3 pt-4 mt-4 border-t border-gray-200">
            <button 
              type="button"
              on:click={cancel}
              class="btn btn-secondary"
            >
              Cancel
            </button>
            <button 
              type="button"
              on:click={handleScopeSelect}
              class="btn btn-primary flex items-center gap-1"
              disabled={!selectedScopeId || isLoading}
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        {/if}
        {#if currentStep === 2}
        <div class="space-y-4">
          <h3 class="text-md font-medium text-gray-900">Select Assets</h3>
          <p class="text-sm text-gray-600">
            Select one or more assets to create damage scenarios for.
          </p>
          
          {#if assets.length === 0}
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <p class="text-sm text-yellow-700">
                No assets available for this scope. Please create assets first.
              </p>
            </div>
          {:else}
            <div class="max-h-96 overflow-y-auto border rounded-lg">
              {#each assets as asset}
                <div 
                  class="p-4 flex items-center border-b last:border-b-0 hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    value={asset.asset_id}
                    bind:group={selectedAssets}
                    class="form-checkbox h-5 w-5 text-primary border-gray-300 rounded"
                  />
                  <div class="ml-3 flex-1">
                    <span class="block text-sm font-medium text-gray-900">
                      {asset.name}
                    </span>
                    <span class="block text-xs text-gray-600">
                      {asset.asset_type || 'No type'}
                    </span>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
        
        <!-- Step 2 Actions -->
        <div class="flex justify-between pt-4 mt-4 border-t border-gray-200">
          <button 
            type="button"
            on:click={() => currentStep = 1}
            class="btn btn-secondary flex items-center gap-1"
          >
            <ChevronLeft size={16} /> Back
          </button>
          
          <button 
            type="button"
            on:click={handleAssetSelect}
            class="btn btn-primary flex items-center gap-1"
            disabled={selectedAssets.length === 0 || isLoading}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      {/if}
      {#if currentStep === 3}
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
              
              <!-- Description field - emphasis on importance -->
              <div class="mt-3">
                <label for="desc-{index}" class="block text-sm font-medium text-gray-700 mb-1">
                  Description <span class="text-red-500">*</span>
                </label>
                <textarea
                  id="desc-{index}"
                  bind:value={scenario.description}
                  rows="3"
                  class="form-textarea w-full rounded-md border-gray-300"
                  placeholder="Describe what could happen if security properties are compromised. Include all information needed for later assessment: item functionality, adverse consequences, and description of harm."
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
    </div>
    
    <!-- Step 3 Actions -->
    <div class="flex justify-between pt-4 mt-4 border-t border-gray-200">
      <button 
        type="button"
        on:click={() => currentStep = 2}
        class="btn btn-secondary flex items-center gap-1"
      >
        <ChevronLeft size={16} /> Back
      </button>
      
      <button 
        type="button"
        on:click={handleSubmit}
        class="btn btn-primary flex items-center gap-1"
        disabled={scenariosToCreate.length === 0 || isSaving}
      >
        {#if isSaving}
          <div class="loader-sm"></div>
          Saving...
        {:else}
          <Save size={16} /> Save All Scenarios
        {/if}
      </button>
    </div>
  {/if}
{/if}
</div>
</div>

<style>
.loader {
border: 4px solid #f3f3f3;
border-radius: 50%;
border-top: 4px solid var(--color-primary);
width: 30px;
height: 30px;
animation: spin 1s linear infinite;
}

.loader-sm {
border: 2px solid #f3f3f3;
border-radius: 50%;
border-top: 2px solid #fff;
width: 16px;
height: 16px;
animation: spin 1s linear infinite;
}

@keyframes spin {
0% { transform: rotate(0deg); }
100% { transform: rotate(360deg); }
}
</style>