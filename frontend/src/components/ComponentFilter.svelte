<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Search, Filter, X, ChevronDown, ChevronUp } from '@lucide/svelte';
  import { scopeApi, type SystemScope } from '../api/scope';
  import { safeApiCall } from '../utils/error-handler';

  export let componentTypes = ['ECU', 'Sensor', 'Gateway', 'Actuator', 'Network'];
  export let safetyLevels = ['QM', 'ASIL A', 'ASIL B', 'ASIL C', 'ASIL D'];
  export let trustZones = ['Critical', 'Boundary', 'Standard', 'Untrusted'];
  
  // Available scopes for filtering
  let scopes: SystemScope[] = [];
  
  // Filter state
  let searchTerm = '';
  let selectedType = '';
  let selectedSafetyLevel = '';
  let selectedTrustZone = '';
  let selectedScope = '';
  
  // UI state
  let filtersExpanded = false;
  let activeFilterCount = 0;
  
  const dispatch = createEventDispatcher();
  
  // Load available scopes
  onMount(async () => {
    const result = await safeApiCall(scopeApi.getAll);
    if (result) {
      scopes = result.scopes;
    }
  });

  // Function to update the active filter count
  function updateActiveFilterCount() {
    activeFilterCount = 0;
    if (selectedType) activeFilterCount++;
    if (selectedSafetyLevel) activeFilterCount++;
    if (selectedTrustZone) activeFilterCount++;
    if (selectedScope) activeFilterCount++;
  }
  
  function applyFilters() {
    updateActiveFilterCount();
    dispatch('filter', {
      searchTerm,
      type: selectedType,
      safetyLevel: selectedSafetyLevel,
      trustZone: selectedTrustZone,
      scope: selectedScope
    });
  }
  
  function resetFilters() {
    searchTerm = '';
    selectedType = '';
    selectedSafetyLevel = '';
    selectedTrustZone = '';
    selectedScope = '';
    activeFilterCount = 0;
    dispatch('filter', {
      searchTerm: '',
      type: '',
      safetyLevel: '',
      trustZone: '',
      scope: ''
    });
  }
  
  function handleInput() {
    dispatch('filter', {
      searchTerm,
      type: selectedType,
      safetyLevel: selectedSafetyLevel,
      trustZone: selectedTrustZone,
      scope: selectedScope
    });
  }
  
  function toggleFilters() {
    filtersExpanded = !filtersExpanded;
  }
</script>

