<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  export let filters = {
    search: '',
    asset: '',
    cia: ''
  };
  
  export let assets: any[] = [];
  
  const ciaOptions = ['Confidentiality', 'Integrity', 'Availability'];
  
  let isExpanded = false;
  
  function updateFilter(key: keyof typeof filters, value: string) {
    filters[key] = value;
    dispatch('filterChange', filters);
  }
  
  function clearFilters() {
    filters = {
      search: '',
      asset: '',
      cia: ''
    };
    dispatch('filterChange', filters);
  }
</script>

<div class="rounded-lg mb-6" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
  <div class="flex items-center justify-between p-4 cursor-pointer" on:click={() => isExpanded = !isExpanded}>
    <div class="flex items-center space-x-2">
      <h3 class="text-xs font-medium" style="color: var(--color-text-primary);">Filters</h3>
      <svg 
        class="w-5 h-5 text-gray-400 transition-transform duration-200 {isExpanded ? 'rotate-180' : ''}" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
      </svg>
    </div>
    <button
      on:click|stopPropagation={clearFilters}
      class="text-xs" style="color: var(--color-accent-primary);"
    >
      Clear all
    </button>
  </div>
  
  {#if isExpanded}
    <div class="px-4 pb-4">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- Search -->
    <div>
      <label class="block text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Search</label>
      <input
        type="text"
        bind:value={filters.search}
        on:input={() => updateFilter('search', filters.search)}
        placeholder="Search scenarios..."
        class="w-full px-3 py-2 rounded-md text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
      />
    </div>
    
    <!-- Asset -->
    <div>
      <label class="block text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Asset</label>
      <select
        bind:value={filters.asset}
        on:change={() => updateFilter('asset', filters.asset)}
        class="w-full px-3 py-2 rounded-md text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
      >
        <option value="">All assets</option>
        {#each assets as asset}
          <option value={asset.asset_id}>{asset.name}</option>
        {/each}
      </select>
    </div>
    
    <!-- CIA -->
    <div>
      <label class="block text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">CIA Impact</label>
      <select
        bind:value={filters.cia}
        on:change={() => updateFilter('cia', filters.cia)}
        class="w-full px-3 py-2 rounded-md text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
      >
        <option value="">Any CIA</option>
        {#each ciaOptions as cia}
          <option value={cia.toLowerCase()}>{cia}</option>
        {/each}
      </select>
    </div>
      </div>
    </div>
  {/if}
</div>
