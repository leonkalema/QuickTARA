<script lang="ts">
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

  function getRiskColor(level: string): string {
    switch (level) {
      case 'Critical':
      case 'Severe':
      case 'Very High': return 'var(--color-risk-critical)';
      case 'High':
      case 'Major': return 'var(--color-risk-high)';
      case 'Medium':
      case 'Moderate': return 'var(--color-risk-medium)';
      case 'Low':
      case 'Negligible': return 'var(--color-risk-low)';
      default: return 'var(--color-text-tertiary)';
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

  $: filteredRiskTreatmentData = riskTreatmentData.filter(scenario => {
    const riskMatch = selectedRiskFilter === 'All' || scenario.risk_level === selectedRiskFilter;
    const statusMatch = selectedStatusFilter === 'All' ||
      (selectedStatusFilter === 'Draft' && scenario.treatment_status === 'draft') ||
      (selectedStatusFilter === 'Approved' && scenario.treatment_status === 'approved');
    return riskMatch && statusMatch;
  });

  $: summaryStats = {
    total: riskTreatmentData.length,
    approved: riskTreatmentData.filter(d => d.treatment_status === 'approved').length,
    draft: riskTreatmentData.filter(d => d.treatment_status !== 'approved').length,
    critical: riskTreatmentData.filter(d => d.risk_level === 'Critical').length,
    high: riskTreatmentData.filter(d => d.risk_level === 'High').length,
  };

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
    <div class="rounded-xl border border-dashed py-20 text-center" style="border-color: var(--color-border-default);">
      <div class="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4" style="background: var(--color-bg-elevated);">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
      </div>
      <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No product selected</h3>
      <p class="text-sm mb-6 max-w-sm mx-auto" style="color: var(--color-text-tertiary);">Select a product from the header dropdown to manage its risk treatment decisions.</p>
      <a href="/products" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Go to Products</a>
    </div>
  {:else if (riskTreatmentData.length === 0)}
    <div class="rounded-xl border border-dashed py-20 text-center" style="border-color: var(--color-border-default);">
      <div class="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4" style="background: var(--color-bg-elevated);">
        <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
      </div>
      <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No risk data yet</h3>
      <p class="text-sm mb-6 max-w-sm mx-auto" style="color: var(--color-text-tertiary);">Complete the workflow first — add damage scenarios, threat scenarios, and run risk assessment. Treatment options will appear here.</p>
      <a href="/damage-scenarios" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">Start with Damage Scenarios</a>
    </div>
  {:else}
    <!-- Summary stats bar -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {#each [
        { label: 'Total', value: summaryStats.total, color: 'var(--color-text-primary)', bg: 'var(--color-bg-surface)' },
        { label: 'Approved', value: summaryStats.approved, color: 'var(--color-status-success)', bg: 'rgba(34,197,94,0.07)' },
        { label: 'Draft', value: summaryStats.draft, color: '#fbbf24', bg: 'rgba(251,191,36,0.07)' },
        { label: 'Critical / High', value: `${summaryStats.critical} / ${summaryStats.high}`, color: 'var(--color-risk-critical)', bg: 'rgba(239,68,68,0.07)' },
      ] as s}
        <div class="rounded-xl px-4 py-3 flex flex-col gap-0.5" style="background: {s.bg}; border: 1px solid var(--color-border-default);">
          <span class="text-[11px] uppercase tracking-wide font-medium" style="color: var(--color-text-tertiary);">{s.label}</span>
          <span class="text-xl font-bold" style="color: {s.color};">{s.value}</span>
        </div>
      {/each}
    </div>

    <!-- Filter toolbar -->
    <div class="flex flex-wrap items-center gap-3">
      <span class="text-xs font-medium" style="color: var(--color-text-tertiary);">Filter:</span>
      <div class="flex items-center gap-2">
        <label for="risk-filter" class="text-xs" style="color: var(--color-text-tertiary);">Risk</label>
        <select id="risk-filter" bind:value={selectedRiskFilter}
          class="px-2 py-1.5 text-xs rounded-lg"
          style="background: var(--color-bg-surface); color: var(--color-text-primary); border: 1px solid var(--color-border-default);">
          <option value="All">All levels</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label for="status-filter" class="text-xs" style="color: var(--color-text-tertiary);">Status</label>
        <select id="status-filter" bind:value={selectedStatusFilter}
          class="px-2 py-1.5 text-xs rounded-lg"
          style="background: var(--color-bg-surface); color: var(--color-text-primary); border: 1px solid var(--color-border-default);">
          <option value="All">All statuses</option>
          <option value="Draft">Draft</option>
          <option value="Approved">Approved</option>
        </select>
      </div>
      <span class="ml-auto text-xs" style="color: var(--color-text-tertiary);">
        {filteredRiskTreatmentData.length} of {riskTreatmentData.length} shown
      </span>
    </div>

    <!-- Risk Treatment Cards -->
    <div class="space-y-3">
      {#each filteredRiskTreatmentData as damageScenario}
        {@const impactLevel = damageScenario.impact_level}
        {@const feasibilityLevel = damageScenario.feasibility_level || 'Unknown'}
        {@const riskLevel = damageScenario.risk_level || 'Unknown'}
        {@const suggestedTreatment = getSuggestedTreatment(riskLevel)}
        {@const goalTemplate = damageScenario.suggested_goal || generateGoalTemplate(damageScenario, suggestedTreatment)}
        
        {@const isExpanded = expandedCards.has(damageScenario.scenario_id)}
        
        {@const isApproved = damageScenario.treatment_status === 'approved'}
        <div class="flex rounded-xl overflow-hidden border"
          style="background: var(--color-bg-surface); border-color: {isApproved ? 'var(--color-status-success)' : 'var(--color-border-default)'};">
          <!-- Left risk stripe -->
          <div class="w-1 flex-shrink-0" style="background: {getRiskColor(riskLevel)};"></div>

          <div class="flex-1 min-w-0">
            <!-- Card header -->
            <div
              class="px-5 py-4 cursor-pointer"
              role="button"
              tabindex="0"
              on:click={() => toggleCard(damageScenario.scenario_id)}
              on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && toggleCard(damageScenario.scenario_id)}
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 flex-wrap mb-1">
                    <h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">{damageScenario.name}</h3>
                    <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold" style="{getRiskStyle(riskLevel)}">{riskLevel}</span>
                    {#if isApproved}
                      <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold" style="background: rgba(52,211,153,0.12); color: var(--color-status-success);">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                        Approved
                      </span>
                    {:else}
                      <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold" style="background: rgba(251,191,36,0.12); color: #fbbf24;">Draft</span>
                    {/if}
                  </div>
                  {#if !isExpanded}
                    {#if damageScenario.treatment_goal || damageScenario.suggested_goal}
                      <p class="text-xs truncate" style="color: var(--color-text-secondary);">
                        <span class="font-medium">Goal:</span> {damageScenario.treatment_goal || damageScenario.suggested_goal}
                      </p>
                    {:else}
                      <p class="text-xs truncate" style="color: var(--color-text-tertiary);">{damageScenario.description}</p>
                    {/if}
                  {/if}
                </div>

                <div class="flex items-center gap-4 flex-shrink-0">
                  <!-- Impact / Feasibility pills -->
                  <div class="hidden sm:flex items-center gap-2">
                    <span class="text-[10px] px-2 py-0.5 rounded" style="background: var(--color-bg-elevated); color: var(--color-text-tertiary);">
                      Impact: <span style="color: {getRiskColor(impactLevel ?? '')}; font-weight: 600;">{impactLevel ?? '—'}</span>
                    </span>
                    <span class="text-[10px] px-2 py-0.5 rounded" style="background: var(--color-bg-elevated); color: var(--color-text-tertiary);">
                      Feasibility: <span style="color: {getRiskColor(feasibilityLevel)}; font-weight: 600;">{feasibilityLevel}</span>
                    </span>
                  </div>
                  <svg class="w-4 h-4 transition-transform duration-200 {isExpanded ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                  </svg>
                </div>
              </div>
            </div>

            {#if isExpanded}
              <!-- Risk breakdown row -->
              <div class="mx-5 mb-4 rounded-lg grid grid-cols-3 divide-x overflow-hidden"
                style="border: 1px solid var(--color-border-default); divide-color: var(--color-border-default);">
                {#each [
                  { label: 'Impact', value: impactLevel ?? '—' },
                  { label: 'Feasibility', value: feasibilityLevel },
                  { label: 'Risk', value: riskLevel }
                ] as cell}
                  <div class="px-4 py-3 text-center" style="background: var(--color-bg-elevated);">
                    <p class="text-[10px] uppercase tracking-wide mb-1" style="color: var(--color-text-tertiary);">{cell.label}</p>
                    <p class="text-sm font-bold" style="color: {getRiskColor(cell.value)};">{cell.value}</p>
                  </div>
                {/each}
              </div>

              <!-- Treatment decision -->
              <div class="px-5 pb-5 space-y-4">
                <div>
                  <label for="treatment-select-{damageScenario.scenario_id}" class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">
                    Treatment Decision
                  </label>
                  <select
                    id="treatment-select-{damageScenario.scenario_id}"
                    bind:value={damageScenario.selected_treatment}
                    disabled={isApproved || !canManageTreatment}
                    class="w-full px-3 py-2 text-xs rounded-lg"
                    style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default); opacity: {isApproved || !canManageTreatment ? '0.6' : '1'};"
                  >
                    <option value="Reducing">Reducing</option>
                    <option value="Retaining">Retaining</option>
                    <option value="Sharing">Sharing</option>
                    <option value="Avoiding">Avoiding</option>
                  </select>
                  {#if !isApproved && canManageTreatment}
                    <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">
                      Suggested: <span class="font-semibold" style="color: var(--color-text-secondary);">{suggestedTreatment}</span> based on {riskLevel} risk
                    </p>
                  {/if}
                </div>

                <div>
                  <label for="treatment-goal-{damageScenario.scenario_id}" class="block text-xs font-medium mb-1.5" style="color: var(--color-text-secondary);">
                    Security Goal / Claim <span style="color: var(--color-status-error);">*</span>
                  </label>
                  <textarea
                    id="treatment-goal-{damageScenario.scenario_id}"
                    bind:value={damageScenario.treatment_goal}
                    disabled={isApproved || !canManageTreatment}
                    rows="3"
                    placeholder={damageScenario.suggested_goal || goalTemplate}
                    class="w-full px-3 py-2 text-xs rounded-lg resize-none"
                    style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default); opacity: {isApproved || !canManageTreatment ? '0.6' : '1'};"
                  ></textarea>
                  {#if !isApproved && canManageTreatment}
                    <p class="text-[10px] mt-1" style="color: var(--color-text-tertiary);">
                      Review and edit the auto-generated goal. Required before approval.
                    </p>
                  {:else if isApproved}
                    <p class="text-[10px] mt-1 flex items-center gap-1" style="color: var(--color-status-success);">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                      Locked — treatment approved
                    </p>
                  {:else}
                    <p class="text-[10px] mt-1 flex items-center gap-1" style="color: var(--color-text-tertiary);">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                      View only
                    </p>
                  {/if}
                </div>

                <!-- Actions -->
                <div class="flex items-center justify-end gap-2 pt-3" style="border-top: 1px solid var(--color-border-subtle);">
                  {#if isApproved}
                    <span class="inline-flex items-center gap-1.5 text-xs font-medium" style="color: var(--color-status-success);">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                      Treatment approved
                    </span>
                  {:else if canManageTreatment}
                    <button
                      on:click={() => saveTreatment(damageScenario, 'draft')}
                      class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors"
                      style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
                    >
                      Save Draft
                    </button>
                    {#if canApprove}
                      <button
                        on:click={() => approveTreatment(damageScenario)}
                        class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors"
                        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
                      >
                        Approve Treatment
                      </button>
                    {/if}
                  {:else}
                    <span class="inline-flex items-center gap-1.5 text-xs" style="color: var(--color-text-tertiary);">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                      View only
                    </span>
                  {/if}
                </div>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
