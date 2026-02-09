<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { selectedProduct } from '$lib/stores/productStore';
  import { notifications } from '$lib/stores/notificationStore';
  import { damageScenarioApi } from '$lib/api/damageScenarioApi';
  import { threatScenarioApi } from '$lib/api/threatScenarioApi';
  import { authStore } from '$lib/stores/auth';
  import { canPerformTARA, isReadOnly } from '$lib/utils/permissions';
  import { scenarioGeneratorApi } from '$lib/api/scenarioGeneratorApi';
  import type { DamageScenario } from '$lib/types/damageScenario';
  import type { ThreatScenario } from '$lib/types/threatScenario';
  import ThreatScenarioTable from '../../features/threat-scenarios/components/ThreatScenarioTable.svelte';
  import Pagination from '../../components/Pagination.svelte';
  import ConfirmDialog from '../../components/ConfirmDialog.svelte';

  let damageScenarios: DamageScenario[] = [];
  let threatScenarios: ThreatScenario[] = [];
  let loading = false;
  let showAddForm = false;
  let canManageScenarios = false;
  let isGenerating = false;
  let showConfirmGenerate = false;
  let statusFilter: 'all' | 'draft' | 'accepted' = 'all';
  
  // Pagination
  let currentPage = 1;
  let itemsPerPage = 10;
  
  // Filters
  let searchTerm = '';
  let selectedDamageScenario = '';
  
  $: draftCount = threatScenarios.filter(s => s.status === 'draft').length;
  $: acceptedCount = threatScenarios.filter(s => s.status === 'accepted').length;

  $: filteredScenarios = threatScenarios.filter(scenario => {
    if (statusFilter === 'draft' && scenario.status !== 'draft') return false;
    if (statusFilter === 'accepted' && scenario.status !== 'accepted') return false;
    const matchesSearch = scenario.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         scenario.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         scenario.attack_vector?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  $: paginatedScenarios = filteredScenarios.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Reactive permission checks - wait for auth to be initialized
  $: if ($authStore.isInitialized) {
    canManageScenarios = canPerformTARA() && !isReadOnly();
    
    if ($authStore.isAuthenticated && !canPerformTARA()) {
      goto('/unauthorized');
    }
  }

  onMount(async () => {
    if ($selectedProduct?.scope_id) {
      await loadData();
    }
  });

  $: if ($selectedProduct?.scope_id) {
    loadData();
  }

  // Watch for damage scenario filter changes and reload data
  $: if ($selectedProduct?.scope_id && selectedDamageScenario !== undefined) {
    loadThreatScenarios();
  }

  async function loadData() {
    if (!$selectedProduct?.scope_id) return;
    
    loading = true;
    try {
      // Load damage scenarios first
      const damageResponse = await damageScenarioApi.getDamageScenariosByProduct($selectedProduct.scope_id);
      damageScenarios = damageResponse.scenarios;
     
      
      // Load threat scenarios
      await loadThreatScenarios();
    } catch (error) {
      console.error('Error loading data:', error);
      notifications.show('Failed to load threat scenarios', 'error');
    } finally {
      loading = false;
    }
  }

  async function loadThreatScenarios() {
    if (!$selectedProduct?.scope_id) return;
    
    try {
      let threatResponse;
      if (selectedDamageScenario) {
        // Filter by damage scenario using API
        threatResponse = await threatScenarioApi.getThreatScenariosByDamageScenario(selectedDamageScenario);
      } else {
        // Load all threat scenarios for the product
        threatResponse = await threatScenarioApi.getThreatScenariosByProduct($selectedProduct.scope_id);
      }
      threatScenarios = threatResponse.threat_scenarios;
      
    } catch (error) {
      console.error('Error loading threat scenarios:', error);
      notifications.show('Failed to load threat scenarios', 'error');
    }
  }

  function handleScenarioAdded(event: CustomEvent) {
    threatScenarios = [...threatScenarios, event.detail];
    showAddForm = false;
  }

  function handleScenarioDeleted(event: CustomEvent) {
    threatScenarios = threatScenarios.filter(s => s.threat_scenario_id !== event.detail.threat_scenario_id);
  }

  function clearFilters() {
    searchTerm = '';
    selectedDamageScenario = '';
    currentPage = 1;
  }

  function getDamageScenarioName(damageScenarioId: string): string {
    const scenario = damageScenarios.find(ds => ds.scenario_id === damageScenarioId);
    return scenario?.name || 'Unknown Damage Scenario';
  }

  function handleAutoGenerateClick() {
    if (!$selectedProduct?.scope_id) return;
    showConfirmGenerate = true;
  }

  async function confirmGenerate() {
    if (!$selectedProduct?.scope_id) return;
    showConfirmGenerate = false;
    isGenerating = true;
    try {
      const result = await scenarioGeneratorApi.generateThreatScenarios($selectedProduct.scope_id);
      const msg = result.drafts_replaced > 0
        ? `Generated ${result.threat_scenarios_created} scenarios (replaced ${result.drafts_replaced} old drafts)`
        : `Generated ${result.threat_scenarios_created} threat scenarios from ${result.damage_scenarios_used} damage scenarios`;
      notifications.show(msg, 'success');
      await loadData();
    } catch (error: any) {
      notifications.show(error.message || 'Auto-generation failed. Do you have damage scenarios?', 'error');
    } finally {
      isGenerating = false;
    }
  }

  async function bulkAcceptDrafts() {
    const drafts = threatScenarios.filter(s => s.status === 'draft');
    if (!drafts.length) return;
    let accepted = 0;
    for (const d of drafts) {
      try {
        await threatScenarioApi.acceptScenario(d.threat_scenario_id);
        accepted++;
      } catch { /* skip */ }
    }
    notifications.show(`Accepted ${accepted} scenarios`, 'success');
    await loadData();
  }

  async function bulkDeleteDrafts() {
    const drafts = threatScenarios.filter(s => s.status === 'draft');
    if (!drafts.length) return;
    let deleted = 0;
    for (const d of drafts) {
      try {
        await threatScenarioApi.deleteThreatScenario(d.threat_scenario_id);
        deleted++;
      } catch { /* skip */ }
    }
    notifications.show(`Deleted ${deleted} draft scenarios`, 'success');
    await loadData();
  }

  function setStatusFilter(value: 'all' | 'draft' | 'accepted') {
    statusFilter = value;
  }
</script>

<div class="space-y-5">
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4">
    <div>
      <h1 class="text-xl font-bold tracking-tight" style="color: var(--color-text-primary);">
        Threat Scenarios
      </h1>
      <p class="text-sm mt-1" style="color: var(--color-text-secondary);">
        {#if $selectedProduct}
          How attacks could happen against <strong style="color: var(--color-text-primary);">{$selectedProduct.name}</strong>.
        {:else}
          Select a product to manage threat scenarios.
        {/if}
      </p>
    </div>
    {#if canManageScenarios}
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
          on:click={() => showAddForm = !showAddForm}
          class="px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2"
          style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        >
          {showAddForm ? 'Cancel' : 'New Threat Scenario'}
        </button>
      </div>
    {/if}
  </div>

  {#if !$selectedProduct}
    <div class="relative flex flex-col items-center py-16 text-center">
      <div class="absolute inset-0 radar-bg pointer-events-none"></div>
      <div class="relative z-10 flex flex-col items-center max-w-md">
        <div class="w-14 h-14 rounded-xl flex items-center justify-center mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
          <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
        </div>
        <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No Product Selected</h3>
        <p class="text-sm" style="color: var(--color-text-secondary);">Select a product from the header to manage threat scenarios.</p>
      </div>
    </div>
  {:else if !damageScenarios || damageScenarios.length === 0}
    <div class="relative flex flex-col items-center py-16 text-center">
      <div class="absolute inset-0 radar-bg pointer-events-none"></div>
      <div class="relative z-10 flex flex-col items-center max-w-md">
        <div class="w-14 h-14 rounded-xl flex items-center justify-center mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
          <svg class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" /></svg>
        </div>
        <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No Damage Scenarios Found</h3>
        <p class="text-sm mb-6" style="color: var(--color-text-secondary);">Create damage scenarios first — threats describe how damage could happen.</p>
        <a href="/damage-scenarios" class="px-4 py-2 rounded-md text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Go to Damage Scenarios</a>
      </div>
    </div>
  {:else}
    <!-- Status filter tabs + bulk actions -->
    {#if draftCount > 0 || acceptedCount > 0}
      <div class="flex items-center justify-between">
        <div class="flex gap-0.5 rounded-md p-0.5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
          <button on:click={() => setStatusFilter('all')}
            class="px-3 py-1.5 text-xs rounded font-medium transition-colors"
            style="background: {statusFilter === 'all' ? 'var(--color-bg-elevated)' : 'transparent'}; color: {statusFilter === 'all' ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)'};">
            All ({threatScenarios.length})
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

    <!-- Filters -->
    <div class="rounded-lg p-3" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
      <div class="flex flex-wrap gap-3 items-center">
        <div class="flex-1 min-w-64">
          <input
            bind:value={searchTerm}
            placeholder="Search threat scenarios..."
            class="w-full px-3 py-2 rounded-md text-sm border-0 focus:ring-1 focus:outline-none"
            style="background: var(--color-bg-inset); color: var(--color-text-primary); --tw-ring-color: var(--color-border-focus);"
          />
        </div>
        <div class="min-w-48">
          <select bind:value={selectedDamageScenario}
            class="w-full px-3 py-2 rounded-md text-sm border-0 focus:ring-1 focus:outline-none"
            style="background: var(--color-bg-inset); color: var(--color-text-primary); --tw-ring-color: var(--color-border-focus);">
            <option value="">All damage scenarios</option>
            {#each damageScenarios as scenario}
              <option value={scenario.scenario_id}>{scenario.name}</option>
            {/each}
          </select>
        </div>
        {#if searchTerm || selectedDamageScenario}
          <button on:click={clearFilters} class="text-xs font-medium" style="color: var(--color-text-link);">Clear</button>
        {/if}
      </div>
    </div>
    
    <!-- Threat Scenario Table -->
    <ThreatScenarioTable 
      threatScenarios={paginatedScenarios}
      {damageScenarios}
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
      on:pageChange={(e) => currentPage = e.detail.page}
    />
  {/if}
</div>

<ConfirmDialog
  bind:isOpen={showConfirmGenerate}
  title="Auto-Generate Threat Scenarios"
  message={`This will generate threat scenarios from ${damageScenarios.length} damage scenarios by matching the MITRE ATT&CK ICS catalog. Any existing auto-generated drafts will be replaced. New scenarios will be created as drafts for your review.`}
  variant="info"
  confirmText="Generate"
  cancelText="Cancel"
  on:confirm={confirmGenerate}
  on:cancel={() => showConfirmGenerate = false}
/>
