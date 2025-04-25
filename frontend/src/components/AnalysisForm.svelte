<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, AlertCircle, RefreshCw } from '@lucide/svelte';
  import { componentApi } from '../api/components';
  import { safeApiCall } from '../utils/error-handler';
  
  // Component properties
  export let editMode = false;

  // Form state
  let name = '';
  let description = '';
  let selectedComponentIds: string[] = [];
  let isLoading = true;
  let error = '';
  
  // Available components to select from
  let components: any[] = [];
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Validation state
  let validationErrors: any = {};
  
  onMount(async () => {
    await loadComponents();
  });
  
  async function loadComponents() {
    isLoading = true;
    error = '';
    
    try {
      const result = await safeApiCall(() => componentApi.getAll());
      
      if (result) {
        components = Array.isArray(result) ? result : [];
      }
    } catch (err) {
      console.error('Error loading components:', err);
      error = 'Failed to load components for analysis.';
    } finally {
      isLoading = false;
    }
  }
  
  function validate(): boolean {
    validationErrors = {};
    
    if (!name.trim()) {
      validationErrors.name = 'Analysis name is required';
    }
    
    if (selectedComponentIds.length === 0) {
      validationErrors.components = 'At least one component must be selected';
    }
    
    return Object.keys(validationErrors).length === 0;
  }
  
  function handleSubmit() {
    if (!validate()) {
      return;
    }
    
    const analysisData = {
      name: name.trim(),
      description: description.trim(),
      component_ids: selectedComponentIds
    };
    
    dispatch('submit', analysisData);
  }
  
  function handleCancel() {
    dispatch('cancel');
  }
  
  function handleComponentChange(componentId: string) {
    const index = selectedComponentIds.indexOf(componentId);
    
    if (index >= 0) {
      selectedComponentIds = selectedComponentIds.filter(id => id !== componentId);
    } else {
      selectedComponentIds = [...selectedComponentIds, componentId];
    }
    
    // Clear validation error if we now have components
    if (selectedComponentIds.length > 0) {
      validationErrors.components = '';
    }
  }
  
  function handleSelectAll() {
    if (components.length === selectedComponentIds.length) {
      // If all selected, deselect all
      selectedComponentIds = [];
    } else {
      // Select all
      selectedComponentIds = components.map(c => c.component_id);
    }
  }
</script>

<div class="bg-white rounded-xl shadow-lg p-6 w-full">
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-bold text-gray-900">
      {editMode ? 'Edit Analysis' : 'New Analysis'}
    </h2>
    <button 
      on:click={handleCancel}
      class="p-1.5 text-gray-500 hover:bg-gray-100 rounded-full transition-colors">
      <X size={20} />
    </button>
  </div>
  
  {#if error}
    <div class="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 mb-6 flex items-start">
      <AlertCircle size={20} class="mr-3 mt-0.5 flex-shrink-0" />
      <div>
        <h3 class="font-medium">Error loading components</h3>
        <p class="mt-1">{error}</p>
        <button 
          on:click={loadComponents}
          class="mt-2 text-sm font-medium text-red-600 hover:text-red-800 flex items-center gap-1">
          <RefreshCw size={14} /> Try again
        </button>
      </div>
    </div>
  {/if}
  
  <form on:submit|preventDefault={handleSubmit} class="space-y-6">
    <!-- Analysis Name -->
    <div>
      <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Analysis Name *</label>
      <input
        type="text"
        id="name"
        bind:value={name}
        class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 {validationErrors.name ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : ''}"
        placeholder="Engine Systems Analysis, Telematics Security Review, etc."
      />
      {#if validationErrors.name}
        <p class="mt-1 text-sm text-red-600">{validationErrors.name}</p>
      {/if}
    </div>
    
    <!-- Analysis Description -->
    <div>
      <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
      <textarea
        id="description"
        bind:value={description}
        rows="3"
        class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        placeholder="Brief description of analysis purpose, scope or goals"
      ></textarea>
    </div>
    
    <!-- Component Selection -->
    <div>
      <div class="flex justify-between items-center mb-2">
        <label for="component-selection" class="block text-sm font-medium text-gray-700">Select Components *</label>
        <button 
          type="button"
          on:click={handleSelectAll}
          class="text-sm text-indigo-600 hover:text-indigo-800">
          {components.length === selectedComponentIds.length ? 'Deselect All' : 'Select All'}
        </button>
      </div>
      
      {#if validationErrors.components}
        <p class="mt-1 text-sm text-red-600 mb-2">{validationErrors.components}</p>
      {/if}
      
      {#if isLoading}
        <div class="flex justify-center items-center h-32 bg-gray-50 border border-gray-200 rounded-lg">
          <RefreshCw size={24} class="animate-spin text-indigo-500" />
        </div>
      {:else if components.length === 0}
        <div class="flex justify-center items-center h-32 bg-gray-50 border border-gray-200 rounded-lg">
          <p class="text-gray-500">No components found. Add components first.</p>
        </div>
      {:else}
        <div id="component-selection" class="max-h-64 overflow-y-auto border border-gray-200 rounded-lg" role="group" aria-labelledby="component-selection-label">
          <ul class="divide-y divide-gray-200">
            {#each components as component}
              <li class="hover:bg-gray-50">
                <label class="flex items-center px-4 py-3 cursor-pointer">
                  <input
                    type="checkbox"
                    value={component.component_id}
                    checked={selectedComponentIds.includes(component.component_id)}
                    on:change={() => handleComponentChange(component.component_id)}
                    class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <div class="ml-3">
                    <p class="text-sm font-medium text-gray-900">{component.name}</p>
                    <p class="text-xs text-gray-500">{component.component_id} - {component.type} ({component.safety_level})</p>
                  </div>
                </label>
              </li>
            {/each}
          </ul>
        </div>
      {/if}
      
      <p class="mt-2 text-sm text-gray-500">
        Selected {selectedComponentIds.length} of {components.length} components
      </p>
    </div>
    
    <!-- Form Actions -->
    <div class="flex justify-end space-x-3 pt-4 border-t">
      <button 
        type="button"
        on:click={handleCancel} 
        class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
        Cancel
      </button>
      <button 
        type="submit"
        class="btn btn-primary"
        disabled={isLoading}>
        {editMode ? 'Update Analysis' : 'Run Analysis'}
      </button>
    </div>
  </form>
</div>
