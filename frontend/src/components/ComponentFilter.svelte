<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Search, Filter, X } from '@lucide/svelte';

  export let componentTypes = ['ECU', 'Sensor', 'Gateway', 'Actuator', 'Network'];
  export let safetyLevels = ['QM', 'ASIL A', 'ASIL B', 'ASIL C', 'ASIL D'];
  export let trustZones = ['Critical', 'Boundary', 'Standard', 'Untrusted'];
  
  // Filter state
  let searchTerm = '';
  let selectedType = '';
  let selectedSafetyLevel = '';
  let selectedTrustZone = '';
  
  const dispatch = createEventDispatcher();
  
  function applyFilters() {
    dispatch('filter', {
      searchTerm,
      type: selectedType,
      safetyLevel: selectedSafetyLevel,
      trustZone: selectedTrustZone
    });
  }
  
  function resetFilters() {
    searchTerm = '';
    selectedType = '';
    selectedSafetyLevel = '';
    selectedTrustZone = '';
    dispatch('filter', {
      searchTerm: '',
      type: '',
      safetyLevel: '',
      trustZone: ''
    });
  }
  
  function handleInput() {
    dispatch('filter', {
      searchTerm,
      type: selectedType,
      safetyLevel: selectedSafetyLevel,
      trustZone: selectedTrustZone
    });
  }
</script>

<div class="bg-white rounded-xl shadow-sm p-4 mb-6">
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-lg font-semibold text-gray-900 flex items-center">
      <Filter size={20} class="mr-2" />
      Filter Components
    </h2>
    
    {#if searchTerm || selectedType || selectedSafetyLevel || selectedTrustZone}
      <button 
        on:click={resetFilters}
        class="text-sm text-gray-600 flex items-center hover:text-red-600 transition-colors">
        <X size={16} class="mr-1" /> Clear Filters
      </button>
    {/if}
  </div>
  
  <div class="relative mb-4">
    <input 
      type="text" 
      bind:value={searchTerm}
      on:input={handleInput}
      placeholder="Search components..."
      class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
    />
    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <Search size={18} class="text-gray-400" />
    </div>
  </div>
  
  <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
    <!-- Type Filter -->
    <div>
      <label for="type-filter" class="block text-sm font-medium text-gray-700 mb-1">Component Type</label>
      <select 
        id="type-filter" 
        bind:value={selectedType}
        on:change={applyFilters}
        class="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-primary focus:border-primary">
        <option value="">All Types</option>
        {#each componentTypes as type}
          <option value={type}>{type}</option>
        {/each}
      </select>
    </div>
    
    <!-- Safety Level Filter -->
    <div>
      <label for="safety-filter" class="block text-sm font-medium text-gray-700 mb-1">Safety Level</label>
      <select 
        id="safety-filter" 
        bind:value={selectedSafetyLevel}
        on:change={applyFilters}
        class="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-primary focus:border-primary">
        <option value="">All Levels</option>
        {#each safetyLevels as level}
          <option value={level}>{level}</option>
        {/each}
      </select>
    </div>
    
    <!-- Trust Zone Filter -->
    <div>
      <label for="trust-filter" class="block text-sm font-medium text-gray-700 mb-1">Trust Zone</label>
      <select 
        id="trust-filter" 
        bind:value={selectedTrustZone}
        on:change={applyFilters}
        class="w-full rounded-lg border-gray-300 focus:ring-2 focus:ring-primary focus:border-primary">
        <option value="">All Zones</option>
        {#each trustZones as zone}
          <option value={zone}>{zone}</option>
        {/each}
      </select>
    </div>
  </div>
</div>
