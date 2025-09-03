<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedProduct } from '../../lib/stores/productStore';
  import { notifications } from '../../lib/stores/notificationStore';
  import { assetApi } from '../../lib/api/assetApi';
  import type { Asset } from '../../lib/types/asset';
  import AssetTable from '../../features/assets/components/AssetTable.svelte';

  let assets: Asset[] = [];
  let isLoading = true;
  let error = '';

  async function loadAssets() {
    if (!$selectedProduct) return;
    
    isLoading = true;
    error = '';
    
    try {
      const response = await assetApi.getByProduct($selectedProduct.scope_id);
      assets = response.assets;
    } catch (err) {
      console.error('Error loading assets:', err);
      error = 'Failed to load assets';
      notifications.show('Failed to load assets', 'error');
    } finally {
      isLoading = false;
    }
  }

  function handleAssetCreated(event: CustomEvent<Asset>) {
    assets = [...assets, event.detail];
    notifications.show('Asset created successfully', 'success');
  }

  function handleAssetUpdated(event: CustomEvent<Asset>) {
    const updatedAsset = event.detail;
    const index = assets.findIndex(a => a.asset_id === updatedAsset.asset_id);
    if (index !== -1) {
      assets[index] = updatedAsset;
      assets = [...assets];
    }
  }

  onMount(() => {
    loadAssets();
  });

  // Reload assets when selected product changes
  $: if ($selectedProduct) {
    loadAssets();
  }
</script>

<svelte:head>
  <title>Assets - QuickTARA</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start space-y-4 lg:space-y-0">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Assets & Components</h1>
      {#if $selectedProduct}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Manage assets and components for <strong>{$selectedProduct.name}</strong>. 
          Define the building blocks that will be analyzed for potential damage scenarios.
        </p>
      {:else}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Please select a product first to view and manage its assets and components.
        </p>
      {/if}
    </div>
  </div>

  {#if !$selectedProduct}
    <!-- No Product Selected State -->
    <div class="text-center py-16">
      <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Product Selected</h3>
      <p class="text-gray-500 mb-6 max-w-md mx-auto">
        Select a product from the header dropdown or visit the Products page to choose which product's assets you want to manage.
      </p>
      <a
        href="/products"
        class="bg-slate-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-slate-700 transition-colors inline-flex items-center space-x-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
        </svg>
        <span>Select a Product</span>
      </a>
    </div>
  {:else}
    <!-- Content -->
    {#if isLoading}
      <div class="flex flex-col justify-center items-center py-16">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600 mb-4"></div>
        <p class="text-gray-500">Loading assets...</p>
      </div>
    {:else if error}
      <div class="bg-red-50 border border-red-200 rounded-lg p-6">
        <div class="flex items-start">
          <svg class="w-6 h-6 text-red-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading assets</h3>
            <p class="text-sm text-red-700 mt-1">{error}</p>
            <button
              on:click={loadAssets}
              class="mt-3 bg-red-100 text-red-800 px-3 py-1 rounded text-sm hover:bg-red-200 transition-colors"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    {:else}
      <!-- Asset Table -->
      <AssetTable 
        {assets} 
        productId={$selectedProduct.scope_id}
        on:assetCreated={handleAssetCreated}
        on:assetUpdated={handleAssetUpdated}
      />
    {/if}
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
