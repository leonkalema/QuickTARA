<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, Save, AlertTriangle } from '@lucide/svelte';
  import { 
    damageScenarioApi, 
    type DamageScenario, 
    type DamageScenarioCreate,
    DamageCategory,
    ImpactType,
    SeverityLevel
  } from '../../api/damage-scenarios';
  import { safeApiCall } from '../../utils/error-handler';
  import AssetSelector from './AssetSelector.svelte';
  import ThreatScenarioLinker from './ThreatScenarioLinker.svelte';

  // Props
  export let scenario: DamageScenario | null = null;
  export let selectedProductId: string;
  export let selectedProductName: string = '';

  // State
  let isLoading = false;
  let isSaving = false;
  let formData: DamageScenarioCreate = {
    name: '',
    description: '',
    damage_category: DamageCategory.OPERATIONAL,
    impact_type: ImpactType.DIRECT,
    confidentiality_impact: false,
    integrity_impact: false,
    availability_impact: false,
    severity: SeverityLevel.MEDIUM,
    impact_details: {},
    scope_id: selectedProductId || '',
    primary_component_id: '',
    affected_component_ids: [],
    version: 1,
    revision_notes: ''
  };
  let formErrors: Record<string, string> = {};
  let selectedAssetId: string | null = null;
  let selectedThreatId: string | null = null;
  let currentStep = 1;

  const dispatch = createEventDispatcher();

  onMount(() => {
    if (scenario) {
      initFormData();
    }
  });

  function initFormData() {
    if (scenario) {
      formData = {
        name: scenario.name || '',
        description: scenario.description || '',
        damage_category: scenario.damage_category || DamageCategory.OPERATIONAL,
        impact_type: scenario.impact_type || ImpactType.DIRECT,
        confidentiality_impact: scenario.confidentiality_impact || false,
        integrity_impact: scenario.integrity_impact || false,
        availability_impact: scenario.availability_impact || false,
        severity: scenario.severity || SeverityLevel.MEDIUM,
        impact_details: scenario.impact_details || {},
        scope_id: scenario.scope_id || selectedProductId || '',
        primary_component_id: scenario.primary_component_id || '',
        affected_component_ids: scenario.affected_component_ids || [],
        version: scenario.version || 1,
        revision_notes: ''
      };
      selectedAssetId = scenario.primary_component_id;
    }
  }

  function validateForm(): boolean {
    formErrors = {};
    
    if (!formData.name?.trim()) {
      formErrors.name = 'Name is required';
    }
    
    if (!formData.description?.trim()) {
      formErrors.description = 'Description is required';
    }
    
    if (!selectedAssetId) {
      formErrors.asset = 'Asset selection is required';
    }
    
    if (!formData.confidentiality_impact && !formData.integrity_impact && !formData.availability_impact) {
      formErrors.cia = 'At least one CIA property must be affected';
    }
    
    return Object.keys(formErrors).length === 0;
  }

  async function handleSubmit() {
    if (!validateForm()) return;
    
    isSaving = true;
    
    try {
      // Update form data with selected asset
      formData.primary_component_id = selectedAssetId || '';
      formData.affected_component_ids = selectedAssetId ? [selectedAssetId] : [];
      
      const result = scenario 
        ? await safeApiCall(() => damageScenarioApi.update(scenario!.scenario_id, formData))
        : await safeApiCall(() => damageScenarioApi.create(formData));
      
      if (result) {
        dispatch('submit', result);
      }
    } catch (err) {
      console.error('Error saving damage scenario:', err);
      formErrors.submit = 'Failed to save damage scenario. Please try again.';
    } finally {
      isSaving = false;
    }
  }

  function handleCancel() {
    dispatch('cancel');
  }

  function handleAssetSelected(event: CustomEvent) {
    selectedAssetId = event.detail.assetId;
    formData.primary_component_id = event.detail.assetId;
    formErrors.asset = '';
  }

  function handleAssetCleared() {
    selectedAssetId = null;
    formData.primary_component_id = '';
  }

  function handleThreatSelected(event: CustomEvent) {
    selectedThreatId = event.detail.threatId;
  }

  function handleThreatCleared() {
    selectedThreatId = null;
  }

  function nextStep() {
    if (currentStep < 4) currentStep++;
  }

  function prevStep() {
    if (currentStep > 1) currentStep--;
  }

  function canProceedToStep(step: number): boolean {
    switch (step) {
      case 2: return selectedAssetId !== null;
      case 3: return formData.name.trim() !== '' && formData.description?.trim() !== '';
      case 4: return formData.confidentiality_impact || formData.integrity_impact || formData.availability_impact;
      default: return true;
    }
  }
</script>

