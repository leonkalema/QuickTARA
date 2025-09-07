<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedProduct } from '../../lib/stores/productStore';
  import { notifications } from '../../lib/stores/notificationStore';
  import { assetApi } from '../../lib/api/assetApi';
  import type { Asset } from '../../lib/types/asset';
  import type { APIError } from '$lib/utils/errorHandler';
  import { parseAPIError, withRetry } from '$lib/utils/errorHandler';
  import AssetTable from '../../features/assets/components/AssetTable.svelte';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import ErrorMessage from '$lib/components/ErrorMessage.svelte';

  let assets: Asset[] = [];
  let isLoading = true;
  let error: APIError | null = null;
  let retryCount = 0;
  const maxRetries = 3;

  async function loadAssets() {
    if (!$selectedProduct) return;
    
    isLoading = true;
    error = null;
    
    try {
      const response = await withRetry(
        () => assetApi.getByProduct($selectedProduct.scope_id),
        maxRetries,
        1000
      );
      assets = response.assets;
      retryCount = 0; // Reset retry count on success
      
      if (assets.length === 0) {
        notifications.show('No assets found for this product', 'info');
      }
    } catch (err) {
      console.error('Error loading assets:', err);
      error = parseAPIError(err);
      
      // Show user-friendly notification
      const errorMsg = error.message || 'Failed to load assets';
      notifications.show(errorMsg, 'error');
    } finally {
      isLoading = false;
    }
  }
  
  async function retryLoadAssets() {
    retryCount++;
    await loadAssets();
  }
  
  function dismissError() {
    error = null;
  }

  function handleAssetCreated(event: CustomEvent<Asset>) {
    assets = [...assets, event.detail];
    notifications.show(`Asset "${event.detail.name}" created successfully`, 'success');
  }

  function handleAssetUpdated(event: CustomEvent<Asset>) {
    const updatedAsset = event.detail;
    const index = assets.findIndex(a => a.asset_id === updatedAsset.asset_id);
    if (index !== -1) {
      assets[index] = updatedAsset;
      assets = [...assets];
      notifications.show(`Asset "${updatedAsset.name}" updated successfully`, 'success');
    }
  }
  
  function handleAssetDeleted(event: CustomEvent<{asset_id: string, name: string}>) {
    const { asset_id, name } = event.detail;
    assets = assets.filter(a => a.asset_id !== asset_id);
    notifications.show(`Asset "${name}" deleted successfully`, 'success');
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
      <LoadingSpinner 
        size="lg" 
        message="Loading assets for {$selectedProduct.name}..." 
      />
    {:else if error}
      <ErrorMessage 
        {error} 
        showRetry={retryCount < maxRetries}
        onRetry={retryLoadAssets}
        onDismiss={dismissError}
      />
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

