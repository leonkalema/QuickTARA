<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedProduct } from '../../lib/stores/productStore';
  import { notifications } from '../../lib/stores/notificationStore';
  import { damageScenarioApi } from '../../lib/api/damageScenarioApi';
  import { assetApi } from '../../lib/api/assetApi';
  import type { DamageScenario } from '../../lib/types/damageScenario';
  import type { Asset } from '../../lib/types/asset';
  import DamageScenarioTable from '../../features/damage-scenarios/components/DamageScenarioTableNew.svelte';

  let damageScenarios: DamageScenario[] = [];
  let assets: Asset[] = [];
  let isLoading = true;
  let error = '';

  async function loadData() {
    if (!$selectedProduct) {
      console.log('No product selected');
      return;
    }
    
    console.log('Loading data for product:', $selectedProduct.scope_id);
    isLoading = true;
    error = '';
    
    try {
      // Load both damage scenarios and assets for the selected product
      const [damageResponse, assetResponse] = await Promise.all([
        damageScenarioApi.getDamageScenariosByProduct($selectedProduct.scope_id),
        assetApi.getByProduct($selectedProduct.scope_id)
      ]);
      
      console.log('Loaded damage scenarios:', damageResponse);
      console.log('Loaded assets:', assetResponse);
      
      damageScenarios = damageResponse.scenarios;
      assets = assetResponse.assets;
    } catch (err) {
      console.error('Error loading data:', err);
      error = 'Failed to load damage scenarios';
      notifications.show('Failed to load damage scenarios', 'error');
    } finally {
      isLoading = false;
    }
  }

  function handleScenarioAdded(event: CustomEvent<DamageScenario>) {
    damageScenarios = [...damageScenarios, event.detail];
  }

  function handleScenarioDeleted(event: CustomEvent<string>) {
    damageScenarios = damageScenarios.filter(s => s.scenario_id !== event.detail);
  }

  function handleScenarioUpdated(event: CustomEvent<DamageScenario>) {
    const updatedScenario = event.detail;
    const index = damageScenarios.findIndex(ds => ds.scenario_id === updatedScenario.scenario_id);
    if (index !== -1) {
      damageScenarios[index] = updatedScenario;
      damageScenarios = [...damageScenarios];
    }
  }

  onMount(() => {
    loadData();
  });

  // Reload data when selected product changes
  $: if ($selectedProduct) {
    loadData();
  }
</script>

<svelte:head>
  <title>Damage Scenarios - QuickTARA</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start space-y-4 lg:space-y-0">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Damage Scenarios</h1>
      {#if $selectedProduct}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Define potential damage scenarios for <strong>{$selectedProduct.name}</strong>. 
          Each scenario describes what could go wrong with a specific asset and its CIA properties.
        </p>
      {:else}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Please select a product first to view and manage its damage scenarios.
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
        Select a product from the header dropdown or visit the Products page to choose which product's damage scenarios you want to manage.
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
  {:else if assets.length === 0 && !isLoading}
    <!-- No Assets State -->
    <div class="text-center py-16">
      <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Assets Found</h3>
      <p class="text-gray-500 mb-6 max-w-md mx-auto">
        You need to create assets first before you can define damage scenarios. Assets are the building blocks that can be affected by damage scenarios.
      </p>
      <a
        href="/assets"
        class="bg-slate-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-slate-700 transition-colors inline-flex items-center space-x-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        <span>Create Assets First</span>
      </a>
    </div>
  {:else}
    <!-- Content -->
    {#if isLoading}
      <div class="flex flex-col justify-center items-center py-16">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600 mb-4"></div>
        <p class="text-gray-500">Loading damage scenarios...</p>
      </div>
    {:else if error}
      <div class="bg-red-50 border border-red-200 rounded-lg p-6">
        <div class="flex items-start">
          <svg class="w-6 h-6 text-red-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Error loading damage scenarios</h3>
            <p class="text-sm text-red-700 mt-1">{error}</p>
            <button
              on:click={loadData}
              class="mt-3 bg-red-100 text-red-800 px-3 py-1 rounded text-sm hover:bg-red-200 transition-colors"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    {:else}
      <!-- Damage Scenario Table -->
      <DamageScenarioTable 
        {damageScenarios}
        {assets}
        productId={$selectedProduct.scope_id}
        on:scenarioAdded={handleScenarioAdded}
        on:scenarioDeleted={handleScenarioDeleted}
      />
    {/if}
  {/if}
</div>
