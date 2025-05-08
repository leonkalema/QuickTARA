<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { X, AlertTriangle, Save, RefreshCw } from '@lucide/svelte';
  import { impactRatingApi, SeverityLevel, type ImpactRatingExplanation } from '../../api/impact-ratings';
  import type { DamageScenario } from '../../api/damage-scenarios';
  import { safeApiCall } from '../../utils/error-handler';
  import { showSuccess, showError } from '../ToastManager.svelte';
  import RadarChart from './RadarChart.svelte';
  
  export let scenario: DamageScenario;
  
  const dispatch = createEventDispatcher();
  
  let isLoading = false;
  let isSaving = false;
  let error = '';
  let explanations: ImpactRatingExplanation | null = null;
  
  // Form data
  let safetyImpact = scenario.safety_impact || null;
  let financialImpact = scenario.financial_impact || null;
  let operationalImpact = scenario.operational_impact || null;
  let privacyImpact = scenario.privacy_impact || null;
  let impactRatingNotes = scenario.impact_rating_notes || '';
  let overrideReason = '';
  
  let originalValues = {
    safetyImpact: scenario.safety_impact,
    financialImpact: scenario.financial_impact,
    operationalImpact: scenario.operational_impact,
    privacyImpact: scenario.privacy_impact
  };
  
  let valuesChanged = false;
  
  onMount(async () => {
    // If we have auto-generated ratings, fetch the explanations
    if (scenario.sfop_rating_auto_generated) {
      await loadExplanations();
    }
  });
  
  async function loadExplanations() {
    isLoading = true;
    error = '';
    
    try {
      // Get suggested ratings to see explanations
      const result = await safeApiCall(() => impactRatingApi.getSuggestedRatings({
        component_id: scenario.primary_component_id,
        damage_category: scenario.damage_category,
        confidentiality_impact: scenario.confidentiality_impact,
        integrity_impact: scenario.integrity_impact,
        availability_impact: scenario.availability_impact
      }));
      
      if (result) {
        explanations = result.explanations;
      }
    } catch (err) {
      console.error('Error loading explanations:', err);
      error = 'Failed to load rating explanations.';
    } finally {
      isLoading = false;
    }
  }
  
  function checkForChanges() {
    valuesChanged = 
      safetyImpact !== originalValues.safetyImpact ||
      financialImpact !== originalValues.financialImpact ||
      operationalImpact !== originalValues.operationalImpact ||
      privacyImpact !== originalValues.privacyImpact;
  }
  
  async function handleSave() {
    if (scenario.sfop_rating_auto_generated && valuesChanged && !overrideReason) {
      showError('You must provide an override reason when changing auto-generated ratings.');
      return;
    }
    
    isSaving = true;
    error = '';
    
    try {
      const updateData: ImpactRatingUpdate = {
        safety_impact: safetyImpact as SeverityLevel | undefined,
        financial_impact: financialImpact as SeverityLevel | undefined,
        operational_impact: operationalImpact as SeverityLevel | undefined,
        privacy_impact: privacyImpact as SeverityLevel | undefined,
        impact_rating_notes: impactRatingNotes || undefined,
        sfop_rating_override_reason: overrideReason || undefined
      };
      
      const updated = await safeApiCall(() => 
        impactRatingApi.updateScenarioRatings(scenario.scenario_id, updateData)
      );
      
      if (updated) {
        showSuccess('Impact ratings updated successfully');
        dispatch('close');
      }
    } catch (err) {
      console.error('Error updating impact ratings:', err);
      error = 'Failed to update impact ratings. Please try again.';
    } finally {
      isSaving = false;
    }
  }
  
  function handleClose() {
    dispatch('close');
  }
  
  function getSeverityOptions() {
    return [
      { value: null, label: 'None' },
      { value: SeverityLevel.LOW, label: 'Low' },
      { value: SeverityLevel.MEDIUM, label: 'Medium' },
      { value: SeverityLevel.HIGH, label: 'High' },
      { value: SeverityLevel.CRITICAL, label: 'Critical' }
    ];
  }
  
  function getImpactColor(level: string | null): string {
    switch(level) {
      case 'Critical':
        return 'text-red-700 border-red-300 bg-red-50';
      case 'High':
        return 'text-orange-700 border-orange-300 bg-orange-50';
      case 'Medium':
        return 'text-yellow-700 border-yellow-300 bg-yellow-50';
      case 'Low':
        return 'text-green-700 border-green-300 bg-green-50';
      default:
        return 'text-gray-700 border-gray-300 bg-gray-50';
    }
  }
  
  $: {
    // Watch for changes to update valuesChanged flag
    safetyImpact;
    financialImpact;
    operationalImpact;
    privacyImpact;
    checkForChanges();
  }
  
  $: radarData = {
    labels: ['Safety', 'Financial', 'Operational', 'Privacy'],
    values: [
      safetyImpact === 'Critical' ? 4 : safetyImpact === 'High' ? 3 : safetyImpact === 'Medium' ? 2 : safetyImpact === 'Low' ? 1 : 0,
      financialImpact === 'Critical' ? 4 : financialImpact === 'High' ? 3 : financialImpact === 'Medium' ? 2 : financialImpact === 'Low' ? 1 : 0,
      operationalImpact === 'Critical' ? 4 : operationalImpact === 'High' ? 3 : operationalImpact === 'Medium' ? 2 : operationalImpact === 'Low' ? 1 : 0,
      privacyImpact === 'Critical' ? 4 : privacyImpact === 'High' ? 3 : privacyImpact === 'Medium' ? 2 : privacyImpact === 'Low' ? 1 : 0
    ]
  };
