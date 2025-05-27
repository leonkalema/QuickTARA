<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { RefreshCw, AlertCircle, Eye, Edit, Trash2, Info } from '@lucide/svelte';
  import { assetApi, type Asset, AssetType } from '../api/assets';
  import { safeApiCall } from '../utils/error-handler';
  
  const dispatch = createEventDispatcher();
  
  // Props
  export let productId: string | null = null; // Optional product ID to filter assets by
  
  // Asset state
  let assets: Asset[] = [];
  let filteredAssets: Asset[] = [];
  let isLoading = true;
  let error = '';
  
  // Filter state
  let filters = {
    searchTerm: '',
    assetType: ''
  };
  
  onMount(async () => {
    await loadAssets();
  });
  
  // Expose this method so parent component can update assets
  export function updateAssets(newAssets: Asset[]) {
    assets = newAssets;
    applyFilters();
    dispatch('update', assets);
  }
  
  async function loadAssets() {
    isLoading = true;
    error = '';
    
    try {
      let result;
      if (productId) {
        result = await assetApi.getByProduct(productId);
      } else {
        result = await assetApi.getAll();
      }
      
      assets = result.assets;
      applyFilters();
      dispatch('update', assets);
    } catch (err) {
      console.error('Error loading assets:', err);
      error = 'Failed to load assets. Please try again.';
    } finally {
      isLoading = false;
    }
  }
  
  function applyFilters() {
    filteredAssets = assets.filter(asset => {
      // Search term filter (case insensitive)
      const searchTermMatch = !filters.searchTerm || 
        asset.name.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        asset.asset_id.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        (asset.description && asset.description.toLowerCase().includes(filters.searchTerm.toLowerCase()));
      
      // Asset type filter
      const assetTypeMatch = !filters.assetType || asset.asset_type === filters.assetType;
      
      return searchTermMatch && assetTypeMatch;
    });
  }
  
  function handleSearchInput(event: Event) {
    filters.searchTerm = (event.target as HTMLInputElement).value;
    applyFilters();
  }
  
  function handleTypeFilter(event: Event) {
    filters.assetType = (event.target as HTMLSelectElement).value;
    applyFilters();
  }
  
  function handleViewAsset(asset: Asset) {
    dispatch('view', asset);
  }
  
  function handleEditAsset(asset: Asset) {
    dispatch('edit', asset);
  }
  
  async function handleDeleteAsset(assetId: string) {
    if (confirm(`Are you sure you want to delete this asset: ${assetId}?`)) {
      const success = await safeApiCall(() => assetApi.delete(assetId));
      
      if (success) {
        // First update local state
        assets = assets.filter(a => a.asset_id !== assetId);
        applyFilters();
        dispatch('update', assets);
        
        // Then trigger a fresh reload to ensure consistency
        await loadAssets();
      }
    }
  }
</script>

<div>
  <!-- Search and Filter Controls -->
  <div class="mb-6">
    <div class="flex justify-between items-end gap-4">
      <div class="flex-grow">
        <label for="asset-search" class="block text-sm font-medium text-gray-700 mb-1">Search Assets</label>
        <div class="relative">
          <input
            id="asset-search"
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
      
      <div class="w-1/3">
        <label for="type-filter" class="block text-sm font-medium text-gray-700 mb-1">Asset Type</label>
        <select
          id="type-filter"
          class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
          value={filters.assetType}
          on:change={handleTypeFilter}
        >
          <option value="">All Types</option>
          <option value={AssetType.FIRMWARE}>Firmware</option>
          <option value={AssetType.SOFTWARE}>Software</option>
          <option value={AssetType.CONFIGURATION}>Configuration</option>
          <option value={AssetType.CALIBRATION}>Calibration</option>
          <option value={AssetType.DATA}>Data</option>
          <option value={AssetType.DIAGNOSTIC}>Diagnostic</option>
          <option value={AssetType.COMMUNICATION}>Communication</option>
          <option value={AssetType.HARDWARE}>Hardware</option>
          <option value={AssetType.INTERFACE}>Interface</option>
          <option value={AssetType.OTHER}>Other</option>
        </select>
      </div>
    </div>
  </div>
  
  <!-- Asset List -->
  <div>
    {#if isLoading}
      <div class="flex justify-center items-center h-64">
        <div class="text-center">
          <RefreshCw size={36} class="animate-spin mx-auto text-primary mb-4" />
          <p>Loading assets...</p>
        </div>
      </div>
    {:else if error}
      <div class="bg-red-50 border-l-4 border-red-500 p-4 flex items-start">
        <AlertCircle size={20} class="mr-3 mt-0.5 flex-shrink-0" />
        <div>
          <h3 class="font-medium">Error loading assets</h3>
          <p class="mt-1">{error}</p>
          <button 
            on:click={loadAssets}
            class="mt-2 text-sm font-medium text-red-600 hover:text-red-800 flex items-center gap-1">
            <RefreshCw size={14} /> Try again
          </button>
        </div>
      </div>
    {:else if filteredAssets.length === 0}
      <div class="bg-gray-50 border border-gray-200 text-gray-600 rounded-lg p-8 text-center">
        {#if assets.length === 0}
          <p class="mb-4">No assets found. {#if productId}Add your first asset to this product.{:else}Add your first asset to get started.{/if}</p>
        {:else}
          <p>No assets match your filters.</p>
          <button 
            on:click={() => {
              filters.searchTerm = '';
              filters.assetType = '';
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
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Security (C-I-A)</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            {#each filteredAssets as asset (asset.asset_id)}
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{asset.asset_id}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{asset.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {asset.asset_type}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div class="flex space-x-2">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      {asset.confidentiality === 'High' ? 'bg-red-100 text-red-800' : 
                       asset.confidentiality === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
                       asset.confidentiality === 'Low' ? 'bg-green-100 text-green-800' : 
                       'bg-gray-100 text-gray-800'}">
                      C:{asset.confidentiality}
                    </span>
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      {asset.integrity === 'High' ? 'bg-red-100 text-red-800' : 
                       asset.integrity === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
                       asset.integrity === 'Low' ? 'bg-green-100 text-green-800' : 
                       'bg-gray-100 text-gray-800'}">
                      I:{asset.integrity}
                    </span>
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      {asset.availability === 'High' ? 'bg-red-100 text-red-800' : 
                       asset.availability === 'Medium' ? 'bg-yellow-100 text-yellow-800' : 
                       asset.availability === 'Low' ? 'bg-green-100 text-green-800' : 
                       'bg-gray-100 text-gray-800'}">
                      A:{asset.availability}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex space-x-2">
                    <button 
                      on:click={() => handleViewAsset(asset)}
                      class="text-blue-600 hover:text-blue-900 p-1 rounded-full hover:bg-blue-100 transition-colors"
                      title="View"
                    >
                      <Eye size={16} />
                      <span class="sr-only">View</span>
                    </button>
                    <button 
                      on:click={() => handleEditAsset(asset)}
                      class="text-green-600 hover:text-green-900 p-1 rounded-full hover:bg-green-100 transition-colors"
                      title="Edit"
                    >
                      <Edit size={16} />
                      <span class="sr-only">Edit</span>
                    </button>
                    <button 
                      on:click={() => handleDeleteAsset(asset.asset_id)}
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
      
      {#if filteredAssets.length !== assets.length}
        <p class="text-sm text-gray-500 mt-4">
          Showing {filteredAssets.length} of {assets.length} assets
        </p>
      {/if}
    {/if}
  </div>
</div>
