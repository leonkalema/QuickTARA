<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    performThreatAnalysis, 
    type ThreatAnalysisResult, 
    type ComponentThreatProfile,
    StrideCategory
  } from '../../api/threat';
  import { getComponents } from '../../api/component';
  import type { Component } from '../../api/component';
  import { showNotification } from '../../stores/notification';
  import Spinner from '../ui/Spinner.svelte';
  
  export let selectedComponentIds: string[] = [];
  
  let loading = false;
  let analyzing = false;
  let error = '';
  let components: Component[] = [];
  let analysisResult: ThreatAnalysisResult | null = null;
  
  // STRIDE category display names
  const strideCategoryNames = {
    [StrideCategory.SPOOFING]: 'Spoofing',
    [StrideCategory.TAMPERING]: 'Tampering',
    [StrideCategory.REPUDIATION]: 'Repudiation',
    [StrideCategory.INFO_DISCLOSURE]: 'Information Disclosure',
    [StrideCategory.DENIAL_OF_SERVICE]: 'Denial of Service',
    [StrideCategory.ELEVATION]: 'Elevation of Privilege'
  };
  
  // Risk level colors
  const riskLevelColors = {
    'LOW': 'bg-green-100 text-green-800 border-green-200',
    'MEDIUM': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'HIGH': 'bg-orange-100 text-orange-800 border-orange-200',
    'CRITICAL': 'bg-red-100 text-red-800 border-red-200'
  };
  
  // Get background color based on risk score (1-25)
  function getRiskScoreColor(score: number): string {
    if (score <= 4) return 'bg-green-500';
    if (score <= 9) return 'bg-yellow-500';
    if (score <= 16) return 'bg-orange-500';
    return 'bg-red-500';
  }
  
  // Calculate width percentage for risk score display
  function getRiskScoreWidth(score: number): string {
    // Max score is 25 (5*5), so convert to percentage
    return `${(score / 25) * 100}%`;
  }
  
  // Sort threats by risk score (high to low)
  function sortByRiskScore(a: ComponentThreatProfile, b: ComponentThreatProfile): number {
    return (b.risk_score || 0) - (a.risk_score || 0);
  }
  
  // Count threats by STRIDE category
  function countThreatsByStrideCategory(profiles: ComponentThreatProfile[]): Record<string, number> {
    const counts: Record<string, number> = {
      [StrideCategory.SPOOFING]: 0,
      [StrideCategory.TAMPERING]: 0,
      [StrideCategory.REPUDIATION]: 0,
      [StrideCategory.INFO_DISCLOSURE]: 0,
      [StrideCategory.DENIAL_OF_SERVICE]: 0,
      [StrideCategory.ELEVATION]: 0
    };
    
    for (const profile of profiles) {
      if (profile.stride_category) {
        counts[profile.stride_category] = (counts[profile.stride_category] || 0) + 1;
      }
    }
    
    return counts;
  }
  
  // Get components with threats for matrix display
  function getComponentsWithThreats(): { component: Component, threatCount: number }[] {
    if (!analysisResult || !components.length) return [];
    
    return components
      .filter(comp => selectedComponentIds.includes(comp.id))
      .map(comp => {
        const componentThreats = analysisResult.component_threat_profiles.filter(
          profile => profile.component_id === comp.id
        );
        return {
          component: comp,
          threatCount: componentThreats.length
        };
      })
      .sort((a, b) => b.threatCount - a.threatCount);
  }
  
  // Load components
  async function loadComponents() {
    loading = true;
    error = '';
    
    try {
      const result = await getComponents();
      components = result;
    } catch (err) {
      console.error('Error loading components:', err);
      error = 'Failed to load components';
      showNotification('Failed to load components', 'error');
    } finally {
      loading = false;
    }
  }
  
  // Perform threat analysis
  async function runThreatAnalysis() {
    if (!selectedComponentIds.length) {
      showNotification('Please select at least one component to analyze', 'warning');
      return;
    }
    
    analyzing = true;
    error = '';
    
    try {
      analysisResult = await performThreatAnalysis(selectedComponentIds);
      showNotification('Threat analysis completed successfully', 'success');
    } catch (err) {
      console.error('Error performing threat analysis:', err);
      error = 'Failed to perform threat analysis';
      showNotification('Failed to perform threat analysis', 'error');
    } finally {
      analyzing = false;
    }
  }
  
  // Handle component selection
  function handleComponentChange(componentId: string, isSelected: boolean) {
    if (isSelected) {
      selectedComponentIds = [...selectedComponentIds, componentId];
    } else {
      selectedComponentIds = selectedComponentIds.filter(id => id !== componentId);
    }
    
    // Reset analysis result when selection changes
    analysisResult = null;
  }
  
  // Get component by ID
  function getComponentById(id: string): Component | undefined {
    return components.find(comp => comp.id === id);
  }
  
  // Get threat counts by component
  function getThreatCountByComponent(): Record<string, number> {
    if (!analysisResult) return {};
    
    const counts: Record<string, number> = {};
    for (const profile of analysisResult.component_threat_profiles) {
      counts[profile.component_id] = (counts[profile.component_id] || 0) + 1;
    }
    
    return counts;
  }
  
  onMount(() => {
    loadComponents();
  });