<div class="fixed inset-0 backdrop-blur-sm bg-neutral-900/40 flex items-center justify-center z-50 p-4">
  <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
    <!-- Header -->
    <div class="flex justify-between items-center px-6 py-4 bg-gray-50 border-b border-gray-200">
      <div>
        <h2 class="text-xl font-semibold text-gray-900">
          {scenario ? 'Edit' : 'Create'} Damage Scenario
        </h2>
        <p class="text-sm text-gray-600 mt-1">Step {currentStep} of 4</p>
      </div>
      <button 
        on:click={handleCancel}
        class="p-2 text-gray-500 hover:bg-gray-100 rounded-full transition-colors"
      >
        <X class="h-5 w-5" />
      </button>
    </div>

    <!-- Progress Steps -->
    <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
      <div class="flex items-center space-x-4">
        {#each [
          { num: 1, title: 'Select Asset' },
          { num: 2, title: 'Enter Details' },
          { num: 3, title: 'CIA Impact' },
          { num: 4, title: 'Link Threat' }
        ] as step}
          <div class="flex items-center">
            <div class="flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium
              {currentStep >= step.num ? 'bg-blue-600 text-white' : 
               canProceedToStep(step.num) ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-600'}">
              {step.num}
            </div>
            <span class="ml-2 text-sm font-medium text-gray-700">{step.title}</span>
            {#if step.num < 4}
              <div class="w-8 h-0.5 bg-gray-300 ml-4"></div>
            {/if}
          </div>
        {/each}
      </div>
    </div>

    <!-- Form Content -->
    <div class="p-6 overflow-y-auto max-h-[60vh]">
      {#if currentStep === 1}
        <!-- Step 1: Asset Selection -->
        <div class="mb-4">
          <h3 class="text-lg font-medium text-gray-900 mb-2">Select Asset for {selectedProductName}</h3>
          <p class="text-sm text-gray-600 mb-4">Choose one asset under this product for the damage scenario.</p>
        </div>
        <AssetSelector
          productId={selectedProductId}
          bind:selectedAssetId
          on:assetSelected={handleAssetSelected}
          on:assetCleared={handleAssetCleared}
        />
        {#if formErrors.asset}
          <p class="text-red-600 text-sm mt-2">{formErrors.asset}</p>
        {/if}
      
      {:else if currentStep === 2}
        <!-- Step 2: Basic Details -->
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
            <input
              type="text"
              bind:value={formData.name}
              placeholder="Enter damage scenario name"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {#if formErrors.name}
              <p class="text-red-600 text-sm mt-1">{formErrors.name}</p>
            {/if}
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description *</label>
            <textarea
              bind:value={formData.description}
              placeholder="Describe what happens in this damage scenario"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            ></textarea>
            {#if formErrors.description}
              <p class="text-red-600 text-sm mt-1">{formErrors.description}</p>
            {/if}
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select
                bind:value={formData.damage_category}
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {#each Object.values(DamageCategory) as category}
                  <option value={category}>{category}</option>
                {/each}
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Severity</label>
              <select
                bind:value={formData.severity}
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {#each Object.values(SeverityLevel) as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </div>
          </div>
        </div>

      {:else if currentStep === 3}
        <!-- Step 3: CIA Impact -->
        <div class="space-y-4">
          <h3 class="text-lg font-medium text-gray-900">Security Properties Affected</h3>
          <p class="text-sm text-gray-600">Select which security properties are impacted by this damage scenario.</p>
          
          <div class="space-y-3">
            <label class="flex items-center space-x-3">
              <input
                type="checkbox"
                bind:checked={formData.confidentiality_impact}
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span class="font-medium text-gray-900">Confidentiality</span>
                <p class="text-sm text-gray-600">Unauthorized disclosure of information</p>
              </div>
            </label>

            <label class="flex items-center space-x-3">
              <input
                type="checkbox"
                bind:checked={formData.integrity_impact}
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span class="font-medium text-gray-900">Integrity</span>
                <p class="text-sm text-gray-600">Unauthorized modification of information or systems</p>
              </div>
            </label>

            <label class="flex items-center space-x-3">
              <input
                type="checkbox"
                bind:checked={formData.availability_impact}
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span class="font-medium text-gray-900">Availability</span>
                <p class="text-sm text-gray-600">Disruption of access to information or systems</p>
              </div>
            </label>
          </div>
          
          {#if formErrors.cia}
            <p class="text-red-600 text-sm">{formErrors.cia}</p>
          {/if}
        </div>

      {:else if currentStep === 4}
        <!-- Step 4: Threat Scenario Linking -->
        <ThreatScenarioLinker
          bind:selectedThreatId
          on:threatSelected={handleThreatSelected}
          on:threatCleared={handleThreatCleared}
        />
      {/if}
    </div>

    <!-- Footer -->
    <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
      <div>
        {#if currentStep > 1}
          <button
            type="button"
            on:click={prevStep}
            class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
          >
            Previous
          </button>
        {/if}
      </div>

      <div class="flex space-x-3">
        <button
          type="button"
          on:click={handleCancel}
          class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>

        {#if currentStep < 4}
          <button
            type="button"
            on:click={nextStep}
            disabled={!canProceedToStep(currentStep + 1)}
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        {:else}
          <button
            type="button"
            on:click={handleSubmit}
            disabled={isSaving || !validateForm()}
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {#if isSaving}
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            {:else}
              <Save class="h-4 w-4" />
            {/if}
            <span>{scenario ? 'Update' : 'Create'} Scenario</span>
          </button>
        {/if}
      </div>
    </div>

    <!-- Error Display -->
    {#if formErrors.submit}
      <div class="px-6 py-3 bg-red-50 border-t border-red-200">
        <div class="flex items-center">
          <AlertTriangle class="h-5 w-5 text-red-600 mr-2" />
          <p class="text-red-700 text-sm">{formErrors.submit}</p>
        </div>
      </div>
    {/if}
  </div>
</div>
