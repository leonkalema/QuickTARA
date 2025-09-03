<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Search, Cpu, AlertCircle, CheckCircle2 } from '@lucide/svelte';
  import { componentApi, type Component } from '../../api/components';
  import { safeApiCall } from '../../utils/error-handler';

  export let productId: string;
  export let selectedAssetId: string | null = null;
  export let disabled = false;

  const dispatch = createEventDispatcher();

  let assets: Component[] = [];
  let filteredAssets: Component[] = [];
  let searchTerm = '';
  let isLoading = true;
  let error = '';

  onMount(async () => {
    await loadAssets();
  });

  async function loadAssets() {
    if (!productId) return;
    
    isLoading = true;
    error = '';
    
    try {
      const result = await safeApiCall(() => componentApi.getAll());
      
      if (result) {
        // Filter assets that belong to the selected product (scope_id matches productId)
        const allComponents = Array.isArray(result) ? result : (result as any)?.components || [];
        assets = allComponents.filter((component: any) => 
          component.scope_id === productId
        );
        
        filteredAssets = assets;
      }
    } catch (err) {
      console.error('Error loading assets:', err);
      error = 'Failed to load assets. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  function handleSearch() {
    if (!searchTerm.trim()) {
      filteredAssets = assets;
      return;
    }

    const term = searchTerm.toLowerCase();
    filteredAssets = assets.filter(asset =>
      asset.name.toLowerCase().includes(term) ||
      asset.type?.toLowerCase().includes(term) ||
      asset.description?.toLowerCase().includes(term)
    );
  }

  function selectAsset(asset: Component) {
    if (disabled) return;
    
    selectedAssetId = asset.component_id;
    dispatch('assetSelected', {
      assetId: asset.component_id,
      assetName: asset.name,
      assetType: asset.type
    });
  }

  function clearSelection() {
    selectedAssetId = null;
    dispatch('assetCleared');
  }

  $: handleSearch();
  $: if (productId) loadAssets();
</script>

<div class="space-y-4">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h3 class="text-lg font-medium text-gray-900">Select Asset</h3>
      <p class="text-sm text-gray-600">Choose one asset for this damage scenario</p>
    </div>
    {#if selectedAssetId}
      <button
        on:click={clearSelection}
        class="text-sm text-red-600 hover:text-red-700 transition-colors"
        disabled={disabled}
      >
        Clear Selection
      </button>
    {/if}
  </div>

  <!-- Search -->
  <div class="relative">
    <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
    <input
      type="text"
      bind:value={searchTerm}
      placeholder="Search assets..."
      disabled={disabled}
      class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500"
    />
  </div>

  <!-- Loading State -->
  {#if isLoading}
    <div class="text-center py-8">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-gray-600 text-sm mt-2">Loading assets...</p>
    </div>
  {:else if error}
    <!-- Error State -->
    <div class="bg-red-50 border border-red-200 rounded-md p-4">
      <div class="flex items-center">
        <AlertCircle class="h-5 w-5 text-red-600 mr-2" />
        <p class="text-red-700 text-sm">{error}</p>
      </div>
      <button 
        on:click={loadAssets}
        class="mt-2 text-sm text-red-600 hover:text-red-700 underline"
      >
        Retry
      </button>
    </div>
  {:else if filteredAssets.length === 0}
    <!-- Empty State -->
    <div class="text-center py-8">
      <Cpu class="mx-auto h-12 w-12 text-gray-300 mb-3" />
      <h4 class="text-sm font-medium text-gray-900 mb-1">No assets found</h4>
      <p class="text-sm text-gray-600">
        {searchTerm ? 'Try adjusting your search terms.' : 'No assets available for this product.'}
      </p>
    </div>
  {:else}
    <!-- Assets List -->
    <div class="space-y-2 max-h-64 overflow-y-auto">
      {#each filteredAssets as asset}
        <button
          on:click={() => selectAsset(asset)}
          disabled={disabled}
          class="w-full text-left p-3 border border-gray-200 rounded-md hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
            {selectedAssetId === asset.component_id ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : ''}"
          data-testid="asset-option-{asset.component_id}"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-2">
                <Cpu class="h-4 w-4 text-gray-500" />
                <h4 class="font-medium text-gray-900">{asset.name}</h4>
                {#if selectedAssetId === asset.component_id}
                  <CheckCircle2 class="h-4 w-4 text-blue-600" />
                {/if}
              </div>
              {#if asset.type}
                <p class="text-sm text-gray-500 mt-1">{asset.type}</p>
              {/if}
              {#if asset.description}
                <p class="text-sm text-gray-600 mt-1 line-clamp-2">{asset.description}</p>
              {/if}
            </div>
          </div>

          <!-- CIA Properties Display -->
          {#if asset.confidentiality_requirement || asset.integrity_requirement || asset.availability_requirement}
            <div class="flex space-x-1 mt-2">
              {#if asset.confidentiality_requirement}
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                  C
                </span>
              {/if}
              {#if asset.integrity_requirement}
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                  I
                </span>
              {/if}
              {#if asset.availability_requirement}
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                  A
                </span>
              {/if}
            </div>
          {/if}
        </button>
      {/each}
    </div>
  {/if}

  <!-- Selection Summary -->
  {#if selectedAssetId}
    <div class="bg-green-50 border border-green-200 rounded-md p-3">
      <div class="flex items-center">
        <CheckCircle2 class="h-5 w-5 text-green-600 mr-2" />
        <div>
          <p class="text-sm font-medium text-green-800">Asset Selected</p>
          <p class="text-sm text-green-700">
            {filteredAssets.find(a => a.component_id === selectedAssetId)?.name || 'Selected asset'}
          </p>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
