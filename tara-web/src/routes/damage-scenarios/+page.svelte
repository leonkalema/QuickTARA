<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { selectedProduct } from '$lib/stores/productStore';
  import { damageScenarioApi } from '$lib/api/damageScenarioApi';
  import { assetApi } from '$lib/api/assetApi';
  import { notifications } from '$lib/stores/notificationStore';
  import { authStore } from '$lib/stores/auth';
  import { canPerformTARA, isReadOnly } from '$lib/utils/permissions';
  import { scenarioGeneratorApi } from '$lib/api/scenarioGeneratorApi';
  import DamageScenarioTableNew from '../../features/damage-scenarios/components/DamageScenarioTableNew.svelte';
  import DamageScenarioFilters from '../../components/DamageScenarioFilters.svelte';
  import Pagination from '../../components/Pagination.svelte';
  import type { DamageScenario } from '$lib/types/damageScenario';

  let allDamageScenarios: DamageScenario[] = [];
  let filteredScenarios: DamageScenario[] = [];
  let paginatedScenarios: DamageScenario[] = [];
  let assets: any[] = [];
  let loading = true;
  let error: string | null = null;
  let canManageScenarios = false;
  let isGenerating = false;
  
  // Pagination
  let currentPage = 1;
  let itemsPerPage = 20;
  let showAddForm = false;
  
  // Filters
  let filters = {
    search: '',
    asset: '',
    cia: ''
  };

  async function loadData() {
    if (!$selectedProduct?.scope_id) {
      error = 'Please select a product first';
      loading = false;
      return;
    }

    try {
      loading = true;
      error = null;

      const [scenariosResponse, assetsResponse] = await Promise.all([
        damageScenarioApi.getDamageScenariosByProduct($selectedProduct.scope_id),
        assetApi.getByProduct($selectedProduct.scope_id)
      ]);
      
      allDamageScenarios = scenariosResponse?.scenarios || [];
      assets = assetsResponse?.assets || [];
      applyFilters();

    } catch (err) {
      console.error('Error loading data:', err);
      error = 'Failed to load damage scenarios';
      notifications.show('Failed to load damage scenarios', 'error');
    } finally {
      loading = false;
    }
  }

  function applyFilters() {
    filteredScenarios = allDamageScenarios.filter(scenario => {
      // Search filter
      if (filters.search && !scenario.name.toLowerCase().includes(filters.search.toLowerCase()) && 
          !scenario.description?.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      
      
      // Asset filter
      if (filters.asset && scenario.primary_component_id !== filters.asset) {
        return false;
      }
      
      // CIA filter
      if (filters.cia) {
        const ciaMap: Record<string, boolean> = {
          'confidentiality': scenario.confidentiality_impact,
          'integrity': scenario.integrity_impact,
          'availability': scenario.availability_impact
        };
        if (!ciaMap[filters.cia]) {
          return false;
        }
      }
      
      return true;
    });
    
    // Reset to first page when filters change
    currentPage = 1;
    updatePagination();
  }

  function updatePagination() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    paginatedScenarios = filteredScenarios.slice(startIndex, endIndex);
  }

  function handleFilterChangeEvent(event: CustomEvent) {
    filters = event.detail;
    applyFilters();
  }

  function handlePageChange(event: CustomEvent) {
    currentPage = event.detail.page;
    itemsPerPage = event.detail.itemsPerPage;
    updatePagination();
  }

  function handleScenarioAdded(event: CustomEvent) {
    const newScenario = event.detail;
    allDamageScenarios = [...allDamageScenarios, newScenario];
    applyFilters();
    notifications.show('Damage scenario added successfully', 'success');
  }

  function handleScenarioDeleted(event: CustomEvent) {
    const deletedId = event.detail.scenario_id;
    allDamageScenarios = allDamageScenarios.filter(s => s.scenario_id !== deletedId);
    applyFilters();
    notifications.show('Damage scenario deleted successfully', 'success');
  }

  function clearFilters() {
    filters = { search: '', asset: '', cia: '' };
    applyFilters();
  }

  async function handleAutoGenerate() {
    if (!$selectedProduct?.scope_id) return;
    isGenerating = true;
    try {
      const result = await scenarioGeneratorApi.generateDamageScenarios($selectedProduct.scope_id);
      notifications.show(
        `Generated ${result.damage_scenarios_created} damage scenarios from ${result.assets_processed} assets`,
        'success',
      );
      await loadData();
    } catch (err: any) {
      console.error('Auto-generation failed:', err);
      notifications.show(err.message || 'Auto-generation failed', 'error');
    } finally {
      isGenerating = false;
    }
  }

  function handleFilterChange() {
    applyFilters();
  }

  // Reactive permission checks - wait for auth to be initialized
  $: if ($authStore.isInitialized) {
    canManageScenarios = canPerformTARA() && !isReadOnly();
    
    if ($authStore.isAuthenticated && !canPerformTARA()) {
      goto('/unauthorized');
    }
  }

  // Load data when component mounts or when selected product changes
  onMount(() => {
    loadData();
  });
  
  // Update pagination when filtered scenarios change
  $: if (filteredScenarios) {
    updatePagination();
  }
