<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedProduct } from '$lib/stores/productStore';
  import { notifications } from '$lib/stores/notificationStore';
  import { threatScenarioApi } from '$lib/api/threatScenarioApi';
  import { attackPathApi } from '$lib/api/attackPathApi';
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
    const matchesSearch = scenario.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         scenario.description?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  $: filteredAttackPaths = attackPaths.filter(path => {
    if (!selectedThreatScenario) return true;
    return path.threat_scenario_id === selectedThreatScenario;
  });

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
</script>

<svelte:head>
  <title>Risk Assessment - QuickTARA</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start space-y-4 lg:space-y-0">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Risk Assessment</h1>
      {#if $selectedProduct}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Create attack paths and assess feasibility for threat scenarios in <strong>{$selectedProduct.name}</strong>. 
          Define step-by-step attack sequences and rate their feasibility.
        </p>
      {:else}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Please select a product first to begin risk assessment.
        </p>
      {/if}
    </div>
    {#if $selectedProduct && threatScenarios.length > 0 && !loading}
      <button
        class="bg-slate-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-700 transition-colors flex items-center space-x-2 self-start"
        on:click={() => startAddAttackPath()}
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        <span>New Attack Path</span>
      </button>
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
        Select a product from the header dropdown or visit the Products page to begin risk assessment.
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
  {:else if threatScenarios.length === 0 && !loading}
    <!-- No Threat Scenarios State -->
    <div class="text-center py-16">
      <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Threat Scenarios Found</h3>
      <p class="text-gray-500 mb-6 max-w-md mx-auto">
        You need to create threat scenarios first before you can assess attack paths and feasibility.
      </p>
      <a
        href="/threat-scenarios"
        class="bg-slate-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-slate-700 transition-colors inline-flex items-center space-x-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z"></path>
        </svg>
        <span>Create Threat Scenarios</span>
      </a>
    </div>
  {:else}
    <!-- Content -->
    {#if loading}
      <div class="flex flex-col justify-center items-center py-16">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600 mb-4"></div>
        <p class="text-gray-500">Loading risk assessment data...</p>
      </div>
    {:else}
      <!-- Filters -->
      <div class="bg-white p-4 rounded-lg border border-gray-200">
        <div class="flex flex-wrap gap-4 items-center">
          <div class="flex-1 min-w-64">
            <input
              bind:value={searchTerm}
              placeholder="Search threat scenarios..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent"
            />
          </div>
          
          <div class="min-w-48">
            <select bind:value={selectedThreatScenario} class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent">
              <option value="">All threat scenarios</option>
              {#each threatScenarios as scenario}
                <option value={scenario.threat_scenario_id}>{scenario.name}</option>
              {/each}
            </select>
          </div>

          {#if searchTerm || selectedThreatScenario}
            <button
              on:click={() => { searchTerm = ''; selectedThreatScenario = ''; }}
              class="text-slate-600 hover:text-slate-800 px-3 py-2 text-sm font-medium transition-colors"
            >
              Clear filters
            </button>
          {/if}
        </div>
      </div>

      <!-- Add Attack Path Form -->
      {#if showAddForm}
        <div class="bg-white border border-gray-200 rounded-lg p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-medium text-gray-900">Create New Attack Path</h3>
            <button
              on:click={() => showAddForm = false}
              class="text-gray-400 hover:text-gray-500"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Left Column: Basic Info -->
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Threat Scenario *
                </label>
                <select
                  bind:value={formData.threat_scenario_id}
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-slate-500 focus:border-slate-500"
                  required
                >
                  <option value="">Select a threat scenario</option>
                  {#each threatScenarios as scenario}
                    <option value={scenario.threat_scenario_id}>{scenario.name}</option>
                  {/each}
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Attack Path Name *
                </label>
                <input
                  type="text"
                  bind:value={formData.name}
                  placeholder="e.g., Remote Code Execution via Buffer Overflow"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-slate-500 focus:border-slate-500"
                  required
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  bind:value={formData.description}
                  placeholder="Brief description of this attack path..."
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-slate-500 focus:border-slate-500"
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Attack Steps *
                </label>
                <textarea
                  bind:value={formData.attack_steps}
                  placeholder="Enter each attack step on a new line:&#10;1. Reconnaissance and target identification&#10;2. Vulnerability scanning&#10;3. Exploit development&#10;4. Initial access&#10;5. Privilege escalation&#10;..."
                  rows="8"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-slate-500 focus:border-slate-500 font-mono text-sm"
                  required
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">Enter each step on a separate line. Be as detailed as possible.</p>
              </div>
            </div>

            <!-- Right Column: Feasibility Rating -->
            <div>
              <h4 class="text-sm font-medium text-gray-700 mb-4">Feasibility Assessment</h4>
              <FeasibilityRatingSelector bind:feasibilityRating={formData.feasibility_rating} />
            </div>
          </div>

          <div class="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
            <button
              type="button"
              on:click={() => showAddForm = false}
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="button"
              on:click={handleSubmit}
              class="px-4 py-2 text-sm font-medium text-white bg-slate-600 border border-transparent rounded-md hover:bg-slate-700"
            >
              Create Attack Path
            </button>
          </div>
        </div>
      {/if}

      <!-- Threat Scenarios with Attack Paths -->
      <div class="space-y-6">
        {#each filteredThreatScenarios as threatScenario}
          {@const threatAttackPaths = getAttackPathsForThreat(threatScenario.threat_scenario_id)}
          <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <!-- Threat Scenario Header -->
            <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-lg font-medium text-gray-900">{threatScenario.name}</h3>
                  {#if threatScenario.description}
                    <p class="text-sm text-gray-600 mt-1">{threatScenario.description}</p>
                  {/if}
                </div>
                <div class="flex items-center space-x-3">
                  <span class="text-sm text-gray-500">
                    {threatAttackPaths.length} attack path{threatAttackPaths.length !== 1 ? 's' : ''}
                  </span>
                  <button
                    on:click={() => startAddAttackPath(threatScenario.threat_scenario_id)}
                    class="text-slate-600 hover:text-slate-800 text-sm font-medium"
                  >
                    + Add Attack Path
                  </button>
                </div>
              </div>
            </div>

            <!-- Attack Paths -->
            <div class="divide-y divide-gray-200">
              {#if threatAttackPaths.length === 0}
                <div class="px-6 py-8 text-center">
                  <svg class="w-8 h-8 mx-auto text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <p class="text-sm text-gray-500">No attack paths defined yet</p>
                  <button
                    on:click={() => startAddAttackPath(threatScenario.threat_scenario_id)}
                    class="text-slate-600 hover:text-slate-800 text-sm font-medium mt-2"
                  >
                    Create the first attack path
                  </button>
                </div>
              {:else}
                {#each threatAttackPaths as attackPath}
                  <div class="px-6 py-4">
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <div class="flex items-center space-x-3 mb-2">
                          <h4 class="text-md font-medium text-gray-900">{attackPath.name}</h4>
                          <div class="flex items-center space-x-2">
                            <span class="text-xs text-gray-500">Feasibility:</span>
                            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium {attackPath.feasibility_rating.overall_rating <= 1.5 ? 'bg-green-100 text-green-800' : attackPath.feasibility_rating.overall_rating <= 2.5 ? 'bg-yellow-100 text-yellow-800' : attackPath.feasibility_rating.overall_rating <= 3.5 ? 'bg-orange-100 text-orange-800' : 'bg-red-100 text-red-800'}">
                              {attackPath.feasibility_rating.overall_rating}/4.0
                            </span>
                          </div>
                        </div>
                        
                        {#if attackPath.description}
                          <p class="text-sm text-gray-600 mb-3">{attackPath.description}</p>
                        {/if}
                        
                        <div>
                          <h5 class="text-sm font-medium text-gray-700 mb-2">Attack Steps:</h5>
                          <ol class="text-sm text-gray-600 space-y-1">
                            {#each formatAttackSteps(attackPath.attack_steps) as step, index}
                              <li class="flex items-start">
                                <span class="flex-shrink-0 w-6 h-6 bg-slate-100 text-slate-700 rounded-full flex items-center justify-center text-xs font-medium mr-2 mt-0.5">
                                  {index + 1}
                                </span>
                                <span>{step}</span>
                              </li>
                            {/each}
                          </ol>
                        </div>
                      </div>
                      
                      <button
                        on:click={() => handleDeleteAttackPath(attackPath)}
                        class="text-red-600 hover:text-red-800 ml-4"
                        title="Delete attack path"
                      >
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                {/each}
              {/if}
            </div>
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
