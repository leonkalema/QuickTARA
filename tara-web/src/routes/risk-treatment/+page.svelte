<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { selectedProduct } from '$lib/stores/productStore';
  import { riskTreatmentApi } from '$lib/api/riskTreatmentApi';
  import type { RiskTreatmentData } from '$lib/api/riskTreatmentApi';
  import { notifications } from '$lib/stores/notificationStore';
  import { authStore } from '$lib/stores/auth';
  import { canPerformTARA, canManageRisk, isReadOnly } from '$lib/utils/permissions';

  let riskTreatmentData: RiskTreatmentData[] = [];
  let loading = false;
  let expandedCards: Set<string> = new Set();
  let canApprove = false;
  let canManageTreatment = false;
  
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

  // Reactive permission checks - wait for auth to be initialized
  $: if ($authStore.isInitialized) {
    canManageTreatment = canManageRisk() && !isReadOnly();
    
    if ($authStore.isAuthenticated && !canPerformTARA()) {
      goto('/unauthorized');
    }
  }

  onMount(async () => {
    if ($selectedProduct?.scope_id) {
      await loadData();
    }
  });

  // Compute approval capability based on role (risk_manager, org_admin, tool_admin or superuser)
  $: {
    const state: any = $authStore;
    const isSuperuser: boolean = !!state?.user?.is_superuser;
    canApprove = isSuperuser 
      || authStore.hasRole('tool_admin') 
      || authStore.hasRole('org_admin') 
      || authStore.hasRole('risk_manager');
  }

  $: if ($selectedProduct?.scope_id) {
    loadData();
  }

  async function loadData() {
    loading = true;
    try {
      const response = await riskTreatmentApi.getRiskTreatmentData($selectedProduct!.scope_id);
      // Initialize client state using backend-provided suggestions
      const rows = response.damage_scenarios || [];
      riskTreatmentData = rows.map((d) => {
        const suggested = (TREATMENT_SUGGESTIONS as any)[d.risk_level || ''] || 'Retaining';
        return {
          ...d,
          selected_treatment: d.selected_treatment ?? suggested,
          treatment_goal: d.treatment_goal ?? d.suggested_goal
        };
      });
      
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

  function getRiskStyle(riskLevel: string): string {
    switch (riskLevel) {
      case 'Critical': return 'background: var(--color-risk-critical-bg); color: var(--color-risk-critical);';
      case 'High': return 'background: var(--color-risk-high-bg); color: var(--color-risk-high);';
      case 'Medium': return 'background: var(--color-risk-medium-bg); color: var(--color-risk-medium);';
      case 'Low': return 'background: var(--color-risk-low-bg); color: var(--color-risk-low);';
      default: return 'background: var(--color-bg-elevated); color: var(--color-text-tertiary);';
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
      <h1 class="text-xl font-bold" style="color: var(--color-text-primary);">Risk Treatment</h1>
      {#if $selectedProduct}
        <p class="mt-1 text-xs max-w-2xl" style="color: var(--color-text-tertiary);">
          Review risk levels and define treatment strategies for <strong style="color: var(--color-text-secondary);">{$selectedProduct.name}</strong>.
        </p>
      {:else}
        <p class="mt-1 text-xs max-w-2xl" style="color: var(--color-text-tertiary);">
          Select a product to begin risk treatment.
        </p>
      {/if}
    </div>
  </div>

  {#if loading}
    <div class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2" style="border-color: var(--color-accent-primary);"></div>
      <span class="ml-3 text-xs" style="color: var(--color-text-tertiary);">Loading risk treatment data...</span>
    </div>
  {:else if !$selectedProduct}
    <div class="text-center py-12">
      <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
      </svg>
      <h3 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">No Product Selected</h3>
      <p class="text-xs mb-4" style="color: var(--color-text-tertiary);">Select a product to begin risk treatment.</p>
      <a href="/products" class="text-xs font-medium" style="color: var(--color-accent-primary);">
        Go to Product Scope →
      </a>
    </div>
  {:else if (riskTreatmentData.length === 0) }
    <div class="text-center py-16">
      <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 0a9 9 0 110-18 9 9 0 010 18z"></path>
      </svg>
      <h3 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">No Damage Scenarios Found</h3>
      <p class="text-xs mb-4" style="color: var(--color-text-tertiary);">Create damage scenarios first to perform risk treatment analysis.</p>
      <a href="/damage-scenarios" class="text-xs font-medium" style="color: var(--color-accent-primary);">
        Go to Damage Scenarios →
      </a>
    </div>
  {:else}
    <!-- Filters -->
    <div class="rounded-lg p-4 mb-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
      <div class="flex flex-col sm:flex-row sm:items-center gap-4">
        <div class="flex items-center space-x-2">
          <span class="text-xs font-medium" style="color: var(--color-text-secondary);">Filters:</span>
        </div>
        
        <div class="flex flex-col sm:flex-row gap-4 flex-1">
          <!-- Risk Level Filter -->
          <div class="flex items-center space-x-2">
            <label for="risk-filter" class="text-xs whitespace-nowrap" style="color: var(--color-text-tertiary);">Risk Level:</label>
            <select 
              id="risk-filter"
              bind:value={selectedRiskFilter}
              class="w-32 px-2 py-1 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
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
            <label for="status-filter" class="text-xs whitespace-nowrap" style="color: var(--color-text-tertiary);">Status:</label>
            <select 
              id="status-filter"
              bind:value={selectedStatusFilter}
              class="w-28 px-2 py-1 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
            >
              <option value="All">All Status</option>
              <option value="Draft">Draft</option>
              <option value="Approved">Approved</option>
            </select>
          </div>
        </div>

        <!-- Results Count -->
        <div class="text-xs whitespace-nowrap" style="color: var(--color-text-tertiary);">
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
        {@const goalTemplate = damageScenario.suggested_goal || generateGoalTemplate(damageScenario, suggestedTreatment)}
        
        {@const isExpanded = expandedCards.has(damageScenario.scenario_id)}
        
        <div class="rounded-lg overflow-hidden" style="background: var(--color-bg-surface); border: 1px solid {damageScenario.treatment_status === 'approved' ? 'var(--color-success)' : 'var(--color-border-default)'};">
          <!-- Header - Always Visible -->
          <div 
            class="px-5 py-3 cursor-pointer transition-colors" style="background: var(--color-bg-elevated); border-bottom: 1px solid var(--color-border-subtle);" 
            role="button"
            tabindex="0"
            on:click={() => toggleCard(damageScenario.scenario_id)}
            on:keydown={(e) => e.key === 'Enter' || e.key === ' ' ? toggleCard(damageScenario.scenario_id) : null}
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">{damageScenario.name}</h3>
                  {#if damageScenario.treatment_status === 'approved'}
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium" style="background: var(--color-success-bg); color: var(--color-success);">
                      ✓ Approved
                    </span>
                  {:else}
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium" style="background: var(--color-warning-bg); color: var(--color-warning);">
                      Draft
                    </span>
                  {/if}
                  <!-- Risk Level Badge -->
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium" style="{getRiskStyle(riskLevel)}">{riskLevel}</span>
                </div>
                
                <!-- Minimized View - Show Goal when collapsed -->
                {#if !isExpanded && (damageScenario.treatment_goal || damageScenario.suggested_goal)}
                  <div class="mt-1 text-xs" style="color: var(--color-text-secondary);">
                    <span class="font-medium">Goal:</span> {damageScenario.treatment_goal || damageScenario.suggested_goal}
                  </div>
                {:else if !isExpanded}
                  <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">{damageScenario.description}</p>
                {/if}
              </div>
              
              <div class="flex items-center space-x-4">
                <!-- Risk Level Info -->
                <div class="text-right text-[10px]" style="color: var(--color-text-tertiary);">
                  Impact: {damageScenario.impact_level} | Feasibility: {damageScenario.feasibility_level}
                </div>
                
                <!-- Expand/Collapse Button -->
                <button 
                  class="transition-colors" style="color: var(--color-text-tertiary);"
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
            <div class="px-5 py-3" style="background: var(--color-bg-inset); border-bottom: 1px solid var(--color-border-subtle);">
              <h4 class="text-xs font-semibold mb-2" style="color: var(--color-text-secondary);">Risk Calculation (ISO 21434)</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span class="text-xs" style="color: var(--color-text-tertiary);">Impact:</span>
                  <span class="ml-2 font-medium {impactLevel === 'Severe' ? 'text-red-700' : impactLevel === 'Major' ? 'text-orange-700' : impactLevel === 'Moderate' ? 'text-yellow-700' : 'text-green-700'}">{impactLevel}</span>
                </div>
                <div>
                  <span class="text-xs" style="color: var(--color-text-tertiary);">Feasibility:</span>
                  <span class="ml-2 font-medium {feasibilityLevel === 'Very High' ? 'text-red-700' : feasibilityLevel === 'High' ? 'text-orange-700' : feasibilityLevel === 'Medium' ? 'text-yellow-700' : 'text-green-700'}">{feasibilityLevel}</span>
                </div>
                <div>
                  <span class="text-xs" style="color: var(--color-text-tertiary);">Risk:</span>
                  <span class="ml-2 font-medium {riskLevel === 'Critical' ? 'text-red-700' : riskLevel === 'High' ? 'text-orange-700' : riskLevel === 'Medium' ? 'text-yellow-700' : 'text-green-700'}">{riskLevel}</span>
                </div>
              </div>
            </div>

            <!-- Treatment Decision -->
            <div class="px-5 py-4">
              <div class="space-y-4">
                <!-- Treatment Selection -->
                <div>
                  <label for="treatment-select-{damageScenario.scenario_id}" class="block text-xs font-medium mb-2" style="color: var(--color-text-secondary);">
                    Risk Treatment Decision
                  </label>
                  <select 
                    id="treatment-select-{damageScenario.scenario_id}"
                    bind:value={damageScenario.selected_treatment}
                    disabled={damageScenario.treatment_status === 'approved' || !canManageTreatment}
                    class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default); {damageScenario.treatment_status === 'approved' || !canManageTreatment ? 'opacity: 0.6; cursor: not-allowed;' : ''}"
                  >
                    <option value="Reducing" selected={suggestedTreatment === 'Reducing'}>Reducing</option>
                    <option value="Retaining" selected={suggestedTreatment === 'Retaining'}>Retaining</option>
                    <option value="Sharing" selected={suggestedTreatment === 'Sharing'}>Sharing</option>
                    <option value="Avoiding" selected={suggestedTreatment === 'Avoiding'}>Avoiding</option>
                  </select>
                  <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">
                    {#if damageScenario.treatment_status === 'approved'}
                      🔒 Treatment decision is locked (approved)
                    {:else if !canManageTreatment}
                      👁️ View-only mode - treatment modifications restricted
                    {:else}
                      Auto-suggested: <span class="font-medium">{suggestedTreatment}</span> (based on {riskLevel} risk level)
                    {/if}
                  </p>
                </div>

                <!-- Goal/Claim -->
                <div>
                  <label for="treatment-goal-{damageScenario.scenario_id}" class="block text-xs font-medium mb-2" style="color: var(--color-text-secondary);">
                    Security Goal/Claim <span class="text-red-500">*</span>
                  </label>
                  <textarea 
                    id="treatment-goal-{damageScenario.scenario_id}"
                    bind:value={damageScenario.treatment_goal}
                    disabled={damageScenario.treatment_status === 'approved' || !canManageTreatment}
                    rows="3"
                    placeholder={damageScenario.suggested_goal || goalTemplate}
                    class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default); {damageScenario.treatment_status === 'approved' || !canManageTreatment ? 'opacity: 0.6; cursor: not-allowed;' : ''}"
                  ></textarea>
                  <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">
                    {#if damageScenario.treatment_status === 'approved'}
                      🔒 Security goal is locked (approved)
                    {:else if !canManageTreatment}
                      👁️ View-only mode - goal modifications restricted
                    {:else}
                      Review and edit the auto-generated goal above. This field is mandatory before approval.
                    {/if}
                  </p>
                </div>

                <!-- Action Buttons -->
                <div class="flex justify-end space-x-3 pt-3" style="border-top: 1px solid var(--color-border-subtle);">
                  {#if damageScenario.treatment_status === 'approved'}
                    <div class="flex items-center text-xs" style="color: var(--color-success);">
                      <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                      </svg>
                      Treatment Approved
                    </div>
                  {:else if canManageTreatment}
                    <button 
                      on:click={() => saveTreatment(damageScenario, 'draft')}
                      class="px-3 py-1.5 text-xs font-medium rounded-md" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
                    >
                      Save Draft
                    </button>
                    {#if canApprove}
                      <button 
                        on:click={() => approveTreatment(damageScenario)}
                        class="px-3 py-1.5 text-xs font-medium rounded-md" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
                      >
                        Approve Treatment
                      </button>
                    {/if}
                  {:else}
                    <div class="flex items-center text-xs" style="color: var(--color-text-tertiary);">
                      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                      </svg>
                      View-only mode
                    </div>
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