</script>

<svelte:head>
  <title>Damage Scenarios - QuickTARA</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start space-y-4 lg:space-y-0">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">
        Damage Scenarios
        {#if $selectedProduct && !loading}
          <span class="text-lg font-normal text-gray-500 ml-2">({allDamageScenarios.length} {allDamageScenarios.length === 1 ? 'scenario' : 'scenarios'} total)</span>
        {/if}
      </h1>
      {#if $selectedProduct}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Define potential damage scenarios for <strong>{$selectedProduct.name}</strong>. Each scenario describes what could go wrong with a specific asset and its CIA properties.
        </p>
      {:else}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Please select a product first to view and manage its damage scenarios.
        </p>
      {/if}
    </div>
    {#if $selectedProduct && assets.length > 0 && !loading && canManageScenarios}
      <div class="flex gap-3 self-start">
        <button
          on:click={handleAutoGenerate}
          disabled={isGenerating}
          class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
        >
          {#if isGenerating}
            <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/></svg>
            <span>Generating...</span>
          {:else}
            <span>&#9889; Auto-Generate from Assets</span>
          {/if}
        </button>
        <button
          class="bg-slate-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-700 transition-colors flex items-center space-x-2"
          on:click={() => showAddForm = !showAddForm}
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          <span>{showAddForm ? 'Cancel' : 'New Scenario'}</span>
        </button>
      </div>
    {/if}
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
  {:else if assets.length === 0 && !loading}
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
    {#if loading}
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
      <!-- Filters and Controls -->
      <div class="w-full flex items-center justify-between">
        <div class="flex-1">
          <DamageScenarioFilters 
            {filters}
            {assets}
            on:filterChange={handleFilterChangeEvent}
          />
        </div>
        
        <!-- Clear Filters -->
        {#if filters.search || filters.asset || filters.cia}
          <button
            on:click={clearFilters}
            class="text-slate-600 hover:text-slate-800 px-3 py-2 text-sm font-medium transition-colors ml-4"
          >
            Clear filters
          </button>
        {/if}
      </div>
      
      <!-- Add Form -->
      
      <!-- Damage Scenario Table -->
      <DamageScenarioTableNew 
        damageScenarios={paginatedScenarios}
        {assets}
        isAddingNew={showAddForm}
        on:scenarioAdded={handleScenarioAdded}
        on:scenarioDeleted={handleScenarioDeleted}
        on:cancelAdd={() => showAddForm = false}
      />
      
      <!-- Pagination -->
      <Pagination 
        {currentPage}
        totalItems={filteredScenarios.length}
        {itemsPerPage}
        on:pageChange={handlePageChange}
      />
    {/if}
  {/if}
</div>
