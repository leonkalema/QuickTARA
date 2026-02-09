<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { selectedProduct } from '$lib/stores/productStore';
  import { notifications } from '$lib/stores/notificationStore';
  import { threatScenarioApi } from '$lib/api/threatScenarioApi';
  import { attackPathApi } from '$lib/api/attackPathApi';
  import { canPerformTARA, isReadOnly, isAnalyst } from '$lib/utils/permissions';
  import { authStore } from '$lib/stores/auth';
  import type { ThreatScenario } from '$lib/types/threatScenario';
  import type { AttackPath, CreateAttackPathRequest, FeasibilityRating } from '$lib/types/attackPath';
  import FeasibilityRatingSelector from '../../components/FeasibilityRatingSelector.svelte';
  import ConfirmationModal from '../../components/ui/ConfirmationModal.svelte';

  let threatScenarios: ThreatScenario[] = [];
  let attackPaths: AttackPath[] = [];
  let loading = false;
  let showAddForm = false;
  let selectedThreatScenario = '';
  let searchTerm = '';
  let expandedCards: Set<string> = new Set();
  let canManageRisk = false;
  
  // Form data
  let formData: CreateAttackPathRequest = {
    threat_scenario_id: '',
    name: '',
    description: '',
    attack_steps: '',
    feasibility_rating: {
      elapsed_time: 0,
      specialist_expertise: 0,
      knowledge_of_target: 0,
      window_of_opportunity: 0,
      equipment: 0
    }
  };

  // Delete confirmation
  let showDeleteModal = false;
  let attackPathToDelete: AttackPath | null = null;
  let isDeleting = false;

  $: filteredThreatScenarios = threatScenarios.filter(scenario => {
    const matchesSearch = !searchTerm || 
                         scenario.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         scenario.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSelected = !selectedThreatScenario || 
                           scenario.threat_scenario_id === selectedThreatScenario;
    
    return matchesSearch && matchesSelected;
  });

  $: filteredAttackPaths = attackPaths.filter(path => {
    if (!selectedThreatScenario) return true;
    return path.threat_scenario_id === selectedThreatScenario;
  });

  function getAttackPathAFR(afs: number): string {
    if (afs >= 25) return 'Very Low';
    if (afs >= 20) return 'Low';
    if (afs >= 14) return 'Medium';
    if (afs >= 1) return 'High';
    return 'Very High';
  }

  function getAttackPathRatingColor(afs: number): string {
    if (afs >= 25) return 'bg-red-100 text-red-800';      // Very Low
    if (afs >= 20) return 'bg-orange-100 text-orange-800'; // Low
    if (afs >= 14) return 'bg-yellow-100 text-yellow-800'; // Medium
    if (afs >= 1) return 'bg-green-100 text-green-800';    // High
    return 'bg-blue-100 text-blue-800';                    // Very High
  }

  // Reactive permission checks - wait for auth to be initialized
  $: if ($authStore.isInitialized) {
    canManageRisk = canPerformTARA() && !isReadOnly();
    
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

  async function loadData() {
    if (!$selectedProduct?.scope_id) return;
    
    loading = true;
    try {
      const [threatResponse, attackPathResponse] = await Promise.all([
        threatScenarioApi.getThreatScenariosByProduct($selectedProduct.scope_id),
        attackPathApi.getByProduct($selectedProduct.scope_id)
      ]);
      
      threatScenarios = threatResponse.threat_scenarios;
      attackPaths = attackPathResponse.attack_paths;
    } catch (error) {
      console.error('Error loading data:', error);
      notifications.show('Failed to load risk assessment data', 'error');
    } finally {
      loading = false;
    }
  }

  function getThreatScenarioName(threatScenarioId: string): string {
    const scenario = threatScenarios.find(ts => ts.threat_scenario_id === threatScenarioId);
    return scenario?.name || 'Unknown Threat Scenario';
  }

  function startAddAttackPath(threatScenarioId?: string) {
    formData = {
      threat_scenario_id: threatScenarioId || '',
      name: '',
      description: '',
      attack_steps: '',
      feasibility_rating: {
        elapsed_time: 0,
        specialist_expertise: 0,
        knowledge_of_target: 0,
        window_of_opportunity: 0,
        equipment: 0
      }
    };
    showAddForm = true;
  }

  async function handleSubmit() {
    if (!formData.name.trim() || !formData.attack_steps.trim() || !formData.threat_scenario_id) {
      notifications.show('Please fill in all required fields', 'error');
      return;
    }

    try {
      const newAttackPath = await attackPathApi.create(formData);
      // Reload all data to ensure UI is in sync
      await loadData();
      notifications.show('Attack path created successfully', 'success');
      showAddForm = false;
    } catch (error) {
      console.error('Error creating attack path:', error);
      notifications.show('Failed to create attack path', 'error');
    }
  }

  function handleDeleteAttackPath(attackPath: AttackPath) {
    attackPathToDelete = attackPath;
    showDeleteModal = true;
  }

  async function confirmDelete() {
    if (!attackPathToDelete) return;

    isDeleting = true;
    try {
      await attackPathApi.delete(attackPathToDelete.attack_path_id);
      // Reload all data to ensure UI is in sync
      await loadData();
      notifications.show('Attack path deleted successfully', 'success');
      showDeleteModal = false;
      attackPathToDelete = null;
    } catch (error) {
      console.error('Error deleting attack path:', error);
      notifications.show('Failed to delete attack path', 'error');
    } finally {
      isDeleting = false;
    }
  }

  function cancelDelete() {
    showDeleteModal = false;
    attackPathToDelete = null;
  }

  function getAttackPathsForThreat(threatScenarioId: string): AttackPath[] {
    return attackPaths.filter(ap => ap.threat_scenario_id === threatScenarioId);
  }

  function formatAttackSteps(steps: string): string[] {
    return steps.split('\n').filter(step => step.trim().length > 0);
  }

  function toggleCard(cardId: string) {
    if (expandedCards.has(cardId)) {
      expandedCards.delete(cardId);
    } else {
      expandedCards.add(cardId);
    }
    expandedCards = expandedCards; // Trigger reactivity
  }
</script>

<svelte:head>
  <title>Risk Assessment - QuickTARA</title>
</svelte:head>

<div class="space-y-5">
  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4">
    <div>
      <h1 class="text-xl font-bold tracking-tight" style="color: var(--color-text-primary);">Risk Assessment</h1>
      <p class="text-sm mt-1" style="color: var(--color-text-secondary);">
        {#if $selectedProduct}
          Attack paths & feasibility for <strong style="color: var(--color-text-primary);">{$selectedProduct.name}</strong>.
        {:else}
          Select a product to begin risk assessment.
        {/if}
      </p>
    </div>
    {#if $selectedProduct && threatScenarios.length > 0 && !loading && canManageRisk}
      <button
        class="px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 self-start"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        on:click={() => startAddAttackPath()}
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
        New Attack Path
      </button>
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
        <p class="text-sm mb-6" style="color: var(--color-text-secondary);">Select a product from the header to begin risk assessment.</p>
        <a href="/products" class="px-4 py-2 rounded-md text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Select a Product</a>
      </div>
    </div>
  {:else if threatScenarios.length === 0 && !loading}
    <div class="relative flex flex-col items-center py-16 text-center">
      <div class="absolute inset-0 radar-bg pointer-events-none"></div>
      <div class="relative z-10 flex flex-col items-center max-w-md">
        <div class="w-14 h-14 rounded-xl flex items-center justify-center mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z"></path></svg>
        </div>
        <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No Threat Scenarios Found</h3>
        <p class="text-sm mb-6" style="color: var(--color-text-secondary);">Create threat scenarios first to assess attack paths and feasibility.</p>
        <a href="/threat-scenarios" class="px-4 py-2 rounded-md text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Create Threat Scenarios</a>
      </div>
    </div>
  {:else}
    {#if loading}
      <div class="flex flex-col items-center py-16">
        <div class="animate-spin rounded-full h-7 w-7 border-2 border-t-transparent mb-3" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
        <p class="text-sm" style="color: var(--color-text-tertiary);">Loading risk assessment data...</p>
      </div>
    {:else}
      <!-- Filters -->
      <div class="rounded-lg p-3" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
        <div class="flex flex-wrap gap-3 items-center">
          <div class="flex-1 min-w-64">
            <input bind:value={searchTerm} placeholder="Search threat scenarios..."
              class="w-full px-3 py-2 rounded-md text-sm border-0 focus:ring-1 focus:outline-none"
              style="background: var(--color-bg-inset); color: var(--color-text-primary); --tw-ring-color: var(--color-border-focus);" />
          </div>
          <div class="min-w-48">
            <select bind:value={selectedThreatScenario}
              class="w-full px-3 py-2 rounded-md text-sm border-0 focus:ring-1 focus:outline-none"
              style="background: var(--color-bg-inset); color: var(--color-text-primary); --tw-ring-color: var(--color-border-focus);">
              <option value="">All threat scenarios</option>
              {#each threatScenarios as scenario}
                <option value={scenario.threat_scenario_id}>{scenario.name}</option>
              {/each}
            </select>
          </div>
          {#if searchTerm || selectedThreatScenario}
            <button on:click={() => { searchTerm = ''; selectedThreatScenario = ''; }}
              class="text-xs font-medium" style="color: var(--color-text-link);">Clear</button>
          {/if}
        </div>
      </div>

      <!-- Add Attack Path Form -->
      {#if showAddForm}
        <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">Create New Attack Path</h3>
            <button on:click={() => showAddForm = false} style="color: var(--color-text-tertiary);">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div class="space-y-4">
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Threat Scenario *</label>
                <select bind:value={formData.threat_scenario_id} required
                  class="w-full px-3 py-2 rounded-md text-sm border-0"
                  style="background: var(--color-bg-inset); color: var(--color-text-primary);">
                  <option value="">Select a threat scenario</option>
                  {#each threatScenarios as scenario}
                    <option value={scenario.threat_scenario_id}>{scenario.name}</option>
                  {/each}
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Attack Path Name *</label>
                <input type="text" bind:value={formData.name} placeholder="e.g., Remote Code Execution via Buffer Overflow" required
                  class="w-full px-3 py-2 rounded-md text-sm border-0"
                  style="background: var(--color-bg-inset); color: var(--color-text-primary);" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Description</label>
                <textarea bind:value={formData.description} placeholder="Brief description..." rows="3"
                  class="w-full px-3 py-2 rounded-md text-sm border-0"
                  style="background: var(--color-bg-inset); color: var(--color-text-primary);"></textarea>
              </div>
              <div>
                <label class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">Attack Steps *</label>
                <textarea bind:value={formData.attack_steps}
                  placeholder="Enter each attack step on a new line:&#10;1. Reconnaissance&#10;2. Vulnerability scanning&#10;3. Exploit development&#10;..."
                  rows="8" required
                  class="w-full px-3 py-2 rounded-md text-sm font-mono border-0"
                  style="background: var(--color-bg-inset); color: var(--color-text-primary);"></textarea>
                <p class="text-[11px] mt-1" style="color: var(--color-text-tertiary);">Enter each step on a separate line.</p>
              </div>
            </div>
            <div>
              <h4 class="text-xs font-medium mb-3" style="color: var(--color-text-secondary);">Feasibility Assessment</h4>
              <FeasibilityRatingSelector bind:feasibilityRating={formData.feasibility_rating} />
            </div>
          </div>
          <div class="flex justify-end gap-2 mt-5 pt-5" style="border-top: 1px solid var(--color-border-subtle);">
            <button type="button" on:click={() => showAddForm = false}
              class="px-3 py-2 text-sm font-medium rounded-md transition-colors"
              style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);">Cancel</button>
            <button type="button" on:click={handleSubmit}
              class="px-3 py-2 text-sm font-medium rounded-md transition-colors"
              style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Create Attack Path</button>
          </div>
        </div>
      {/if}

      <!-- Threat Scenarios with Attack Paths -->
      <div class="space-y-4">
        {#each filteredThreatScenarios as threatScenario}
          {@const threatAttackPaths = getAttackPathsForThreat(threatScenario.threat_scenario_id)}
          <div class="rounded-lg overflow-hidden" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
            <div class="px-5 py-3" style="background: var(--color-bg-elevated); border-bottom: 1px solid var(--color-border-subtle);">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <button on:click={() => toggleCard(threatScenario.threat_scenario_id)}
                    class="flex items-center gap-2 text-left transition-colors">
                    <svg class="w-4 h-4 transition-transform duration-150 {expandedCards.has(threatScenario.threat_scenario_id) ? 'rotate-90' : ''}"
                      fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                    <h3 class="text-sm font-medium" style="color: var(--color-text-primary);">{threatScenario.name}</h3>
                  </button>
                  {#if threatScenario.description && expandedCards.has(threatScenario.threat_scenario_id)}
                    <p class="text-xs mt-1.5 ml-6" style="color: var(--color-text-tertiary);">{threatScenario.description}</p>
                  {/if}
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-xs" style="color: var(--color-text-tertiary);">
                    {threatAttackPaths.length} path{threatAttackPaths.length !== 1 ? 's' : ''}
                  </span>
                  <button on:click={() => startAddAttackPath(threatScenario.threat_scenario_id)}
                    class="text-xs font-medium" style="color: var(--color-text-link);">+ Add</button>
                </div>
              </div>
            </div>

            {#if expandedCards.has(threatScenario.threat_scenario_id)}
              <div>
                {#if threatAttackPaths.length === 0}
                  <div class="px-5 py-8 text-center">
                    <p class="text-xs" style="color: var(--color-text-tertiary);">No attack paths defined yet</p>
                    <button on:click={() => startAddAttackPath(threatScenario.threat_scenario_id)}
                      class="text-xs font-medium mt-2" style="color: var(--color-text-link);">Create the first attack path</button>
                  </div>
                {:else}
                  {#each threatAttackPaths as attackPath, i}
                    <div class="px-5 py-4" style="border-top: {i > 0 ? '1px solid var(--color-border-subtle)' : 'none'};">
                      <div class="flex items-start justify-between">
                        <div class="flex-1">
                          <div class="flex items-center gap-2 mb-2">
                            <h4 class="text-sm font-medium" style="color: var(--color-text-primary);">{attackPath.name}</h4>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-medium"
                              style="background: {(attackPath.feasibility_rating?.overall_rating || 0) >= 14 ? 'var(--color-risk-low-bg)' : 'var(--color-risk-high-bg)'}; color: {(attackPath.feasibility_rating?.overall_rating || 0) >= 14 ? 'var(--color-risk-low)' : 'var(--color-risk-high)'};">
                              {getAttackPathAFR(attackPath.feasibility_rating?.overall_rating || 0)}
                            </span>
                          </div>
                          {#if attackPath.description}
                            <p class="text-xs mb-3" style="color: var(--color-text-secondary);">{attackPath.description}</p>
                          {/if}
                          <div>
                            <h5 class="text-[11px] font-medium uppercase tracking-wider mb-2" style="color: var(--color-text-tertiary);">Attack Steps</h5>
                            <ol class="text-xs space-y-1" style="color: var(--color-text-secondary);">
                              {#each formatAttackSteps(attackPath.attack_steps) as step, index}
                                <li class="flex items-start">
                                  <span class="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-medium mr-2 mt-0.5"
                                    style="background: var(--color-bg-elevated); color: var(--color-text-tertiary);">{index + 1}</span>
                                  <span>{step}</span>
                                </li>
                              {/each}
                            </ol>
                          </div>
                        </div>
                        <button on:click={() => handleDeleteAttackPath(attackPath)} title="Delete attack path"
                          class="ml-3" style="color: var(--color-error);">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </button>
                      </div>
                    </div>
                  {/each}
                {/if}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<!-- Delete Confirmation Modal -->
{#if showDeleteModal && attackPathToDelete}
  <ConfirmationModal
    bind:isOpen={showDeleteModal}
    title="Delete Attack Path"
    message="Are you sure you want to delete '{attackPathToDelete.name}'? This action cannot be undone."
    confirmText="Delete"
    cancelText="Cancel"
    variant="danger"
    isLoading={isDeleting}
    on:confirm={confirmDelete}
    on:cancel={cancelDelete}
  />
{/if}
