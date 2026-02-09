<script lang="ts">
  export let selectedType: string;
  export let selectedStatus: string;
  export let searchQuery: string;
  export let totalProducts: number;
  export let filteredCount: number;

  const productTypes = [
    { value: 'automotive', label: 'Automotive' },
    { value: 'industrial', label: 'Industrial' },
    { value: 'iot', label: 'IoT' },
    { value: 'medical', label: 'Medical' },
    { value: 'aerospace', label: 'Aerospace' },
    { value: 'other', label: 'Other' }
  ];

  const statusOptions = [
    { value: 'development', label: 'Development' },
    { value: 'testing', label: 'Testing' },
    { value: 'production', label: 'Production' },
    { value: 'deprecated', label: 'Deprecated' }
  ];

  function clearFilters() {
    selectedType = '';
    selectedStatus = '';
    searchQuery = '';
  }

  $: hasActiveFilters = selectedType || selectedStatus || searchQuery;
</script>

<div class="rounded-lg p-4" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
  <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
    <!-- Search and Filters -->
    <div class="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 flex-1">
      <!-- Search -->
      <div class="relative flex-1 max-w-md">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <input
          type="text"
          placeholder="Search products..."
          bind:value={searchQuery}
          class="block w-full pl-10 pr-3 py-2 rounded-md leading-5 text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
        />
      </div>

      <!-- Type Filter -->
      <select
        bind:value={selectedType}
        class="block w-full sm:w-auto px-3 py-2 rounded-md text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
      >
        <option value="">All Types</option>
        {#each productTypes as type}
          <option value={type.value}>{type.label}</option>
        {/each}
      </select>

      <!-- Status Filter -->
      <select
        bind:value={selectedStatus}
        class="block w-full sm:w-auto px-3 py-2 rounded-md text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
      >
        <option value="">All Statuses</option>
        {#each statusOptions as status}
          <option value={status.value}>{status.label}</option>
        {/each}
      </select>

      <!-- Clear Filters -->
      {#if hasActiveFilters}
        <button
          on:click={clearFilters}
          class="px-3 py-2 text-xs font-medium transition-colors" style="color: var(--color-accent-primary);"
        >
          Clear filters
        </button>
      {/if}
    </div>

    <!-- Results Count -->
    <div class="text-xs" style="color: var(--color-text-tertiary);">
      {#if hasActiveFilters}
        Showing {filteredCount} of {totalProducts} products
      {:else}
        {totalProducts} products total
      {/if}
    </div>
  </div>
</div>
