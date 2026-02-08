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

  let damageScenarios: DamageScenario[] = [];
  let threatScenarios: ThreatScenario[] = [];
  let loading = false;
  let showAddForm = false;
  let canManageScenarios = false;
  let isGenerating = false;
  
  // Pagination
  let currentPage = 1;
  let itemsPerPage = 10;
  
  // Filters
  let searchTerm = '';
  let selectedDamageScenario = '';

  $: filteredScenarios = threatScenarios.filter(scenario => {
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

  async function handleAutoGenerate() {
    if (!$selectedProduct?.scope_id) return;
    isGenerating = true;
    try {
      const result = await scenarioGeneratorApi.generateScenarios($selectedProduct.scope_id);
      notifications.show(
        `Generated ${result.damage_scenarios_created} damage + ${result.threat_scenarios_created} threat scenarios from ${result.assets_processed} assets`,
        'success',
      );
      await loadData();
    } catch (error: any) {
      console.error('Auto-generation failed:', error);
      notifications.show(error.message || 'Auto-generation failed', 'error');
    } finally {
      isGenerating = false;
    }
  }
</script>

<div class="container mx-auto px-6 py-8">
  <div class="flex justify-between items-center mb-8">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Threat Scenarios</h1>
      <p class="text-gray-600 mt-2">
        {#if $selectedProduct}
          Managing threat scenarios for {$selectedProduct.name}
        {:else}
          Select a product to manage threat scenarios
        {/if}
      </p>
    </div>
    
    {#if canManageScenarios}
      <div class="flex gap-3">
        <button
          on:click={handleAutoGenerate}
          disabled={isGenerating}
          class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium transition-colors shadow-md flex items-center gap-2"
        >
          {#if isGenerating}
            <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"/></svg>
            Generating...
          {:else}
            &#9889; Auto-Generate Scenarios
          {/if}
        </button>
        <button
          on:click={() => showAddForm = !showAddForm}
          class="bg-black hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-medium transition-colors shadow-md"
        >
          {showAddForm ? 'Cancel' : 'New Threat Scenario'}
        </button>
      </div>
    {/if}
  </div>

  {#if !$selectedProduct}
    <div class="text-center py-12">
      <div class="text-gray-400 mb-4">
        <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Product Selected</h3>
      <p class="text-gray-500">Please select a product from the navigation to manage threat scenarios.</p>
    </div>
  {:else if !damageScenarios || damageScenarios.length === 0}
    <div class="text-center py-12">
      <div class="text-gray-400 mb-4">
        <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Damage Scenarios Found</h3>
      <p class="text-gray-500 mb-4">You need to create damage scenarios first before adding threat scenarios.</p>
      <a href="/damage-scenarios" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors inline-block">
        Go to Damage Scenarios
      </a>
    </div>
  {:else}
    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg border border-gray-200 mb-6">
      <div class="flex flex-wrap gap-4 items-center">
        <div class="flex-1 min-w-64">
          <input
            bind:value={searchTerm}
            placeholder="Search threat scenarios..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
        
        <div class="min-w-48">
          <select bind:value={selectedDamageScenario} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent">
            <option value="">All damage scenarios</option>
            {#each damageScenarios as scenario}
              <option value={scenario.scenario_id}>{scenario.name}</option>
            {/each}
          </select>
        </div>

        {#if searchTerm || selectedDamageScenario}
          <button
            on:click={clearFilters}
            class="text-slate-600 hover:text-slate-800 px-3 py-2 text-sm font-medium transition-colors"
          >
            Clear filters
          </button>
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
      on:pageChange={(e) => currentPage = e.detail}
    />
  {/if}
</div>
