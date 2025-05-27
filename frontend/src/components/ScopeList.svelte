<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { RefreshCw, AlertCircle, Eye, Edit, Trash2, Info } from '@lucide/svelte';
  import { productApi, type Product } from '../api/products';
  import { safeApiCall } from '../utils/error-handler';
  
  const dispatch = createEventDispatcher();
  
  // Product state (formerly scopes)
  let scopes: Product[] = [];
  let filteredScopes: Product[] = [];
  let isLoading = true;
  let error = '';
  
  // Filter state
  let filters = {
    searchTerm: '',
    systemType: ''
  };
  
  onMount(async () => {
    await loadScopes();
  });
  
  // Expose this method so parent component can update scopes
  export function updateScopes(newScopes: Product[]) {
    scopes = newScopes;
    applyFilters();
    dispatch('update', scopes);
  }
  
  async function loadScopes() {
    isLoading = true;
    error = '';
    
    try {
      const result = await productApi.getAll();
      scopes = result.scopes;
      applyFilters();
      dispatch('update', scopes);
    } catch (err) {
      console.error('Error loading products:', err);
      error = 'Failed to load products. Please try again.';
    } finally {
      isLoading = false;
    }
  }
  
  function applyFilters() {
    filteredScopes = scopes.filter(scope => {
      // Search term filter (case insensitive)
      const searchTermMatch = !filters.searchTerm || 
        scope.name.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        scope.scope_id.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        (scope.description && scope.description.toLowerCase().includes(filters.searchTerm.toLowerCase()));
      
      // Product type filter (formerly system type)
      const productTypeMatch = !filters.systemType || scope.product_type === filters.systemType;
      
      return searchTermMatch && productTypeMatch;
    });
  }
  
  function handleSearchInput(event: Event) {
    filters.searchTerm = (event.target as HTMLInputElement).value;
    applyFilters();
  }
  
  function handleTypeFilter(event: Event) {
    filters.systemType = (event.target as HTMLSelectElement).value;
    applyFilters();
  }
  
  function handleViewScope(scope: Product) {
    dispatch('view', scope);
  }
  
  function handleEditScope(scope: Product) {
    dispatch('edit', scope);
  }
  
  async function handleDeleteScope(scopeId: string) {
    if (confirm(`Are you sure you want to delete this product: ${scopeId}?`)) {
      const success = await safeApiCall(() => productApi.delete(scopeId));
      
      if (success) {
        // First update local state
        scopes = scopes.filter(s => s.scope_id !== scopeId);
        applyFilters();
        dispatch('update', scopes);
        
        // Then trigger a fresh reload to ensure consistency
        await loadScopes();
      }
    }
  }
</script>

<div>
  <!-- Search and Filter Controls -->
  <div class="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
    <div class="col-span-2">
      <label for="scope-search" class="block text-sm font-medium text-gray-700 mb-1">Search Scopes</label>
      <div class="relative">
        <input
          id="scope-search"
          type="text"
          placeholder="Search by name, ID, or description"
          class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
          value={filters.searchTerm}
          on:input={handleSearchInput}
        />
        <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
      </div>
    </div>
    
    <div>
      <label for="type-filter" class="block text-sm font-medium text-gray-700 mb-1">Product Type</label>
      <select
        id="type-filter"
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
        value={filters.systemType}
        on:change={handleTypeFilter}
      >
        <option value="">All Types</option>
        <option value="ECU">ECU</option>
        <option value="Gateway">Gateway</option>
        <option value="Sensor">Sensor</option>
        <option value="Actuator">Actuator</option>
        <option value="Network">Network</option>
        <option value="ExternalDevice">External Device</option>
        <option value="Other">Other</option>
      </select>
    </div>
  </div>
  
  <!-- Scope List -->
  <div>
    {#if isLoading}
      <div class="flex justify-center items-center h-64">
        <div class="text-center">
          <RefreshCw size={36} class="animate-spin mx-auto text-primary mb-4" />
          <p class="text-gray-600">Loading scopes...</p>
        </div>
      </div>
    {:else if error}
      <div class="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 flex items-start">
        <AlertCircle size={20} class="mr-3 mt-0.5 flex-shrink-0" />
        <div>
          <h3 class="font-medium">Error loading scopes</h3>
          <p class="mt-1">{error}</p>
          <button 
            on:click={loadScopes}
            class="mt-2 text-sm font-medium text-red-600 hover:text-red-800 flex items-center gap-1">
            <RefreshCw size={14} /> Try again
          </button>
        </div>
      </div>
    {:else if filteredScopes.length === 0}
      <div class="bg-gray-50 border border-gray-200 text-gray-600 rounded-lg p-8 text-center">
        {#if scopes.length === 0}
          <p class="mb-4">No system scopes found. Define your first system scope to get started.</p>
        {:else}
          <p>No scopes match your filters.</p>
          <button 
            on:click={() => {
              filters.searchTerm = '';
              filters.systemType = '';
              applyFilters();
            }}
            class="btn px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 mt-2">
            Clear Filters
          </button>
        {/if}
      </div>
    {:else}
      <div class="overflow-hidden border border-gray-200 rounded-lg">
        <table class="min-w-full divide-y divide-gray-200">
          <thead style="background-color: var(--color-table-header-bg);">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product Type</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            {#each filteredScopes as scope (scope.scope_id)}
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{scope.scope_id}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{scope.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {scope.product_type}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{scope.description || 'No description'}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex space-x-2">
                    <button 
                      on:click={() => handleViewScope(scope)}
                      class="text-blue-600 hover:text-blue-900 p-1 rounded-full hover:bg-blue-100 transition-colors"
                      title="View"
                    >
                      <Eye size={16} />
                      <span class="sr-only">View</span>
                    </button>
                    <button 
                      on:click={() => handleEditScope(scope)}
                      class="text-green-600 hover:text-green-900 p-1 rounded-full hover:bg-green-100 transition-colors"
                      title="Edit"
                    >
                      <Edit size={16} />
                      <span class="sr-only">Edit</span>
                    </button>
                    <button 
                      on:click={() => handleDeleteScope(scope.scope_id)}
                      class="text-red-600 hover:text-red-900 p-1 rounded-full hover:bg-red-100 transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                      <span class="sr-only">Delete</span>
                    </button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      
      {#if filteredScopes.length !== scopes.length}
        <p class="text-sm text-gray-500 mt-4">
          Showing {filteredScopes.length} of {scopes.length} scopes
        </p>
      {/if}
    {/if}
  </div>
</div>
