<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, AlertTriangle, Save, Trash2, Loader2 } from '@lucide/svelte';
  import { 
    damageScenarioApi, 
    type DamageScenario, 
    type DamageScenarioCreate,
    type PropagationSuggestion,
    DamageCategory,
    ImpactType,
    SeverityLevel
  } from '../../api/damage-scenarios';
  import { safeApiCall } from '../../utils/error-handler';
  import AssetSelector from './AssetSelector.svelte';
  import ThreatScenarioLinker from './ThreatScenarioLinker.svelte';
  import { scopeApi, type Scope } from '../../api/scopes';
  import { componentApi, type Component } from '../../api/components';
  import { showError } from '../ToastManager.svelte';
  
  // Props
  export let scenario: DamageScenario | null = null;
  export let scopeId: string | undefined = undefined;
  export let componentId: string | undefined = undefined;
  
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
    scope_id: scopeId || '',
    primary_component_id: componentId || '',
    affected_component_ids: componentId ? [componentId] : [],
    version: 1,
    revision_notes: ''
  };
  let scopes: Scope[] = [];
  let formErrors: Record<string, string> = {};
  let selectedAssetId: string | null = null;
  let selectedThreatId: string | null = null;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Initialize form data
  function initFormData() {
    if (scenario) {
      // Edit mode - use existing scenario data
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
        scope_id: scenario.scope_id || scopeId || '',
        primary_component_id: scenario.primary_component_id || componentId || '',
        affected_component_ids: scenario.affected_component_ids ? [...scenario.affected_component_ids] : (componentId ? [componentId] : []),
        version: scenario.version || 1,
        revision_notes: ''
      };
    }
    // Note: We don't need an else clause as formData is already initialized with defaults
  }
  
  onMount(async () => {
    isLoading = true;
    
    try {
      // Initialize form data
      initFormData();
      
      // Load scopes and components in parallel
      const [scopesResult, componentsResult] = await Promise.all([
        safeApiCall(() => scopeApi.getAll()),
        safeApiCall(() => componentApi.getAll())
      ]);
      
      if (scopesResult) {
        scopes = scopesResult.scopes || [];
        
        // If no scope is selected and we have scopes, select the first one
        if (!formData.scope_id && scopes.length > 0) {
          formData.scope_id = scopes[0].scope_id;
        }
      }
      
      if (componentsResult) {
        allComponents = Array.isArray(componentsResult) ? componentsResult : [];
        // Initial component list filtered by current scope (if any)
        components = formData.scope_id
          ? allComponents.filter(c => c.scope_id === formData.scope_id)
          : allComponents;
        
        // If no primary component is selected and we have components, select the first one
        if (!formData.primary_component_id && components.length > 0) {
          formData.primary_component_id = components[0].component_id;
          
          // Add primary component to affected components if it's not already there
          if (!formData.affected_component_ids.includes(components[0].component_id)) {
            formData.affected_component_ids = [...formData.affected_component_ids, components[0].component_id];
          }
        }
      }
      
      // If we have a primary component, get propagation suggestions
      if (formData.primary_component_id && formData.primary_component_id.trim() !== '') {
        await loadPropagationSuggestions();
      }
    } catch (err) {
      console.error('Error initializing form:', err);
      showError('Failed to load form data. Please try again.');
    } finally {
      isLoading = false;
    }
  });
  
  async function loadPropagationSuggestions() {
    if (!formData.primary_component_id || formData.primary_component_id.trim() === '') return;
    
    isPropagationLoading = true;
    
    try {
      const result = await safeApiCall(() => damageScenarioApi.getPropagationSuggestions(
        formData.primary_component_id,
        {
          confidentiality: formData.confidentiality_impact,
          integrity: formData.integrity_impact,
          availability: formData.availability_impact
        }
      ));
      
      if (result) {
        propagationSuggestions = result.suggestions;
      }
    } catch (err) {
      console.error('Error loading propagation suggestions:', err);
    } finally {
      isPropagationLoading = false;
    }
  }
  
  function handleCancel() {
    dispatch('cancel');
  }
  
  function validateForm(): boolean {
    formErrors = {};
    
    // Required fields
    if (!formData.name.trim()) {
      formErrors.name = 'Name is required';
    }
    
    if (!formData.scope_id) {
      formErrors.scope_id = 'Scope is required';
    }
    
    if (!formData.primary_component_id) {
      formErrors.primary_component_id = 'Primary component is required';
    }
    
    // At least one CIA impact must be selected
    if (!formData.confidentiality_impact && !formData.integrity_impact && !formData.availability_impact) {
      formErrors.cia = 'At least one CIA impact must be selected';
    }
    
    // Primary component must be in affected components
    if (formData.primary_component_id && !formData.affected_component_ids.includes(formData.primary_component_id)) {
      formData.affected_component_ids = [...formData.affected_component_ids, formData.primary_component_id];
    }
    
    return Object.keys(formErrors).length === 0;
  }
  
  async function handleSubmit() {
    if (!validateForm()) {
      return;
    }
    
    isSaving = true;
    
    try {
      // Dispatch the form data to parent component
      dispatch('submit', formData);
    } catch (err) {
      console.error('Error submitting form:', err);
      showError('Failed to save damage scenario. Please try again.');
    } finally {
      isSaving = false;
    }
  }
  
  function handlePrimaryComponentChange() {
    // Add primary component to affected components if it's not already there
    if (formData.primary_component_id && formData.primary_component_id.trim() !== '' && 
        !formData.affected_component_ids.includes(formData.primary_component_id)) {
      formData.affected_component_ids = [...formData.affected_component_ids, formData.primary_component_id];
    }
    
    // Load propagation suggestions for the new primary component
    loadPropagationSuggestions();
  }
  
  function handleCIAChange() {
    // If CIA impacts change, refresh propagation suggestions
    loadPropagationSuggestions();
  }
  
  function handleApplySuggestions() {
    // Add suggested components to affected components
    const newAffectedComponents = [...formData.affected_component_ids];
    
    for (const suggestion of propagationSuggestions) {
      if (!newAffectedComponents.includes(suggestion.target_component_id)) {
        newAffectedComponents.push(suggestion.target_component_id);
      }
    }
    
    formData.affected_component_ids = newAffectedComponents;
  }
  
  function toggleAffectedComponent(componentId: string) {
    if (!componentId || componentId === formData.primary_component_id) {
      // Can't remove primary component from affected components
      return;
    }
    
    if (formData.affected_component_ids.includes(componentId)) {
      // Remove component
      formData.affected_component_ids = formData.affected_component_ids.filter(id => id !== componentId);
    } else {
      // Add component
      formData.affected_component_ids = [...formData.affected_component_ids, componentId];
    }
  }
  
  /**
   * Load components for a specific scope – client-side filtering only
   */
  async function loadComponentsForScope(scopeId: string) {
    // No extra network call – just filter the cached list
    components = scopeId ? allComponents.filter(c => c.scope_id === scopeId) : allComponents;
  }
  
  function getComponentName(componentId: string): string {
    const component = allComponents.find(c => c.component_id === componentId);
    return component ? component.name : 'Unknown Component';
  }