</script>

<div class="container mx-auto px-4 py-6">
  <h2 class="text-2xl font-semibold mb-6">STRIDE Threat Analysis</h2>
  
  {#if loading}
    <div class="flex justify-center py-8">
      <Spinner size="lg" />
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline"> {error}</span>
    </div>
  {:else}
    <div class="mb-6">
      <h3 class="text-lg font-medium mb-3">Select Components to Analyze</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {#each components as component}
          <label class="flex items-center p-3 border rounded-md hover:bg-gray-50 cursor-pointer">
            <input 
              type="checkbox" 
              value={component.id} 
              checked={selectedComponentIds.includes(component.id)}
              on:change={(e) => handleComponentChange(component.id, e.target.checked)}
              class="mr-2"
            />
            <div>
              <div class="font-medium">{component.name}</div>
              <div class="text-sm text-gray-500">{component.component_type}</div>
            </div>
          </label>
        {/each}
      </div>
      
      <div class="mt-4 flex justify-end">
        <button 
          on:click={runThreatAnalysis}
          disabled={analyzing || !selectedComponentIds.length}
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center
                 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {#if analyzing}
            <Spinner size="sm" class="mr-2" />
            Analyzing...
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3.707 5.293a1 1 0 00-1.414 1.414l7 7a1 1 0 001.414 0l7-7a1 1 0 00-1.414-1.414L11 10.586V3a1 1 0 10-2 0v7.586l-5.293-5.293z" clip-rule="evenodd" />
            </svg>
            Run Analysis
          {/if}
        </button>
      </div>
    </div>
    
    {#if analysisResult}
      <div class="mb-10">
        <h3 class="text-xl font-semibold mb-4">Analysis Results</h3>
        
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div class="bg-white p-4 border rounded-lg shadow-sm">
            <div class="text-sm text-gray-500">Total Threats Identified</div>
            <div class="text-3xl font-bold mt-1">{analysisResult.component_threat_profiles.length}</div>
          </div>
          
          <div class="bg-white p-4 border rounded-lg shadow-sm">
            <div class="text-sm text-gray-500">Components Analyzed</div>
            <div class="text-3xl font-bold mt-1">{selectedComponentIds.length}</div>
          </div>
          
          <div class="bg-white p-4 border rounded-lg shadow-sm">
            <div class="text-sm text-gray-500">Avg. Threats per Component</div>
            <div class="text-3xl font-bold mt-1">
              {(analysisResult.component_threat_profiles.length / selectedComponentIds.length).toFixed(1)}
            </div>
          </div>
          
          <div class="bg-white p-4 border rounded-lg shadow-sm">
            <div class="text-sm text-gray-500">Highest Risk Score</div>
            <div class="text-3xl font-bold mt-1">
              {Math.max(...analysisResult.component_threat_profiles.map(t => t.risk_score || 0))}
            </div>
          </div>
        </div>
        
        <!-- STRIDE Category Distribution -->
        <div class="mb-8 bg-white p-5 border rounded-lg shadow-sm">
          <h4 class="text-lg font-medium mb-3">STRIDE Category Distribution</h4>
          <div class="grid grid-cols-3 md:grid-cols-6 gap-3">
            {#each Object.entries(countThreatsByStrideCategory(analysisResult.component_threat_profiles)) as [category, count]}
              <div class="text-center p-3 border rounded-md
                          {category === StrideCategory.SPOOFING ? 'bg-purple-50 border-purple-200' : 
                           category === StrideCategory.TAMPERING ? 'bg-yellow-50 border-yellow-200' : 
                           category === StrideCategory.REPUDIATION ? 'bg-blue-50 border-blue-200' : 
                           category === StrideCategory.INFO_DISCLOSURE ? 'bg-green-50 border-green-200' : 
                           category === StrideCategory.DENIAL_OF_SERVICE ? 'bg-red-50 border-red-200' : 
                           'bg-orange-50 border-orange-200'}">
                <div class="text-2xl font-bold">{count}</div>
                <div class="text-xs mt-1">{strideCategoryNames[category]}</div>
              </div>
            {/each}
          </div>
        </div>
        
        <!-- Component Threat Matrix -->
        <div class="mb-8 bg-white p-5 border rounded-lg shadow-sm">
          <h4 class="text-lg font-medium mb-3">Component Threat Matrix</h4>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div class="flex items-center justify-center">
                      <span class="w-6 h-6 flex items-center justify-center rounded-full bg-purple-100 text-purple-800 text-xs font-bold">S</span>
                    </div>
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div class="flex items-center justify-center">
                      <span class="w-6 h-6 flex items-center justify-center rounded-full bg-yellow-100 text-yellow-800 text-xs font-bold">T</span>
                    </div>
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div class="flex items-center justify-center">
                      <span class="w-6 h-6 flex items-center justify-center rounded-full bg-blue-100 text-blue-800 text-xs font-bold">R</span>
                    </div>
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div class="flex items-center justify-center">
                      <span class="w-6 h-6 flex items-center justify-center rounded-full bg-green-100 text-green-800 text-xs font-bold">I</span>
                    </div>
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div class="flex items-center justify-center">
                      <span class="w-6 h-6 flex items-center justify-center rounded-full bg-red-100 text-red-800 text-xs font-bold">D</span>
                    </div>
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div class="flex items-center justify-center">
                      <span class="w-6 h-6 flex items-center justify-center rounded-full bg-orange-100 text-orange-800 text-xs font-bold">E</span>
                    </div>
                  </th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                {#each selectedComponentIds as componentId}
                  {@const component = getComponentById(componentId)}
                  {@const componentThreats = analysisResult.component_threat_profiles.filter(p => p.component_id === componentId)}
                  {@const threatsByCategory = countThreatsByStrideCategory(componentThreats)}
                  {@const totalThreats = componentThreats.length}
                  
                  {#if component}
                    <tr class="hover:bg-gray-50">
                      <td class="px-4 py-3 whitespace-nowrap text-sm font-medium">{component.name}</td>
                      <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{component.component_type}</td>
                      <td class="px-4 py-3 whitespace-nowrap text-center">
                        {#if threatsByCategory[StrideCategory.SPOOFING] > 0}
                          <span class="inline-flex items-center justify-center w-6 h-6 bg-purple-100 text-purple-800 text-xs font-bold rounded-full">
                            {threatsByCategory[StrideCategory.SPOOFING]}
                          </span>
                        {/if}
                      </td>
                      <td class="px-4 py-3 whitespace-nowrap text-center">
                        {#if threatsByCategory[StrideCategory.TAMPERING] > 0}
                          <span class="inline-flex items-center justify-center w-6 h-6 bg-yellow-100 text-yellow-800 text-xs font-bold rounded-full">
                            {threatsByCategory[StrideCategory.TAMPERING]}
                          </span>
                        {/if}
                      </td>
                      <td class="px-4 py-3 whitespace-nowrap text-center">
                        {#if threatsByCategory[StrideCategory.REPUDIATION] > 0}
                          <span class="inline-flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-800 text-xs font-bold rounded-full">
                            {threatsByCategory[StrideCategory.REPUDIATION]}
                          </span>
                        {/if}
                      </td>
                      <td class="px-4 py-3 whitespace-nowrap text-center">
                        {#if threatsByCategory[StrideCategory.INFO_DISCLOSURE] > 0}
                          <span class="inline-flex items-center justify-center w-6 h-6 bg-green-100 text-green-800 text-xs font-bold rounded-full">
                            {threatsByCategory[StrideCategory.INFO_DISCLOSURE]}
                          </span>
                        {/if}
                      </td>
                      <td class="px-4 py-3 whitespace-nowrap text-center">
                        {#if threatsByCategory[StrideCategory.DENIAL_OF_SERVICE] > 0}
                          <span class="inline-flex items-center justify-center w-6 h-6 bg-red-100 text-red-800 text-xs font-bold rounded-full">
                            {threatsByCategory[StrideCategory.DENIAL_OF_SERVICE]}
                          </span>
                        {/if}
                      </td>
                      <td class="px-4 py-3 whitespace-nowrap text-center">
                        {#if threatsByCategory[StrideCategory.ELEVATION] > 0}
                          <span class="inline-flex items-center justify-center w-6 h-6 bg-orange-100 text-orange-800 text-xs font-bold rounded-full">
                            {threatsByCategory[StrideCategory.ELEVATION]}
                          </span>
                        {/if}
                      </td>
                      <td class="px-4 py-3 whitespace-nowrap text-center font-semibold">{totalThreats}</td>
                    </tr>
                  {/if}
                {/each}
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Top Threats by Risk -->
        <div class="bg-white p-5 border rounded-lg shadow-sm">
          <h4 class="text-lg font-medium mb-3">Top Threats by Risk</h4>
          
          <div class="space-y-4">
            {#each [...analysisResult.component_threat_profiles].sort(sortByRiskScore).slice(0, 10) as threatProfile}
              {@const component = getComponentById(threatProfile.component_id)}
              {#if component}
                <div class="border rounded-md p-4 hover:bg-gray-50">
                  <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-2">
                    <div>
                      <h5 class="font-semibold">{threatProfile.title}</h5>
                      <div class="text-sm text-gray-600">Component: {component.name}</div>
                    </div>
                    <div class="flex items-center mt-2 sm:mt-0">
                      <span class="px-3 py-1 rounded-full text-sm font-semibold 
                        {threatProfile.stride_category === StrideCategory.SPOOFING ? 'bg-purple-100 text-purple-800' : 
                         threatProfile.stride_category === StrideCategory.TAMPERING ? 'bg-yellow-100 text-yellow-800' : 
                         threatProfile.stride_category === StrideCategory.REPUDIATION ? 'bg-blue-100 text-blue-800' : 
                         threatProfile.stride_category === StrideCategory.INFO_DISCLOSURE ? 'bg-green-100 text-green-800' : 
                         threatProfile.stride_category === StrideCategory.DENIAL_OF_SERVICE ? 'bg-red-100 text-red-800' : 
                         'bg-orange-100 text-orange-800'}">
                        {strideCategoryNames[threatProfile.stride_category]}
                      </span>
                      
                      <div class="ml-3 px-3 py-1 rounded-full text-sm font-semibold
                        {riskLevelColors[threatProfile.risk_level]}">
                        {threatProfile.risk_level}
                      </div>
                    </div>
                  </div>
                  
                  <p class="text-sm text-gray-700 mb-3">{threatProfile.description}</p>
                  
                  <div class="mt-2">
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs font-medium">Risk Score: {threatProfile.risk_score}</span>
                      <span class="text-xs text-gray-500">({threatProfile.likelihood} × {threatProfile.severity})</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class={`${getRiskScoreColor(threatProfile.risk_score)} h-2 rounded-full`} 
                           style="width: {getRiskScoreWidth(threatProfile.risk_score)}"></div>
                    </div>
                  </div>
                </div>
              {/if}
            {/each}
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>
