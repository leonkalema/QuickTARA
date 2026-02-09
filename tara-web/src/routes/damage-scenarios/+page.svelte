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
  import ConfirmDialog from '../../components/ConfirmDialog.svelte';
  import type { DamageScenario } from '$lib/types/damageScenario';
  import type { GenerationPreview } from '$lib/api/scenarioGeneratorApi';

  let allDamageScenarios: DamageScenario[] = [];
  let filteredScenarios: DamageScenario[] = [];
  let paginatedScenarios: DamageScenario[] = [];
  let assets: any[] = [];
  let loading = true;
  let error: string | null = null;
  let canManageScenarios = false;
  let isGenerating = false;
  
  // Confirmation dialog
  let showConfirmGenerate = false;
  let generationPreview: GenerationPreview | null = null;
  
  // Status filter
  let statusFilter: 'all' | 'draft' | 'accepted' = 'all';
  
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
  
  // Computed counts
  $: draftCount = allDamageScenarios.filter(s => s.status === 'draft').length;
  $: acceptedCount = allDamageScenarios.filter(s => s.status === 'accepted').length;

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
      // Status filter
      if (statusFilter === 'draft' && scenario.status !== 'draft') return false;
      if (statusFilter === 'accepted' && scenario.status !== 'accepted') return false;
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
        if (!ciaMap[filters.cia]) return false;
      }
      return true;
    });
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
    statusFilter = 'all';
    applyFilters();
  }

  function setStatusFilter(value: 'all' | 'draft' | 'accepted') {
    statusFilter = value;
    applyFilters();
  }

  async function handleAutoGenerateClick() {
    if (!$selectedProduct?.scope_id) return;
    try {
      generationPreview = await scenarioGeneratorApi.previewDamageGeneration($selectedProduct.scope_id);
      showConfirmGenerate = true;
    } catch (err: any) {
      notifications.show(err.message || 'Failed to preview generation', 'error');
    }
  }

  async function confirmGenerate() {
    if (!$selectedProduct?.scope_id) return;
    showConfirmGenerate = false;
    isGenerating = true;
    try {
      const result = await scenarioGeneratorApi.generateDamageScenarios($selectedProduct.scope_id);
      const msg = result.drafts_replaced > 0
        ? `Generated ${result.damage_scenarios_created} scenarios (replaced ${result.drafts_replaced} old drafts)`
        : `Generated ${result.damage_scenarios_created} damage scenarios from ${result.assets_processed} assets`;
      notifications.show(msg, 'success');
      await loadData();
    } catch (err: any) {
      notifications.show(err.message || 'Auto-generation failed', 'error');
    } finally {
      isGenerating = false;
    }
  }

  async function bulkAcceptDrafts() {
    const drafts = allDamageScenarios.filter(s => s.status === 'draft');
    if (!drafts.length) return;
    let accepted = 0;
    for (const draft of drafts) {
      try {
        await damageScenarioApi.acceptScenario(draft.scenario_id);
        accepted++;
      } catch { /* skip failures */ }
    }
    notifications.show(`Accepted ${accepted} scenarios`, 'success');
    await loadData();
  }

  async function bulkDeleteDrafts() {
    const drafts = allDamageScenarios.filter(s => s.status === 'draft');
    if (!drafts.length) return;
    let deleted = 0;
    for (const draft of drafts) {
      try {
        await damageScenarioApi.delete(draft.scenario_id);
        deleted++;
      } catch { /* skip failures */ }
    }
    notifications.show(`Deleted ${deleted} draft scenarios`, 'success');
    await loadData();
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

<div class="space-y-5">
  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4">
    <div>
      <h1 class="text-xl font-bold tracking-tight" style="color: var(--color-text-primary);">
        Damage Scenarios
        {#if $selectedProduct && !loading}
          <span class="text-sm font-normal ml-2" style="color: var(--color-text-tertiary);">({allDamageScenarios.length})</span>
        {/if}
      </h1>
      <p class="text-sm mt-1" style="color: var(--color-text-secondary);">
        {#if $selectedProduct}
          What could go wrong with <strong style="color: var(--color-text-primary);">{$selectedProduct.name}</strong> assets.
        {:else}
          Select a product first to manage damage scenarios.
        {/if}
      </p>
    </div>
    {#if $selectedProduct && assets.length > 0 && !loading && canManageScenarios}
      <div class="flex gap-2 self-start">
        <button
          on:click={handleAutoGenerateClick}
          disabled={isGenerating}
          class="px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
          style="background: var(--color-accent-secondary); color: var(--color-text-inverse);"
        >
          {#if isGenerating}
            <svg class="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/></svg>
            Generating...
          {:else}
            Auto-Generate
          {/if}
        </button>
        <button
          class="px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2"
          style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
          on:click={() => showAddForm = !showAddForm}
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
          {showAddForm ? 'Cancel' : 'New Scenario'}
        </button>
      </div>
    {/if}
  </div>

  {#if !$selectedProduct}
    <div class="relative flex flex-col items-center py-16 text-center">
      <div class="absolute inset-0 radar-bg pointer-events-none"></div>
      <div class="relative z-10 flex flex-col items-center max-w-md">
        <div class="w-14 h-14 rounded-xl flex items-center justify-center mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
        </div>
        <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No Product Selected</h3>
        <p class="text-sm mb-6" style="color: var(--color-text-secondary);">Select a product from the header to manage its damage scenarios.</p>
        <a href="/products" class="px-4 py-2 rounded-md text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Select a Product</a>
      </div>
    </div>
  {:else if assets.length === 0 && !loading}
    <div class="relative flex flex-col items-center py-16 text-center">
      <div class="absolute inset-0 radar-bg pointer-events-none"></div>
      <div class="relative z-10 flex flex-col items-center max-w-md">
        <div class="w-14 h-14 rounded-xl flex items-center justify-center mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
        </div>
        <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No Assets Found</h3>
        <p class="text-sm mb-6" style="color: var(--color-text-secondary);">Create assets first — they're the building blocks for damage scenarios.</p>
        <a href="/assets" class="px-4 py-2 rounded-md text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Create Assets First</a>
      </div>
    </div>
  {:else}
    {#if loading}
      <div class="flex flex-col items-center py-16">
        <div class="animate-spin rounded-full h-7 w-7 border-2 border-t-transparent mb-3" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
        <p class="text-sm" style="color: var(--color-text-tertiary);">Loading damage scenarios...</p>
      </div>
    {:else if error}
      <div class="rounded-lg p-4" style="background: var(--color-error-bg); border: 1px solid var(--color-error);">
        <h3 class="text-sm font-medium" style="color: var(--color-error);">Error loading damage scenarios</h3>
        <p class="text-sm mt-1" style="color: var(--color-text-secondary);">{error}</p>
        <button on:click={loadData} class="mt-2 px-3 py-1 rounded text-xs font-medium" style="color: var(--color-error);">Try again</button>
      </div>
    {:else}
      <!-- Status filter tabs + bulk actions -->
      {#if draftCount > 0 || acceptedCount > 0}
        <div class="flex items-center justify-between">
          <div class="flex gap-0.5 rounded-md p-0.5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
            <button on:click={() => setStatusFilter('all')}
              class="px-3 py-1.5 text-xs rounded font-medium transition-colors"
              style="background: {statusFilter === 'all' ? 'var(--color-bg-elevated)' : 'transparent'}; color: {statusFilter === 'all' ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)'};">
              All ({allDamageScenarios.length})
            </button>
            {#if draftCount > 0}
              <button on:click={() => setStatusFilter('draft')}
                class="px-3 py-1.5 text-xs rounded font-medium transition-colors"
                style="background: {statusFilter === 'draft' ? 'var(--color-warning-bg)' : 'transparent'}; color: {statusFilter === 'draft' ? 'var(--color-warning)' : 'var(--color-text-tertiary)'};">
                Draft ({draftCount})
              </button>
            {/if}
            <button on:click={() => setStatusFilter('accepted')}
              class="px-3 py-1.5 text-xs rounded font-medium transition-colors"
              style="background: {statusFilter === 'accepted' ? 'var(--color-success-bg)' : 'transparent'}; color: {statusFilter === 'accepted' ? 'var(--color-success)' : 'var(--color-text-tertiary)'};">
              Accepted ({acceptedCount})
            </button>
          </div>
          {#if draftCount > 0 && canManageScenarios}
            <div class="flex gap-2">
              <button on:click={bulkAcceptDrafts}
                class="text-xs font-medium px-3 py-1.5 rounded-md transition-colors"
                style="color: var(--color-success); border: 1px solid var(--color-success-bg);">
                Accept all {draftCount} drafts
              </button>
              <button on:click={bulkDeleteDrafts}
                class="text-xs font-medium px-3 py-1.5 rounded-md transition-colors"
                style="color: var(--color-error); border: 1px solid var(--color-error-bg);">
                Delete all drafts
              </button>
            </div>
          {/if}
        </div>
      {/if}

      <!-- Filters and Controls -->
      <div class="w-full flex items-center justify-between">
        <div class="flex-1">
          <DamageScenarioFilters 
            {filters}
            {assets}
            on:filterChange={handleFilterChangeEvent}
          />
        </div>
        {#if filters.search || filters.asset || filters.cia}
          <button on:click={clearFilters} class="text-xs font-medium ml-4" style="color: var(--color-text-link);">Clear filters</button>
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

<!-- Generation Confirmation Dialog -->
<ConfirmDialog
  bind:isOpen={showConfirmGenerate}
  title="Auto-Generate Damage Scenarios"
  message={generationPreview
    ? `This will generate ${generationPreview.scenarios_to_generate} damage scenarios from ${generationPreview.assets_count} assets.${generationPreview.existing_drafts > 0 ? ` ${generationPreview.existing_drafts} existing drafts will be replaced.` : ''} Scenarios will be created as drafts for your review.`
    : 'Generating...'}
  variant="info"
  confirmText="Generate"
  cancelText="Cancel"
  on:confirm={confirmGenerate}
  on:cancel={() => showConfirmGenerate = false}
/>
