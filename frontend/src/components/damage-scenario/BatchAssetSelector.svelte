<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { ChevronRight } from '@lucide/svelte';
  import { assetApi } from '../../api/assets';
  import { safeApiCall } from '../../utils/error-handler';
  import type { Component } from '../../api/components';

  export let selectedProductId: string;
  export let selectedProductName: string;

  const dispatch = createEventDispatcher();

  let assets: Component[] = [];
  let selectedAssets: string[] = [];
  let isLoading = true;
  let error = '';

  onMount(() => {
    loadAssets();
  });

  async function loadAssets() {
    if (!selectedProductId) return;
    
    isLoading = true;
    error = '';
    
    try {
      const result = await safeApiCall(() => assetApi.getByProduct(selectedProductId));
      assets = Array.isArray(result) ? result : (result as any)?.assets || [];
    } catch (err) {
      error = 'Failed to load assets';
      console.error('Error loading assets:', err);
    } finally {
      isLoading = false;
    }
  }

  function handleNext() {
    dispatch('assetsSelected', { selectedAssets });
  }
</script>

<div class="space-y-4">
  <div>
    <h3 class="text-md font-medium text-gray-900">Select Assets</h3>
    <p class="text-sm text-gray-600">
      Select assets from <strong>{selectedProductName}</strong> to create damage scenarios for.
    </p>
  </div>

  {#if isLoading}
    <div class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  {:else if error}
    <div class="bg-red-50 border-l-4 border-red-400 p-4">
      <p class="text-sm text-red-700">{error}</p>
    </div>
  {:else if assets.length === 0}
    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
      <p class="text-sm text-yellow-700">
        No assets available for this product. Please create assets first.
      </p>
    </div>
  {:else}
    <div class="max-h-96 overflow-y-auto border rounded-lg">
      {#each assets as asset}
        <div class="p-4 flex items-center border-b last:border-b-0 hover:bg-gray-50">
          <input
            type="checkbox"
            value={(asset as any).asset_id || asset.component_id || (asset as any).id}
            bind:group={selectedAssets}
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <div class="ml-3 flex-1">
            <span class="block text-sm font-medium text-gray-900">
              {asset.name}
            </span>
            <span class="block text-xs text-gray-600">
              {asset.type || 'No type'}
            </span>
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <div class="flex justify-end pt-4 border-t border-gray-200">
    <button 
      type="button"
      on:click={handleNext}
      class="btn btn-primary flex items-center gap-1"
      disabled={selectedAssets.length === 0 || isLoading}
    >
      Next <ChevronRight size={16} />
    </button>
  </div>
</div>
