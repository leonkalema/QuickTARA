<script lang="ts">
  import { Search, Filter, X } from 'lucide-svelte';
  
  // Props
  export let types: string[] = ['ECU', 'Sensor', 'Gateway', 'Actuator', 'Network'];
  export let safetyLevels: string[] = ['QM', 'ASIL A', 'ASIL B', 'ASIL C', 'ASIL D'];
  export let trustZones: string[] = ['Critical', 'Boundary', 'Standard', 'Untrusted'];
  
  // Filters state
  export let searchTerm = '';
  export let selectedTypes: string[] = [];
  export let selectedSafetyLevels: string[] = [];
  export let selectedTrustZones: string[] = [];
  export let showFilters = false;
  
  // Methods
  function toggleFilter(array: string[], item: string) {
    const index = array.indexOf(item);
    if (index === -1) {
      array.push(item);
    } else {
      array.splice(index, 1);
    }
    array = [...array]; // Trigger reactivity
    dispatchChange();
  }
  
  function clearFilters() {
    searchTerm = '';
    selectedTypes = [];
    selectedSafetyLevels = [];
    selectedTrustZones = [];
    dispatchChange();
  }
  
  function dispatchChange() {
    dispatch('filterChange', {
      searchTerm,
      selectedTypes,
      selectedSafetyLevels,
      selectedTrustZones
    });
  }
  
  function handleSearchInput(event: Event) {
    searchTerm = (event.target as HTMLInputElement).value;
    dispatchChange();
  }
  
  // Create a dispatch function for events
  function dispatch(name: string, detail: any) {
    const event = new CustomEvent(name, { detail });
    dispatchEvent(event);
  }
  
  $: activeFiltersCount = selectedTypes.length + selectedSafetyLevels.length + selectedTrustZones.length;
</script>

<div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-4">
  <div class="p-4">
    <div class="relative">
      <input
        type="text"
        placeholder="Search components..."
        class="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20"
        bind:value={searchTerm}
        on:input={handleSearchInput}
      />
      <div class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
        <Search size={18} />
      </div>
      <button
        class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-primary"
        on:click={() => showFilters = !showFilters}
      >
        <Filter size={18} />
        {#if activeFiltersCount > 0}
          <span class="absolute -top-2 -right-2 bg-primary text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
            {activeFiltersCount}
          </span>
        {/if}
      </button>
    </div>
  </div>

  {#if showFilters}
    <div class="p-4 border-t border-gray-100 bg-gray-50">
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-semibold text-gray-700">Filters</h3>
        {#if activeFiltersCount > 0}
          <button 
            class="text-sm text-gray-500 hover:text-primary flex items-center gap-1"
            on:click={clearFilters}
          >
            <X size={14} /> Clear all
          </button>
        {/if}
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Component Types -->
        <div>
          <h4 class="font-medium text-sm text-gray-600 mb-2">Component Type</h4>
          <div class="flex flex-wrap gap-2">
            {#each types as type}
              <button
                class="px-3 py-1 text-sm rounded-full transition-colors {selectedTypes.includes(type) ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-100'}"
                on:click={() => toggleFilter(selectedTypes, type)}
              >
                {type}
              </button>
            {/each}
          </div>
        </div>
        
        <!-- Safety Levels -->
        <div>
          <h4 class="font-medium text-sm text-gray-600 mb-2">Safety Level</h4>
          <div class="flex flex-wrap gap-2">
            {#each safetyLevels as level}
              <button
                class="px-3 py-1 text-sm rounded-full transition-colors {selectedSafetyLevels.includes(level) ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-100'}"
                on:click={() => toggleFilter(selectedSafetyLevels, level)}
              >
                {level}
              </button>
            {/each}
          </div>
        </div>
        
        <!-- Trust Zones -->
        <div>
          <h4 class="font-medium text-sm text-gray-600 mb-2">Trust Zone</h4>
          <div class="flex flex-wrap gap-2">
            {#each trustZones as zone}
              <button
                class="px-3 py-1 text-sm rounded-full transition-colors {selectedTrustZones.includes(zone) ? 'bg-primary text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-100'}"
                on:click={() => toggleFilter(selectedTrustZones, zone)}
              >
                {zone}
              </button>
            {/each}
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>
