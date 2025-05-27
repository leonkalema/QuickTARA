<script lang="ts">
  import { onMount } from 'svelte';
  import { RefreshCw, AlertCircle, Plus, Target, Database } from '@lucide/svelte';
  import AssetList from './AssetList.svelte';
  import AssetForm from './AssetForm.svelte';
  import { assetApi, AssetType } from '../api/assets';
  import { safeApiCall } from '../utils/error-handler';

  // Component references
  let assetListInstance: any;

  // Props
  export let productId: string | null = null; // If set, only shows assets for this product

  // Summary stats
  let stats = {
    totalAssets: 0,
    byType: {
      [AssetType.FIRMWARE]: 0,
      [AssetType.SOFTWARE]: 0,
      [AssetType.CONFIGURATION]: 0,
      [AssetType.HARDWARE]: 0,
      [AssetType.DATA]: 0,
      [AssetType.OTHER]: 0
    }
  };

  // UI state
  let isLoading = false;
  let showAddAssetForm = false;
  let showViewAssetModal = false;
  let viewingAsset: any = null;
  let showEditAssetModal = false;
  let editingAsset: any = null;

  function updateStats(assets: any[]) {
    stats.totalAssets = assets.length;

    // Reset counts
    Object.keys(stats.byType).forEach(key => {
      stats.byType[key as keyof typeof stats.byType] = 0;
    });

    // Count by type
    assets.forEach(asset => {
      if (asset.asset_type in stats.byType) {
        stats.byType[asset.asset_type as keyof typeof stats.byType]++;
      }
    });
  }

  // Load assets on mount and when productId changes
  onMount(async () => {
    await loadAssets();
  });

  // Reactive statement to reload assets when productId changes
  $: if (productId !== undefined) {
    loadAssets();
  }

  // Load assets from API
  async function loadAssets() {
    isLoading = true;

    try {
      let result;

      if (productId) {
        result = await safeApiCall(() => assetApi.getByProduct(productId));
      } else {
        result = await safeApiCall(() => assetApi.getAll());
      }

      if (result) {
        updateStats(result.assets);

        // Make sure to update the assets list
        if (assetListInstance) {
          assetListInstance.updateAssets(result.assets);
        }
      }
    } catch (err) {
      console.error('Error loading assets:', err);
    } finally {
      isLoading = false;
    }
  }

  // Handle asset creation
  async function handleAssetCreate(event: CustomEvent<any>) {
    const newAssetData = event.detail;

    try {
      const result = await safeApiCall(() => assetApi.create(newAssetData));

      if (result) {
        // Close the form
        showAddAssetForm = false;

        // Refresh the asset list
        await loadAssets();
      }
    } catch (error) {
      console.error("Failed to create asset:", error);
    }
  }

  function handleAssetsUpdate(assets: any[]) {
    updateStats(assets);
  }

  // Handle asset update
  async function handleAssetUpdate(event: CustomEvent<any>) {
    const updatedAssetData = event.detail;
    
    try {
      const result = await safeApiCall(() => assetApi.update(updatedAssetData.asset_id, updatedAssetData));
      
      if (result) {
        // Close the form
        showEditAssetModal = false;
        
        // Refresh the asset list
        await loadAssets();
      }
    } catch (error) {
      console.error("Failed to update asset:", error);
    }
  }
</script>

<div>
  <!-- Stats cards area -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
    <div class="metric-card">
      <div class="flex items-start">
        <Target size={24} style="color: var(--color-primary);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Total Assets</p>
          <p class="metric-value">{stats.totalAssets}</p>
        </div>
      </div>
    </div>

    <div class="metric-card">
      <div class="flex items-start">
        <Database size={24} style="color: var(--color-secondary);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Software Assets</p>
          <p class="metric-value">{stats.byType[AssetType.SOFTWARE]}</p>
        </div>
      </div>
    </div>

    <div class="metric-card">
      <div class="flex items-start">
        <svg class="w-6 h-6 mr-3 mt-1" style="color: var(--color-success);" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
        </svg>
        <div>
          <p class="metric-label">Hardware Assets</p>
          <p class="metric-value">{stats.byType[AssetType.HARDWARE]}</p>
        </div>
      </div>
    </div>
  </div>

  <!-- Action bar -->
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold" style="color: var(--color-text-main);">
      {#if productId}
        Product Assets
      {:else}
        All Assets
      {/if}
    </h2>
    <div class="flex space-x-2">
      <button 
        on:click={loadAssets}
        style="color: var(--color-text-muted); background-color: rgba(255, 255, 255, 0.5);" 
        class="p-2 rounded-md flex items-center gap-1 transition-all duration-200 hover:shadow-sm border border-transparent hover:border-gray-200">
        <RefreshCw size={16} class="{isLoading ? 'animate-spin' : ''}" />
        <span class="sr-only md:not-sr-only">Refresh</span>
      </button>
      
      <button 
        on:click={() => showAddAssetForm = true}
        class="btn btn-primary flex items-center gap-1">
        <Plus size={16} />
        <span>Add Asset</span>
      </button>
    </div>
  </div>
  
  <!-- Asset List Component -->
  <AssetList 
    bind:this={assetListInstance} 
    {productId}
    on:update={(e: CustomEvent<any[]>) => handleAssetsUpdate(e.detail)}
    on:view={(e: CustomEvent<any>) => {
      // Set the asset for viewing and show the view modal
      viewingAsset = e.detail;
      showViewAssetModal = true;
    }}
    on:edit={(e: CustomEvent<any>) => {
      // Set the asset for editing and show the edit modal
      editingAsset = e.detail;
      showEditAssetModal = true;
    }} />
  
  <!-- Asset Form Modal -->  
  {#if showAddAssetForm}
    <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <AssetForm 
          preselectedProductId={productId} 
          on:submit={handleAssetCreate} 
          on:cancel={() => showAddAssetForm = false} 
        />
      </div>
    </div>
  {/if}

  <!-- View Asset Modal -->  
  {#if showViewAssetModal && viewingAsset}
    <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <AssetForm 
          viewMode={true}
          asset={viewingAsset} 
          on:cancel={() => showViewAssetModal = false} 
        />
      </div>
    </div>
  {/if}
  
  <!-- Edit Asset Modal -->  
  {#if showEditAssetModal && editingAsset}
    <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4">
      <div class="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <AssetForm 
          editMode={true}
          asset={editingAsset} 
          on:submit={handleAssetUpdate} 
          on:cancel={() => showEditAssetModal = false} 
        />
      </div>
    </div>
  {/if}
</div>

<style>
  .metric-card {
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid var(--color-border);
    background-color: var(--color-card-bg);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }
  
  .metric-label {
    font-size: 0.875rem;
    color: var(--color-text-muted);
    margin-bottom: 0.25rem;
  }
  
  .metric-value {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-text-main);
  }
</style>
