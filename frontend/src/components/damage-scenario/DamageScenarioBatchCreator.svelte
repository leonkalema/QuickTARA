<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import BatchAssetSelector from './BatchAssetSelector.svelte';
  import BatchScenarioForm from './BatchScenarioForm.svelte';
  import { damageScenarioApi } from '../../api/damage-scenarios';
  import { safeApiCall } from '../../utils/error-handler';
  import type { DamageScenarioCreate, DamageCategory, ImpactType, SeverityLevel } from '../../api/damage-scenarios';

  export let selectedProductId: string;
  export let selectedProductName: string;

  const dispatch = createEventDispatcher();

  let currentStep = 1;
  let selectedAssets: string[] = [];
  let scenariosToCreate: Array<{
    componentId: string;
    name: string;
    description: string;
    confidentialityImpact: boolean;
    integrityImpact: boolean;
    availabilityImpact: boolean;
  }> = [];
  let isSaving = false;
  let error = '';

  function handleAssetsSelected(event: CustomEvent) {
    selectedAssets = event.detail.selectedAssets;
    // Create initial scenarios for selected assets
    scenariosToCreate = selectedAssets.map(assetId => ({
      componentId: assetId,
      name: `Asset Damage Scenario`,
      description: '',
      confidentialityImpact: false,
      integrityImpact: false,
      availabilityImpact: false
    }));
    currentStep = 2;
  }

  function handleBack() {
    currentStep = 1;
  }

  async function handleSubmit() {
    isSaving = true;
    error = '';
    
    try {
      const promises = scenariosToCreate.map(scenario => {
        const damageScenario: DamageScenarioCreate = {
          name: scenario.name,
          description: scenario.description,
          damage_category: 'Operational' as DamageCategory,
          impact_type: 'Direct' as ImpactType,
          confidentiality_impact: scenario.confidentialityImpact,
          integrity_impact: scenario.integrityImpact,
          availability_impact: scenario.availabilityImpact,
          severity: 'Medium' as SeverityLevel,
          scope_id: selectedProductId,
          primary_component_id: scenario.componentId,
          affected_component_ids: scenario.componentId ? [scenario.componentId] : [],
          version: 1,
          revision_notes: 'Initial creation via batch creator'
        };
        
        return safeApiCall(() => damageScenarioApi.create(damageScenario));
      });
      
      await Promise.all(promises);
      dispatch('complete');
    } catch (err) {
      error = 'Failed to create damage scenarios';
      console.error('Error creating scenarios:', err);
    } finally {
      isSaving = false;
    }
  }

  function handleCancel() {
    dispatch('cancel');
  }
</script>

<div class="bg-white rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
  <div class="px-6 py-4 border-b border-gray-200">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-lg font-semibold text-gray-900">Batch Create Damage Scenarios</h2>
        <p class="text-sm text-gray-600 mt-1">
          Product: <span class="font-medium">{selectedProductName}</span>
        </p>
      </div>
      <button 
        on:click={handleCancel}
        class="text-gray-400 hover:text-gray-600"
      >
        ✕
      </button>
    </div>
    
    <!-- Step indicator -->
    <div class="flex items-center mt-4 space-x-4">
      <div class="flex items-center">
        <div class="{currentStep >= 1 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-600'} 
                    rounded-full w-8 h-8 flex items-center justify-center text-sm font-medium">
          1
        </div>
        <span class="ml-2 text-sm {currentStep >= 1 ? 'text-gray-900' : 'text-gray-500'}">Select Assets</span>
      </div>
      
      <div class="flex-1 h-px bg-gray-200"></div>
      
      <div class="flex items-center">
        <div class="{currentStep >= 2 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-600'} 
                    rounded-full w-8 h-8 flex items-center justify-center text-sm font-medium">
          2
        </div>
        <span class="ml-2 text-sm {currentStep >= 2 ? 'text-gray-900' : 'text-gray-500'}">Define Scenarios</span>
      </div>
    </div>
  </div>
  
  <div class="p-6 overflow-y-auto" style="max-height: calc(90vh - 140px);">
    {#if error}
      <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">
        <p class="text-sm text-red-700">{error}</p>
      </div>
    {/if}
    
    {#if currentStep === 1}
      <BatchAssetSelector 
        {selectedProductId}
        {selectedProductName}
        on:assetsSelected={handleAssetsSelected}
      />
    {:else if currentStep === 2}
      <BatchScenarioForm 
        bind:scenariosToCreate
        {selectedAssets}
        {isSaving}
        on:submit={handleSubmit}
        on:back={handleBack}
      />
    {/if}
  </div>
</div>