</script>

<div class="bg-white rounded-lg shadow-lg overflow-hidden max-w-3xl mx-auto">
  <div class="flex justify-between items-center px-6 py-4 bg-gray-50 border-b border-gray-200">
    <h2 class="text-lg font-medium text-gray-900">
      {scenario ? 'Edit Damage Scenario' : 'Create Damage Scenario'}
    </h2>
    <button 
      on:click={handleCancel}
      class="text-gray-400 hover:text-gray-500"
    >
      <X size={20} />
    </button>
  </div>
  
  {#if isLoading}
    <div class="p-6 flex justify-center items-center h-64">
      <Loader2 size={36} class="animate-spin text-primary" />
    </div>
  {:else}
    <form on:submit|preventDefault={handleSubmit} class="p-6 space-y-6">
      <!-- Basic Information -->
      <div class="space-y-4">
        <h3 class="text-md font-medium text-gray-900 border-b pb-2">Basic Information</h3>
        
        <!-- Name -->
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name *</label>
          <input
            type="text"
            id="name"
            bind:value={formData.name}
            class="form-input w-full rounded-md border-gray-300 {formErrors.name ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}"
            placeholder="Enter scenario name"
          />
          {#if formErrors.name}
            <p class="mt-1 text-sm text-red-600">{formErrors.name}</p>
          {/if}
        </div>
        
        <!-- Description -->
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            id="description"
            bind:value={formData.description}
            rows="3"
            class="form-textarea w-full rounded-md border-gray-300"
            placeholder="Describe the damage scenario"
          ></textarea>
        </div>
        
        <!-- Scope -->
        <div>
          <label for="scope" class="block text-sm font-medium text-gray-700 mb-1">Scope *</label>
          <select
            id="scope"
            bind:value={formData.scope_id}
            class="form-select w-full rounded-md border-gray-300 {formErrors.scope_id ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}"
          >
            <option value={null}>All Scopes</option>
            {#each scopes as scope}
              <option value={scope.scope_id}>{scope.name}</option>
            {/each}
          </select>
          {#if formErrors.scope_id}
            <p class="mt-1 text-sm text-red-600">{formErrors.scope_id}</p>
          {/if}
        </div>
      </div>
      
      <!-- Impact Details -->
      <div class="space-y-4">
        <h3 class="text-md font-medium text-gray-900 border-b pb-2">Impact Details</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Damage Category -->
          <div>
            <label for="damage-category" class="block text-sm font-medium text-gray-700 mb-1">Damage Category *</label>
            <select
              id="damage-category"
              bind:value={formData.damage_category}
              class="form-select w-full rounded-md border-gray-300"
            >
              {#each Object.values(DamageCategory) as category}
                <option value={category}>{category}</option>
              {/each}
            </select>
          </div>
          
          <!-- Impact Type -->
          <div>
            <label for="impact-type" class="block text-sm font-medium text-gray-700 mb-1">Impact Type *</label>
            <select
              id="impact-type"
              bind:value={formData.impact_type}
              class="form-select w-full rounded-md border-gray-300"
            >
              {#each Object.values(ImpactType) as type}
                <option value={type}>{type}</option>
              {/each}
            </select>
          </div>
        </div>
        
        <!-- Severity -->
        <div>
          <label for="severity" class="block text-sm font-medium text-gray-700 mb-1">Severity *</label>
          <select
            id="severity"
            bind:value={formData.severity}
            class="form-select w-full rounded-md border-gray-300"
          >
            {#each Object.values(SeverityLevel) as level}
              <option value={level}>{level}</option>
            {/each}
          </select>
        </div>
        
        <!-- CIA Impact -->
        <div>
          <span class="block text-sm font-medium text-gray-700 mb-2">CIA Impact *</span>
          <div class="flex flex-wrap gap-4">
            <label class="inline-flex items-center" for="confidentiality-impact">
              <input 
                id="confidentiality-impact"
                type="checkbox" 
                bind:checked={formData.confidentiality_impact}
                on:change={handleCIAChange}
                class="form-checkbox h-5 w-5 text-blue-600 rounded border-gray-300"
              />
              <span class="ml-2 text-sm text-gray-700">Confidentiality</span>
            </label>
            <label class="inline-flex items-center" for="integrity-impact">
              <input 
                id="integrity-impact"
                type="checkbox" 
                bind:checked={formData.integrity_impact}
                on:change={handleCIAChange}
                class="form-checkbox h-5 w-5 text-green-600 rounded border-gray-300"
              />
              <span class="ml-2 text-sm text-gray-700">Integrity</span>
            </label>
            <label class="inline-flex items-center" for="availability-impact">
              <input 
                id="availability-impact"
                type="checkbox" 
                bind:checked={formData.availability_impact}
                on:change={handleCIAChange}
                class="form-checkbox h-5 w-5 text-purple-600 rounded border-gray-300"
              />
              <span class="ml-2 text-sm text-gray-700">Availability</span>
            </label>
          </div>
          {#if formErrors.cia}
            <p class="mt-1 text-sm text-red-600">{formErrors.cia}</p>
          {/if}
        </div>
      </div>
      
      <!-- Component Selection -->
      <div class="space-y-4">
        <h3 class="text-md font-medium text-gray-900 border-b pb-2">Component Selection</h3>
        
        <!-- Primary Component -->
        <div>
          <label for="primary-component" class="block text-sm font-medium text-gray-700 mb-1">Primary Component *</label>
          <select
            id="primary-component"
            bind:value={formData.primary_component_id}
            on:change={handlePrimaryComponentChange}
            class="form-select w-full rounded-md border-gray-300 {formErrors.primary_component_id ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}"
          >
            <option value="">Select a component</option>
            {#each components as component}
              <option value={component.component_id}>{component.name}</option>
            {/each}
          </select>
          {#if formErrors.primary_component_id}
            <p class="mt-1 text-sm text-red-600">{formErrors.primary_component_id}</p>
          {/if}
        </div>
        
        <!-- Propagation Suggestions -->
        {#if formData && formData.primary_component_id}
          <div class="bg-gray-50 p-4 rounded-md border border-gray-200">
            <div class="flex justify-between items-center mb-2">
              <h4 class="text-sm font-medium text-gray-700">Impact Propagation</h4>
              <button 
                type="button"
                on:click={() => showPropagationSuggestions = !showPropagationSuggestions}
                class="text-sm text-indigo-600 hover:text-indigo-800"
              >
                {showPropagationSuggestions ? 'Hide Suggestions' : 'Show Suggestions'}
              </button>
            </div>
            
            {#if showPropagationSuggestions}
              {#if isPropagationLoading}
                <div class="flex justify-center items-center py-4">
                  <Loader2 size={24} class="animate-spin text-primary" />
                </div>
              {:else if propagationSuggestions.length === 0}
                <p class="text-sm text-gray-500 py-2">No propagation suggestions available. Try selecting different CIA impacts.</p>
              {:else}
                <div class="mb-3">
                  <p class="text-sm text-gray-600 mb-2">
                    Based on component connections, the following components may be affected:
                  </p>
                  <button 
                    type="button"
                    on:click={handleApplySuggestions}
                    class="text-sm bg-indigo-50 text-indigo-700 px-3 py-1 rounded-md hover:bg-indigo-100"
                  >
                    Apply All Suggestions
                  </button>
                </div>
                <ul class="space-y-2 max-h-40 overflow-y-auto">
                  {#each propagationSuggestions as suggestion}
                    <li class="text-sm flex items-start">
                      <input 
                        type="checkbox" 
                        checked={formData.affected_component_ids.includes(suggestion.target_component_id)}
                        on:change={() => toggleAffectedComponent(suggestion.target_component_id)}
                        class="form-checkbox h-4 w-4 mt-1 text-indigo-600 rounded border-gray-300"
                      />
                      <div class="ml-2">
                        <p class="font-medium">{getComponentName(suggestion.target_component_id)}</p>
                        <p class="text-xs text-gray-500">
                          {suggestion.impact_type} impact with {suggestion.severity} severity (Confidence: {Math.round(suggestion.confidence * 100)}%)
                        </p>
                      </div>
                    </li>
                  {/each}
                </ul>
              {/if}
            {/if}
          </div>
        {/if}
        
        <!-- Affected Components -->
        <div>
          <span class="block text-sm font-medium text-gray-700 mb-2">Affected Components</span>
          <div class="bg-white border border-gray-200 rounded-md p-2 max-h-40 overflow-y-auto">
            {#if components.length === 0}
              <p class="text-sm text-gray-500 p-2">No components available</p>
            {:else}
              <ul class="space-y-1">
                {#each components as component}
                  <li>
                    <label class="inline-flex items-center w-full" for="component-{component.component_id}">
                      <input 
                        id="component-{component.component_id}"
                        type="checkbox" 
                        checked={formData.affected_component_ids.includes(component.component_id)}
                        disabled={component.component_id === formData.primary_component_id}
                        on:change={() => toggleAffectedComponent(component.component_id)}
                        class="form-checkbox h-4 w-4 text-indigo-600 rounded border-gray-300"
                      />
                      <span class="ml-2 text-sm text-gray-700 {component.component_id === formData.primary_component_id ? 'font-medium' : ''}">
                        {component.name}
                        {#if component.component_id === formData.primary_component_id}
                          <span class="text-xs text-indigo-600 ml-1">(Primary)</span>
                        {/if}
                      </span>
                    </label>
                  </li>
                {/each}
              </ul>
            {/if}
          </div>
        </div>
      </div>
      
      <!-- Revision Notes (for edit mode) -->
      {#if scenario}
        <div>
          <label for="revision-notes" class="block text-sm font-medium text-gray-700 mb-1">Revision Notes</label>
          <textarea
            id="revision-notes"
            bind:value={formData.revision_notes}
            rows="2"
            class="form-textarea w-full rounded-md border-gray-300"
            placeholder="Describe what changed in this revision"
          ></textarea>
        </div>
      {/if}
      
      <!-- Form Actions -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <button 
          type="button"
          on:click={handleCancel}
          class="btn btn-secondary"
          disabled={isSaving}
        >
          Cancel
        </button>
        
        <button 
          type="submit"
          class="btn btn-primary flex items-center gap-1"
          disabled={isSaving}
        >
          {#if isSaving}
            <Loader2 size={16} class="animate-spin" />
          {:else}
            <Save size={16} />
          {/if}
          {scenario ? 'Update' : 'Create'} Scenario
        </button>
      </div>
    </form>
  {/if}
</div>