</script>

<div class="bg-white rounded-lg shadow-xl overflow-hidden">
  <div class="p-5 border-b border-gray-200 flex justify-between items-center">
    <h3 class="text-lg font-semibold text-gray-900">Edit Impact Ratings</h3>
    <button 
      on:click={handleClose}
      class="text-gray-400 hover:text-gray-500"
    >
      <X size={20} />
    </button>
  </div>
  
  <div class="p-5">
    <!-- Scenario Info -->
    <div class="mb-6">
      <h4 class="text-base font-medium text-gray-900 mb-2">{scenario.name}</h4>
      <p class="text-sm text-gray-500">{scenario.description}</p>
      
      <div class="mt-4 grid grid-cols-2 gap-4">
        <div>
          <p class="text-sm font-medium text-gray-500">Damage Category</p>
          <p class="text-sm">{scenario.damage_category}</p>
        </div>
        <div>
          <p class="text-sm font-medium text-gray-500">Impact Type</p>
          <p class="text-sm">{scenario.impact_type}</p>
        </div>
      </div>
    </div>
    
    <!-- Auto-generated Warning -->
    {#if scenario.sfop_rating_auto_generated && valuesChanged}
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <AlertTriangle class="h-5 w-5 text-yellow-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-yellow-700">
              You are changing auto-generated ratings. Please provide an override reason below.
            </p>
          </div>
        </div>
      </div>
    {/if}
    
    <!-- Error Message -->
    {#if error}
      <div class="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
        <div class="flex">
          <div class="flex-shrink-0">
            <AlertTriangle class="h-5 w-5 text-red-400" />
          </div>
          <div class="ml-3">
            <p class="text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    {/if}
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Rating Form -->
      <div>
        <h5 class="text-base font-medium text-gray-900 mb-4">SFOP Impact Ratings</h5>
        
        <!-- Safety Impact -->
        <div class="mb-4">
          <label for="safetyImpact" class="block text-sm font-medium text-gray-700 mb-1">
            Safety Impact
          </label>
          <select 
            id="safetyImpact"
            bind:value={safetyImpact}
            class={`block w-full rounded-md border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${getImpactColor(safetyImpact)}`}
          >
            {#each getSeverityOptions() as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
          {#if explanations && explanations.safety_impact}
            <p class="mt-1 text-xs text-gray-500">{explanations.safety_impact}</p>
          {/if}
        </div>
        
        <!-- Financial Impact -->
        <div class="mb-4">
          <label for="financialImpact" class="block text-sm font-medium text-gray-700 mb-1">
            Financial Impact
          </label>
          <select 
            id="financialImpact"
            bind:value={financialImpact}
            class={`block w-full rounded-md border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${getImpactColor(financialImpact)}`}
          >
            {#each getSeverityOptions() as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
          {#if explanations && explanations.financial_impact}
            <p class="mt-1 text-xs text-gray-500">{explanations.financial_impact}</p>
          {/if}
        </div>
        
        <!-- Operational Impact -->
        <div class="mb-4">
          <label for="operationalImpact" class="block text-sm font-medium text-gray-700 mb-1">
            Operational Impact
          </label>
          <select 
            id="operationalImpact"
            bind:value={operationalImpact}
            class={`block w-full rounded-md border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${getImpactColor(operationalImpact)}`}
          >
            {#each getSeverityOptions() as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
          {#if explanations && explanations.operational_impact}
            <p class="mt-1 text-xs text-gray-500">{explanations.operational_impact}</p>
          {/if}
        </div>
        
        <!-- Privacy Impact -->
        <div class="mb-4">
          <label for="privacyImpact" class="block text-sm font-medium text-gray-700 mb-1">
            Privacy Impact
          </label>
          <select 
            id="privacyImpact"
            bind:value={privacyImpact}
            class={`block w-full rounded-md border shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${getImpactColor(privacyImpact)}`}
          >
            {#each getSeverityOptions() as option}
              <option value={option.value}>{option.label}</option>
            {/each}
          </select>
          {#if explanations && explanations.privacy_impact}
            <p class="mt-1 text-xs text-gray-500">{explanations.privacy_impact}</p>
          {/if}
        </div>
        
        <!-- Notes -->
        <div class="mb-4">
          <label for="notes" class="block text-sm font-medium text-gray-700 mb-1">
            Impact Rating Notes
          </label>
          <textarea 
            id="notes"
            bind:value={impactRatingNotes}
            rows="3"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="Additional notes about these impact ratings..."
          ></textarea>
        </div>
        
        <!-- Override Reason (only shown when changing auto-generated ratings) -->
        {#if scenario.sfop_rating_auto_generated && valuesChanged}
          <div class="mb-4">
            <label for="overrideReason" class="block text-sm font-medium text-gray-700 mb-1">
              Override Reason <span class="text-red-500">*</span>
            </label>
            <textarea 
              id="overrideReason"
              bind:value={overrideReason}
              rows="3"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              placeholder="Reason for overriding the auto-generated ratings..."
            ></textarea>
          </div>
        {/if}
      </div>
      
      <!-- Visualization -->
      <div>
        <h5 class="text-base font-medium text-gray-900 mb-4">Impact Rating Visualization</h5>
        <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <RadarChart data={radarData} />
        </div>
        
        <!-- Rating Info -->
        <div class="mt-4">
          <h6 class="text-sm font-medium text-gray-700 mb-2">Rating Information</h6>
          
          {#if scenario.sfop_rating_auto_generated}
            <div class="flex items-center text-sm text-blue-700 mb-2">
              <span class="inline-block w-3 h-3 rounded-full bg-blue-500 mr-2"></span>
              <span>Auto-generated ratings</span>
            </div>
          {:else}
            <div class="flex items-center text-sm text-purple-700 mb-2">
              <span class="inline-block w-3 h-3 rounded-full bg-purple-500 mr-2"></span>
              <span>Manually set ratings</span>
            </div>
          {/if}
          
          {#if scenario.sfop_rating_last_edited_at}
            <p class="text-xs text-gray-500 mb-1">
              Last edited by {scenario.sfop_rating_last_edited_by || 'Unknown'} on {new Date(scenario.sfop_rating_last_edited_at).toLocaleString()}
            </p>
          {/if}
          
          {#if scenario.sfop_rating_override_reason}
            <div class="mt-2">
              <p class="text-xs font-medium text-gray-700">Override Reason:</p>
              <p class="text-xs text-gray-600">{scenario.sfop_rating_override_reason}</p>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
  
  <!-- Footer -->
  <div class="px-5 py-4 bg-gray-50 flex justify-end space-x-3">
    <button 
      type="button"
      on:click={handleClose}
      class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
    >
      Cancel
    </button>
    <button 
      type="button"
      on:click={handleSave}
      disabled={isSaving}
      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {#if isSaving}
        <RefreshCw size={16} class="animate-spin" />
        <span>Saving...</span>
      {:else}
        <Save size={16} />
        <span>Save Changes</span>
      {/if}
    </button>
  </div>
</div>