<div style="background-color: rgba(255, 255, 255, 0.5); border: 1px solid var(--color-border);" class="rounded-lg mb-6 transition-all duration-300 overflow-hidden">
  <!-- Filter Header - Always visible -->
  <div class="flex items-center justify-between px-4 py-3" style="color: var(--color-text-main);">
    <div class="flex items-center">
      <!-- Show the clear button if filters are applied -->
      {#if searchTerm || selectedType || selectedSafetyLevel || selectedTrustZone}
        <button 
          type="button"
          on:click|stopPropagation={resetFilters}
          on:keydown={e => e.key === 'Enter' && resetFilters()}
          class="text-xs flex items-center mr-3 transition-colors duration-200 cursor-pointer bg-transparent border-0"
          style="color: var(--color-danger);">
          <X size={14} class="mr-1" /> Clear
        </button>
      {/if}
      
      <!-- Filter title and indicator -->
      <button
        type="button"
        on:click={toggleFilters}
        on:keydown={e => e.key === 'Enter' && toggleFilters()}
        class="font-medium flex items-center bg-transparent border-0 cursor-pointer"
        style="color: var(--color-text-primary);"
      >
        <Filter size={18} style="color: var(--color-primary);" class="mr-2" />
        <span>Filter Components {activeFilterCount > 0 ? '(active)' : '(optional)'}</span>
        
        <!-- Filter count badge -->
        {#if activeFilterCount > 0}
          <span class="ml-2 text-xs font-medium px-2 py-0.5 rounded-full" style="background-color: var(--color-primary); color: white;">
            {activeFilterCount}
          </span>
        {/if}
      </button>
    </div>
    
    <!-- Chevron indicator button -->
    <button
      type="button"
      on:click={toggleFilters}
      on:keydown={e => e.key === 'Enter' && toggleFilters()}
      class="bg-transparent border-0 cursor-pointer"
    >
      {#if filtersExpanded}
        <ChevronUp size={20} style="color: var(--color-text-secondary);" />
      {:else}
        <ChevronDown size={20} style="color: var(--color-text-secondary);" />
      {/if}
    </button>
  </div>
  
  <!-- Expandable Filter Content -->
  {#if filtersExpanded}
    <div class="p-4 pt-0 border-t" style="border-color: var(--color-border);">
      <!-- Search -->
      <div class="relative mb-4">
        <input 
          type="text" 
          bind:value={searchTerm}
          on:input={handleInput}
          placeholder="Search components..."
          class="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-1"
          style="border-color: var(--color-border); background-color: rgba(255, 255, 255, 0.7); color: var(--color-text-main);"
        />
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search size={16} style="color: var(--color-text-muted);" />
        </div>
      </div>
      
      <!-- Filter dropdowns -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Type Filter -->
        <div>
          <label for="type-filter" class="block text-xs mb-1" style="color: var(--color-text-muted);">Component Type (Optional)</label>
          <select 
            id="type-filter" 
            bind:value={selectedType}
            on:change={applyFilters}
            class="w-full rounded-md border py-1.5 text-sm focus:outline-none focus:ring-1"
            style="border-color: var(--color-border); background-color: rgba(255, 255, 255, 0.7); color: var(--color-text-main);">
            <option value="">All Types</option>
            {#each componentTypes as type}
              <option value={type}>{type}</option>
            {/each}
          </select>
        </div>
        
        <!-- Safety Level Filter -->
        <div>
          <label for="safety-filter" class="block text-xs mb-1" style="color: var(--color-text-muted);">Safety Level (Optional)</label>
          <select 
            id="safety-filter" 
            bind:value={selectedSafetyLevel}
            on:change={applyFilters}
            class="w-full rounded-md border py-1.5 text-sm focus:outline-none focus:ring-1"
            style="border-color: var(--color-border); background-color: rgba(255, 255, 255, 0.7); color: var(--color-text-main);">
            <option value="">All Levels</option>
            {#each safetyLevels as level}
              <option value={level}>{level}</option>
            {/each}
          </select>
        </div>
        
        <!-- Trust Zone Filter -->
        <div>
          <label for="trust-filter" class="block text-xs mb-1" style="color: var(--color-text-muted);">Trust Zone (Optional)</label>
          <select 
            id="trust-filter" 
            bind:value={selectedTrustZone}
            on:change={applyFilters}
            class="w-full rounded-md border py-1.5 text-sm focus:outline-none focus:ring-1"
            style="border-color: var(--color-border); background-color: rgba(255, 255, 255, 0.7); color: var(--color-text-main);">
            <option value="">All Zones</option>
            {#each trustZones as zone}
              <option value={zone}>{zone}</option>
            {/each}
          </select>
        </div>
        
        <!-- Scope Filter -->
        <div>
          <label for="scope-filter" class="block text-xs mb-1" style="color: var(--color-text-muted);">System Scope (Optional)</label>
          <select 
            id="scope-filter" 
            bind:value={selectedScope}
            on:change={applyFilters}
            class="w-full rounded-md border py-1.5 text-sm focus:outline-none focus:ring-1"
            style="border-color: var(--color-border); background-color: rgba(255, 255, 255, 0.7); color: var(--color-text-main);">
            <option value="">All Scopes</option>
            {#each scopes as scope}
              <option value={scope.scope_id}>{scope.name}</option>
            {/each}
          </select>
        </div>
      </div>
    </div>
  {/if}
</div>
