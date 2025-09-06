<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedProduct } from '$lib/stores/productStore';
  import { riskTreatmentApi } from '$lib/api/riskTreatmentApi';
  import type { RiskTreatmentData } from '$lib/api/riskTreatmentApi';
  import { notifications } from '$lib/stores/notificationStore';

  let riskTreatmentData: RiskTreatmentData[] = [];
  let loading = false;
  let expandedCards: Set<string> = new Set();
  
  // Filter states
  let selectedRiskFilter = 'All';
  let selectedStatusFilter = 'All';

  

  // Treatment suggestions based on risk level
  const TREATMENT_SUGGESTIONS = {
    "Critical": "Reducing",
    "High": "Reducing", 
    "Medium": "Sharing",
    "Low": "Retaining"
  };

  // Goal templates
  const GOAL_TEMPLATES = {
    "Reducing": "Ensure {asset} {property} by reducing the risk of {threat_description}.",
    "Retaining": "Ensure {asset} {property} by retaining the risk of {threat_description}.",
    "Sharing": "Ensure {asset} {property} by sharing the risk of {threat_description}.",
    "Avoiding": "Ensure {asset} {property} by avoiding the risk of {threat_description}."
  };

  onMount(async () => {
    if ($selectedProduct?.scope_id) {
      await loadData();
    }
  });

  $: if ($selectedProduct?.scope_id) {
    loadData();
  }

  async function loadData() {
    loading = true;
    try {
      const response = await riskTreatmentApi.getRiskTreatmentData($selectedProduct!.scope_id);
      riskTreatmentData = response.damage_scenarios || [];
      
    } catch (error) {
      console.error('Error loading data:', error);
      notifications.show(
'Failed to load risk treatment data', 'error');
    } finally {
      loading = false;
    }
  }

  function capitalizeFirst(str: string): string {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  }

  function getRiskColor(riskLevel: string): string {
    switch (riskLevel) {
      case 'Critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'High': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  }

  async function saveTreatment(damageScenario: RiskTreatmentData, status: string) {
    try {
      await riskTreatmentApi.updateRiskTreatment(damageScenario.risk_treatment_id, {
        selected_treatment: damageScenario.selected_treatment,
        treatment_goal: damageScenario.treatment_goal,
        treatment_status: status
      });
      
      notifications.show('Risk treatment saved successfully', 'success');
      await loadData(); // Refresh data
    } catch (error) {
      console.error('Error saving treatment:', error);
      notifications.show('Failed to save risk treatment', 'error');
    }
  }

  async function approveTreatment(damageScenario: RiskTreatmentData) {
    if (!damageScenario.treatment_goal?.trim()) {
      notifications.show('Security goal/claim is required before approval', 'error');
      return;
    }

    try {
      // First save the current data
      await riskTreatmentApi.updateRiskTreatment(damageScenario.risk_treatment_id, {
        selected_treatment: damageScenario.selected_treatment,
        treatment_goal: damageScenario.treatment_goal,
        treatment_status: 'approved'
      });
      
      // Then approve
      await riskTreatmentApi.approveRiskTreatment(damageScenario.risk_treatment_id);
      
      notifications.show('Risk treatment approved successfully', 'success');
      await loadData(); // Refresh data
    } catch (error) {
      console.error('Error approving treatment:', error);
      notifications.show('Failed to approve risk treatment', 'error');
    }
  }

  function getSuggestedTreatment(riskLevel: string): string {
    return (TREATMENT_SUGGESTIONS as any)[riskLevel] || "Retaining";
  }

  function toggleCard(scenarioId: string) {
    if (expandedCards.has(scenarioId)) {
      expandedCards.delete(scenarioId);
    } else {
      expandedCards.add(scenarioId);
    }
    expandedCards = expandedCards; // Trigger reactivity
  }

  // Filtered data based on selected filters
  $: filteredRiskTreatmentData = riskTreatmentData.filter(scenario => {
    const riskMatch = selectedRiskFilter === 'All' || scenario.risk_level === selectedRiskFilter;
    const statusMatch = selectedStatusFilter === 'All' || 
      (selectedStatusFilter === 'Draft' && scenario.treatment_status === 'draft') ||
      (selectedStatusFilter === 'Approved' && scenario.treatment_status === 'approved');
    
    return riskMatch && statusMatch;
  });

  function generateGoalTemplate(damageScenario: RiskTreatmentData, treatment: string): string {
    const template = (GOAL_TEMPLATES as any)[treatment] || GOAL_TEMPLATES["Retaining"];
    
    // Get primary affected property
    let property = "security";
    if (damageScenario.confidentiality_impact) {
      property = "confidentiality";
    } else if (damageScenario.integrity_impact) {
      property = "integrity";
    } else if (damageScenario.availability_impact) {
      property = "availability";
    }
    
    return template
      .replace('{asset}', 'system')
      .replace('{property}', property)
      .replace('{threat_description}', damageScenario.description || 'unauthorized access');
  }

  function getAttackPathsForDamage(damageScenarioId: string) {
    // This is now handled by the backend API
    return [];
  }

  function getHighestFeasibilityForDamage(riskData: RiskTreatmentData): number {
    return riskData.highest_feasibility_score || 0;
  }
</script>

<svelte:head>
  <title>Risk Treatment - QuickTARA</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start space-y-4 lg:space-y-0">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Risk Treatment</h1>
      {#if $selectedProduct}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Review calculated risk levels and define treatment strategies for <strong>{$selectedProduct.name}</strong>. 
          Each risk is automatically calculated using the ISO 21434 risk matrix.
        </p>
      {:else}
        <p class="mt-2 text-gray-600 max-w-2xl">
          Please select a product first to begin risk treatment.
        </p>
      {/if}
    </div>
  </div>

  {#if loading}
    <div class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600"></div>
      <span class="ml-3 text-gray-600">Loading risk treatment data...</span>
    </div>
  {:else if !$selectedProduct}
    <div class="text-center py-12">
      <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Product Selected</h3>
      <p class="text-gray-500 mb-4">Select a product from the Product Scope page to begin risk treatment.</p>
      <a href="/products" class="text-slate-600 hover:text-slate-800 font-medium">
        Go to Product Scope →
      </a>
    </div>
  {:else if (riskTreatmentData.length === 0) }
    <div class="text-center py-16">
      <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 0a9 9 0 110-18 9 9 0 010 18z"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Damage Scenarios Found</h3>
      <p class="text-gray-500 mb-4">Create damage scenarios first to perform risk treatment analysis.</p>
      <a href="/damage-scenarios" class="text-slate-600 hover:text-slate-800 font-medium">
        Go to Damage Scenarios →
      </a>
    </div>
  {:else}
    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center gap-4">
        <div class="flex items-center space-x-2">
          <span class="text-sm font-medium text-gray-700">Filters:</span>
        </div>
        
        <div class="flex flex-col sm:flex-row gap-4 flex-1">
          <!-- Risk Level Filter -->
          <div class="flex items-center space-x-2">
            <label for="risk-filter" class="text-sm text-gray-600 whitespace-nowrap">Risk Level:</label>
            <select 
              id="risk-filter"
              bind:value={selectedRiskFilter}
              class="w-32 px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-slate-500 focus:border-transparent"
            >
              <option value="All">All Levels</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <!-- Status Filter -->
          <div class="flex items-center space-x-2">
            <label for="status-filter" class="text-sm text-gray-600 whitespace-nowrap">Status:</label>
            <select 
              id="status-filter"
              bind:value={selectedStatusFilter}
              class="w-28 px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-slate-500 focus:border-transparent"
            >
              <option value="All">All Status</option>
              <option value="Draft">Draft</option>
              <option value="Approved">Approved</option>
            </select>
          </div>
        </div>

        <!-- Results Count -->
        <div class="text-sm text-gray-500 whitespace-nowrap">
          Showing {filteredRiskTreatmentData.length} of {riskTreatmentData.length} treatments
        </div>
      </div>
    </div>

    <!-- Risk Treatment Cards -->
    <div class="space-y-6">
      {#each filteredRiskTreatmentData as damageScenario}
        {@const impactLevel = damageScenario.impact_level}
        {@const feasibilityLevel = damageScenario.feasibility_level || 'Unknown'}
        {@const riskLevel = damageScenario.risk_level || 'Unknown'}
        {@const suggestedTreatment = getSuggestedTreatment(riskLevel)}
        {@const goalTemplate = generateGoalTemplate(damageScenario, suggestedTreatment)}
        
        {@const isExpanded = expandedCards.has(damageScenario.scenario_id)}
        
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden {damageScenario.treatment_status === 'approved' ? 'ring-2 ring-green-200' : ''}">
          <!-- Header - Always Visible -->
          <div 
            class="px-6 py-4 bg-gray-50 border-b border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors" 
            role="button"
            tabindex="0"
            on:click={() => toggleCard(damageScenario.scenario_id)}
            on:keydown={(e) => e.key === 'Enter' || e.key === ' ' ? toggleCard(damageScenario.scenario_id) : null}
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <h3 class="text-lg font-medium text-gray-900">{damageScenario.name}</h3>
                  {#if damageScenario.treatment_status === 'approved'}
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                      ✓ Approved
                    </span>
                  {:else}
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-200">
                      Draft
                    </span>
                  {/if}
                  <!-- Risk Level Badge -->
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {getRiskColor(riskLevel)}">{riskLevel}</span>
                </div>
                
                <!-- Minimized View - Show Goal when collapsed -->
                {#if !isExpanded && damageScenario.treatment_goal}
                  <div class="mt-2 text-sm text-gray-700">
                    <span class="font-medium">Goal:</span> {damageScenario.treatment_goal}
                  </div>
                {:else if !isExpanded}
                  <p class="text-sm text-gray-600 mt-1">{damageScenario.description}</p>
                {/if}
              </div>
              
              <div class="flex items-center space-x-4">
                <!-- Risk Level Info -->
                <div class="text-right text-xs text-gray-500">
                  Impact: {damageScenario.impact_level} | Feasibility: {damageScenario.feasibility_level}
                </div>
                
                <!-- Expand/Collapse Button -->
                <button 
                  class="text-gray-400 hover:text-gray-600 transition-colors"
                  aria-label={isExpanded ? 'Collapse card' : 'Expand card'}
                >
                  <svg class="w-5 h-5 transform transition-transform {isExpanded ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          {#if isExpanded}
            <!-- Risk Calculation -->
            <div class="px-6 py-4 bg-blue-50 border-b border-gray-200">
              <h4 class="text-sm font-medium text-gray-900 mb-3">Risk Calculation (ISO 21434)</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">Impact Level:</span>
                  <span class="ml-2 font-medium {impactLevel === 'Severe' ? 'text-red-700' : impactLevel === 'Major' ? 'text-orange-700' : impactLevel === 'Moderate' ? 'text-yellow-700' : 'text-green-700'}">{impactLevel}</span>
                </div>
                <div>
                  <span class="text-gray-600">Feasibility Level:</span>
                  <span class="ml-2 font-medium {feasibilityLevel === 'Very High' ? 'text-red-700' : feasibilityLevel === 'High' ? 'text-orange-700' : feasibilityLevel === 'Medium' ? 'text-yellow-700' : 'text-green-700'}">{feasibilityLevel}</span>
                </div>
                <div>
                  <span class="text-gray-600">Risk Level:</span>
                  <span class="ml-2 font-medium {riskLevel === 'Critical' ? 'text-red-700' : riskLevel === 'High' ? 'text-orange-700' : riskLevel === 'Medium' ? 'text-yellow-700' : 'text-green-700'}">{riskLevel}</span>
                </div>
              </div>
            </div>

            <!-- Treatment Decision -->
            <div class="px-6 py-4">
              <div class="space-y-4">
                <!-- Treatment Selection -->
                <div>
                  <label for="treatment-select-{damageScenario.scenario_id}" class="block text-sm font-medium text-gray-700 mb-2">
                    Risk Treatment Decision
                  </label>
                  <select 
                    id="treatment-select-{damageScenario.scenario_id}"
                    bind:value={damageScenario.selected_treatment}
                    disabled={damageScenario.treatment_status === 'approved'}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-slate-500 focus:border-transparent {damageScenario.treatment_status === 'approved' ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}"
                  >
                    <option value="Reducing" selected={suggestedTreatment === 'Reducing'}>Reducing</option>
                    <option value="Retaining" selected={suggestedTreatment === 'Retaining'}>Retaining</option>
                    <option value="Sharing" selected={suggestedTreatment === 'Sharing'}>Sharing</option>
                    <option value="Avoiding" selected={suggestedTreatment === 'Avoiding'}>Avoiding</option>
                  </select>
                  <p class="text-xs text-gray-500 mt-1">
                    {#if damageScenario.treatment_status === 'approved'}
                      🔒 Treatment decision is locked (approved)
                    {:else}
                      Auto-suggested: <span class="font-medium">{suggestedTreatment}</span> (based on {riskLevel} risk level)
                    {/if}
                  </p>
                </div>

                <!-- Goal/Claim -->
                <div>
                  <label for="treatment-goal-{damageScenario.scenario_id}" class="block text-sm font-medium text-gray-700 mb-2">
                    Security Goal/Claim <span class="text-red-500">*</span>
                  </label>
                  <textarea 
                    id="treatment-goal-{damageScenario.scenario_id}"
                    bind:value={damageScenario.treatment_goal}
                    disabled={damageScenario.treatment_status === 'approved'}
                    rows="3"
                    placeholder={goalTemplate}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-slate-500 focus:border-transparent placeholder-italic {damageScenario.treatment_status === 'approved' ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}"
                  ></textarea>
                  <p class="text-xs text-gray-500 mt-1">
                    {#if damageScenario.treatment_status === 'approved'}
                      🔒 Security goal is locked (approved)
                    {:else}
                      Review and edit the auto-generated goal above. This field is mandatory before approval.
                    {/if}
                  </p>
                </div>

                <!-- Action Buttons -->
                <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                  {#if damageScenario.treatment_status === 'approved'}
                    <div class="flex items-center text-sm text-green-600">
                      <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                      </svg>
                      Treatment Approved
                    </div>
                  {:else}
                    <button 
                      on:click={() => saveTreatment(damageScenario, 'draft')}
                      class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Save Draft
                    </button>
                    <button 
                      on:click={() => approveTreatment(damageScenario)}
                      class="px-4 py-2 text-sm font-medium text-white bg-slate-600 border border-transparent rounded-md hover:bg-slate-700"
                    >
                      Approve Treatment
                    </button>
                  {/if}
                </div>
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
