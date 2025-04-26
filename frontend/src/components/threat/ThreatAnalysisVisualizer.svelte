<script lang="ts">
  /**
   * ThreatAnalysisVisualizer Component
   * 
   * This component provides a comprehensive interface for performing STRIDE threat analysis
   * on selected system components. It allows users to:
   * 
   * 1. Load and select components from the system architecture
   * 2. Run threat analysis against selected components
   * 3. View analysis results in multiple visualizations including:
   *    - Component threat summary table
   *    - Threat distribution by STRIDE category
   *    - Detailed threat cards with risk information
   *    - Risk scores and severity indicators
   * 
   * The component handles both API request/response formats and provides error handling
   * and user feedback. It normalizes different API response structures to ensure consistent
   * display regardless of backend changes.
   * 
   * Usage:
   * <ThreatAnalysisVisualizer />
   */
  import { onMount } from 'svelte';
  import { 
    performThreatAnalysis, 
    type ThreatAnalysisResult, 
    type ComponentThreatProfile,
    StrideCategory
  } from '../../api/threat';
  // Using componentApi from components.ts
  import { componentApi, type Component } from '../../api/components';
  import { showNotification } from '../../stores/notification';
  import Spinner from '../ui/Spinner.svelte';
  
  export let selectedComponentIds: string[] = [];
  
  let loading = false;
  let analyzing = false;
  let error = '';
  let isComponentPanelOpen = false;
  let componentSearchTerm = '';
  let componentTypeFilter = '';
  let components: Component[] = [];
  let analysisResult: ThreatAnalysisResult | null = null;
  
  // Pagination parameters
  const COMPONENTS_PER_PAGE = 100;
  const INITIAL_PAGE = 0;
  
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
  function countThreatsByStrideCategory(profiles: ComponentThreatProfile[] | undefined): Record<string, number> {
    const counts: Record<string, number> = {
      [StrideCategory.SPOOFING]: 0,
      [StrideCategory.TAMPERING]: 0,
      [StrideCategory.REPUDIATION]: 0,
      [StrideCategory.INFO_DISCLOSURE]: 0,
      [StrideCategory.DENIAL_OF_SERVICE]: 0,
      [StrideCategory.ELEVATION]: 0
    };
    
    // Check if profiles exists and is iterable
    if (!profiles || !Array.isArray(profiles)) {
      console.log('No threat profiles to count');
      return counts;
    }
    
    // Iterate over profiles safely
    for (const profile of profiles) {
      if (profile && profile.stride_category) {
        counts[profile.stride_category] = (counts[profile.stride_category] || 0) + 1;
      }
    }
    
    return counts;
  }
  
  /**
   * Normalizes different API response formats into a consistent component threat profile structure
   * 
   * This function handles the variations in the API response structure that might occur as
   * the backend evolves or different API endpoints are used. It extracts threat information
   * from different possible structures and converts them into a standard ComponentThreatProfile
   * format that can be consistently used throughout the UI.
   * 
   * The function handles two main response formats:
   * 1. Direct component_threat_profiles array in the response
   * 2. component_analyses array with either threat_matches or threats arrays
   * 
   * @param {any} analysisResult - The raw analysis result from the API
   * @returns {ComponentThreatProfile[]} - Normalized array of component threat profiles
   */
  function extractComponentThreatProfiles(analysisResult: any): ComponentThreatProfile[] {
    // If the result already has component_threat_profiles, return it directly
    if (analysisResult && Array.isArray(analysisResult.component_threat_profiles)) {
      return analysisResult.component_threat_profiles;
    }
    
    // If the result has component_analyses, convert it to the expected format
    if (analysisResult && Array.isArray(analysisResult.component_analyses)) {
      const profiles: ComponentThreatProfile[] = [];
      
      for (const analysis of analysisResult.component_analyses) {
        // Check if the component has threat_matches
        if (analysis.threat_matches && Array.isArray(analysis.threat_matches)) {
          for (const match of analysis.threat_matches) {
            profiles.push({
              component_id: analysis.component_id,
              threat_id: match.threat_id,
              title: match.title,
              description: match.notes || 'No description available',
              stride_category: match.stride_category,
              likelihood: match.calculated_likelihood,
              severity: match.calculated_severity,
              risk_score: match.calculated_risk_score,
              risk_level: match.calculated_risk_score > 16 ? 'CRITICAL' : 
                         match.calculated_risk_score > 9 ? 'HIGH' : 
                         match.calculated_risk_score > 4 ? 'MEDIUM' : 'LOW',
              mitigation_strategies: match.applicable_mitigation_strategies || []
            });
          }
        } else if (analysis.threats && Array.isArray(analysis.threats)) {
          // Alternative structure - threats directly in component_analyses
          for (const threat of analysis.threats) {
            profiles.push({
              component_id: analysis.component_id,
              threat_id: threat.threat_id || '',
              title: threat.title || 'Unknown Threat',
              description: threat.description || 'No description available',
              stride_category: threat.stride_category || StrideCategory.SPOOFING,
              likelihood: threat.likelihood || 3,
              severity: threat.severity || 3,
              risk_score: threat.risk_score || threat.likelihood * threat.severity || 9,
              risk_level: threat.risk_level || 
                         (threat.risk_score > 16 ? 'CRITICAL' : 
                         threat.risk_score > 9 ? 'HIGH' : 
                         threat.risk_score > 4 ? 'MEDIUM' : 'LOW'),
              mitigation_strategies: []
            });
          }
        }
      }
      
      return profiles;
    }
    
    // If neither structure is found, return an empty array
    console.warn('Unknown analysis result structure:', analysisResult);
    return [];
  }
  
  // Get components with threats for matrix display
  function getComponentsWithThreats(): { component: Component, threatCount: number }[] {
    if (!analysisResult || !components.length) return [];
    
    return components
      .filter(comp => selectedComponentIds.includes(comp.component_id))
      .map(comp => {
        const componentThreats = analysisResult.component_threat_profiles.filter(
          profile => profile.component_id === comp.component_id
        );
        return {
          component: comp,
          threatCount: componentThreats.length
        };
      })
      .sort((a, b) => b.threatCount - a.threatCount);
  }
  
  // Load components from the backend using the API client
  async function loadComponents() {
    loading = true;
    error = '';
    
    try {
      // Use the componentApi that's working on the Components page
      const result = await componentApi.getAll();
      console.log('Components API response:', result);
      
      // Set the components for display
      if (Array.isArray(result)) {
        components = result.filter(c => c && c.component_id);
        console.log('Valid components loaded:', components.length);
        
        // Ensure filtered components are updated
        filteredComponents = getFilteredComponents();
        console.log('Initial filtered components:', filteredComponents.length);
      } else {
        console.error('Unexpected format from componentApi.getAll()');
        components = [];
      }
    } catch (err) {
      console.error('Error loading components:', err);
      error = 'Failed to load components from API';
      showNotification('Could not connect to backend API', 'error');
      components = [];
    } finally {
      loading = false;
    }
  }
  
  // Perform threat analysis using the API client as requested
  async function runThreatAnalysis() {
    if (!selectedComponentIds.length) {
      showNotification('Please select at least one component to analyze', 'warning');
      return;
    }
    
    // Make sure we don't have any undefined IDs
    const validComponentIds = selectedComponentIds.filter(id => id !== undefined && id !== null);
    
    if (validComponentIds.length === 0) {
      showNotification('No valid components selected', 'error');
      return;
    }
    
    analyzing = true;
    error = '';
    
    try {
      console.log('Sending threat analysis request with component IDs:', validComponentIds);
      
      // Format the request exactly as expected by the API - simple object with just component_ids
      const requestData = {
        component_ids: validComponentIds
      };
      
      // Use direct fetch for threat analysis to match what works with curl
      const response = await fetch('http://127.0.0.1:8080/api/threat/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(requestData)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API error (${response.status}):`, errorText);
        throw new Error(`API error: ${response.status}`);
      }
      
      // Parse the response JSON
      const rawResult = await response.json();
      console.log('Raw analysis result:', rawResult);
      
      // Process the API response to match our expected format
      analysisResult = {
        ...rawResult,
        component_threat_profiles: extractComponentThreatProfiles(rawResult)
      };
      
      console.log('Processed analysis result:', analysisResult);
      showNotification('Threat analysis completed successfully', 'success');
    } catch (err) {
      console.error('Error performing threat analysis:', err);
      error = 'Failed to perform threat analysis';
      showNotification('Failed to perform threat analysis', 'error');
    } finally {
      analyzing = false;
    }
  }
  
  // Simplified component toggle function for Svelte
  function handleToggleComponent(componentId: string) {
    if (!componentId) {
      console.error('Attempted to toggle undefined component ID');
      return;
    }
    
    console.log('Toggling component:', componentId);
    
    // Create a new array (Svelte reactivity needs assignment, not mutation)
    if (selectedComponentIds.includes(componentId)) {
      // Remove the ID if it's already selected
      selectedComponentIds = selectedComponentIds.filter(id => id !== componentId);
    } else {
      // Add the ID if it's not selected
      selectedComponentIds = [...selectedComponentIds, componentId];
    }
    
    console.log('Updated selected components:', selectedComponentIds);
    
    // Reset analysis result when selection changes
    analysisResult = null;
  }
  
  // Function to get component by ID for displaying threat details
  function getComponentById(id: string): Component | undefined {
    return components.find(comp => comp.component_id === id);
  }
  
  // Component filtering and selection functions
  function getFilteredComponents(): Component[] {
    if (!components || !Array.isArray(components)) return [];
    
    return components.filter(component => {
      // Filter by search term
      const matchesSearch = !componentSearchTerm || 
        (component.name && component.name.toLowerCase().includes(componentSearchTerm.toLowerCase())) ||
        (component.type && component.type.toLowerCase().includes(componentSearchTerm.toLowerCase()));
      
      // Filter by component type
      const matchesType = !componentTypeFilter || 
        (component.type && component.type.toLowerCase().includes(componentTypeFilter.toLowerCase()));
      
      return matchesSearch && matchesType;
    });
  }
  
  function selectAllComponents() {
    const filteredIds = filteredComponents.map(c => c.component_id);
    // Create a new array with all current selections plus new ones, avoiding duplicates
    const newSelections = [...new Set([...selectedComponentIds, ...filteredIds])];
    selectedComponentIds = newSelections;
  }
  
  function clearComponentSelection() {
    // If no filter is applied, clear all selections
    if (!componentSearchTerm && !componentTypeFilter) {
      selectedComponentIds = [];
    } else {
      // Otherwise, only clear filtered components
      const filteredIds = new Set(filteredComponents.map(c => c.component_id));
      selectedComponentIds = selectedComponentIds.filter(id => !filteredIds.has(id));
    }
  }
  
  // Get threat counts by component
  function getThreatCountsByComponent(): Record<string, number> {
    if (!analysisResult) return {};
    
    const counts: Record<string, number> = {};
    
    // Handle differently structured API responses
    if (analysisResult.component_threat_profiles && Array.isArray(analysisResult.component_threat_profiles)) {
      for (const profile of analysisResult.component_threat_profiles) {
        counts[profile.component_id] = (counts[profile.component_id] || 0) + 1;
      }
    } else if (analysisResult.component_analyses && Array.isArray(analysisResult.component_analyses)) {
      // Handle the structure that came back from the API
      for (const analysis of analysisResult.component_analyses) {
        if (analysis.component_id) {
          counts[analysis.component_id] = (analysis.threats?.length || 0);
        }
      }
    }
    
    return counts;
  }
  


  // Define initial empty filtered components array
  let filteredComponents: Component[] = [];
  
  // Update filtered components whenever search term, type filter, or components change
  $: {
    filteredComponents = getFilteredComponents();
    console.log(`Filtered components: ${filteredComponents.length}`);
  }
  
  // Auto-expand panel when search or filter is applied
  $: if (componentSearchTerm || componentTypeFilter) {
    isComponentPanelOpen = true;
  }
  
  // Force the panel to open when components are loaded and there are none selected
  $: if (components.length > 0 && selectedComponentIds.length === 0 && !loading) {
    isComponentPanelOpen = true;
  }
  
  // Auto-close component panel when search is applied and selections are made
  $: if (componentSearchTerm && selectedComponentIds.length > 0) {
    // Add a slight delay so the user can see what was selected
    setTimeout(() => {
      isComponentPanelOpen = false;
    }, 300);
  }
  
  // Auto-expand panel when first loaded if no components are selected
  onMount(() => {
    loadComponents();
    // Automatically expand if no components selected yet
    if (selectedComponentIds.length === 0) {
      isComponentPanelOpen = true;
    }
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
      <!-- Collapsible Component Selection Panel -->
      <div class="border rounded-lg overflow-hidden mb-4">
        {#if !isComponentPanelOpen}
          <!-- Collapsed View with Selection Summary -->
          <div class="p-4 bg-white flex justify-between items-center cursor-pointer" on:click={() => isComponentPanelOpen = true}>
            <div>
              <h3 class="text-lg font-medium flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
                Select Components for Analysis
              </h3>
              
              {#if selectedComponentIds.length > 0}
                <div class="mt-2 flex flex-wrap gap-2">
                  {#each selectedComponentIds.slice(0, 5) as compId}
                    {@const comp = getComponentById(compId)}
                    {#if comp}
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {comp.name}
                        <button on:click|stopPropagation={() => handleToggleComponent(compId)} class="ml-1.5 text-blue-400 hover:text-blue-600">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </span>
                    {/if}
                  {/each}
                  
                  {#if selectedComponentIds.length > 5}
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      +{selectedComponentIds.length - 5} more
                    </span>
                  {/if}
                </div>
              {:else}
                <p class="text-sm text-gray-500 mt-1">No components selected. Click to select components.</p>
              {/if}
            </div>
            
            <div class="flex items-center">
              <span class="text-sm font-medium text-gray-600 mr-3">{selectedComponentIds.length} selected</span>
              <button 
                on:click|stopPropagation={runThreatAnalysis}
                disabled={analyzing || !selectedComponentIds.length}
                class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center
                       disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {#if analyzing}
                  <Spinner size="sm" class="mr-2" />
                  Analyzing...
                {:else}
                  Run Analysis
                {/if}
              </button>
            </div>
          </div>
        {:else}
          <!-- Expanded Panel -->
          <div class="p-4 bg-white border-b">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-medium flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                </svg>
                Select Components for Analysis
              </h3>
              <button 
                on:click={() => isComponentPanelOpen = false}
                class="text-gray-500 hover:text-gray-700"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
            
            <!-- Search and Filter -->
            <div class="flex flex-col sm:flex-row gap-3 mb-4">
              <div class="relative flex-grow">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input 
                  type="text" 
                  placeholder="Search components..." 
                  bind:value={componentSearchTerm}
                  class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
              
              <select 
                bind:value={componentTypeFilter}
                class="block w-full sm:w-48 px-3 py-2 border border-gray-300 rounded-md text-sm">
                <option value="">All Types</option>
                <option value="sensor">Sensor</option>
                <option value="actuator">Actuator</option>
                <option value="controller">Controller</option>
                <option value="gateway">Gateway</option>
                <option value="storage">Storage</option>
                <option value="communication">Communication</option>
                <option value="interface">Interface</option>
                <option value="external">External Service</option>
              </select>
              
              <div class="flex">
                <button 
                  on:click={selectAllComponents}
                  class="px-3 py-2 bg-gray-100 text-gray-700 rounded-l-md border border-gray-300 text-sm hover:bg-gray-200"
                >
                  Select All
                </button>
                <button 
                  on:click={clearComponentSelection}
                  class="px-3 py-2 bg-gray-100 text-gray-700 rounded-r-md border-t border-r border-b border-gray-300 text-sm hover:bg-gray-200"
                >
                  Clear
                </button>
              </div>
            </div>
            
            <!-- Component List with Virtual Scrolling -->
            <div class="max-h-80 overflow-y-auto border rounded-md">
              {#if loading}
                <div class="p-8 text-center">
                  <Spinner size="md" />
                  <p class="mt-2 text-gray-500">Loading components...</p>
                </div>
              {:else if filteredComponents.length === 0}
                <div class="p-4 text-center text-gray-500">
                  {componentSearchTerm || componentTypeFilter
                    ? 'No components match your search criteria'
                    : 'No components available'}
                </div>
              {:else}
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50 sticky top-0">
                    <tr>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-8">
                        <span class="sr-only">Select</span>
                      </th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    {#each filteredComponents as component}
                      <tr class="hover:bg-gray-50 cursor-pointer" on:click={() => handleToggleComponent(component.component_id)}>
                        <td class="px-4 py-2 whitespace-nowrap">
                          <input 
                            type="checkbox"
                            class="h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
                            checked={selectedComponentIds.includes(component.component_id)}
                            on:change|stopPropagation={() => handleToggleComponent(component.component_id)}
                          />
                        </td>
                        <td class="px-4 py-2 whitespace-nowrap">
                          <div class="text-sm font-medium text-gray-900">{component.name || 'Unnamed Component'}</div>
                        </td>
                        <td class="px-4 py-2 whitespace-nowrap">
                          <div class="text-sm text-gray-500">{component.type || 'Unknown Type'}</div>
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              {/if}
            </div>
            
            <!-- Action Buttons -->
            <div class="mt-4 flex justify-between">
              <div>
                <span class="text-sm text-gray-600">{selectedComponentIds.length} of {components.length} components selected</span>
              </div>
              <div class="flex space-x-3">
                <button 
                  on:click={() => isComponentPanelOpen = false}
                  class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Done
                </button>
                <button 
                  on:click={() => { isComponentPanelOpen = false; runThreatAnalysis(); }}
                  disabled={analyzing || !selectedComponentIds.length}
                  class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center
                         disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {#if analyzing}
                    <Spinner size="sm" class="mr-2" />
                    Analyzing...
                  {:else}
                    Run Analysis
                  {/if}
                </button>
              </div>
            </div>
          </div>
        {/if}
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
              {analysisResult.component_threat_profiles && analysisResult.component_threat_profiles.length > 0 
                ? Math.max(...analysisResult.component_threat_profiles.map(t => t.risk_score || 0)) 
                : 0}
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
                  
                  <!-- Handle different API response structures -->
                  {@const componentThreats = analysisResult.component_threat_profiles 
                    ? analysisResult.component_threat_profiles.filter(p => p.component_id === componentId)
                    : []}
                  
                  <!-- Check for component_analyses structure -->
                  {@const componentAnalysis = analysisResult.component_analyses 
                    ? analysisResult.component_analyses.find(a => a.component_id === componentId)
                    : null}
                  
                  {@const threatsByCategory = countThreatsByStrideCategory(componentThreats)}
                  {@const totalThreats = componentThreats.length || (componentAnalysis?.threats?.length || 0)}
                  
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
            {#if analysisResult.component_threat_profiles && Array.isArray(analysisResult.component_threat_profiles)}
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
            {:else if analysisResult.component_analyses && Array.isArray(analysisResult.component_analyses)}
              <!-- Handle new API response structure -->
              {#each analysisResult.component_analyses as analysis}
                {#if analysis.threats && analysis.threats.length > 0}
                  {#each analysis.threats.slice(0, 5) as threat}  
                    {@const component = getComponentById(analysis.component_id)}
                    {#if component}
                      <div class="border rounded-md p-4 hover:bg-gray-50">
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-2">
                          <div>
                            <h5 class="font-semibold">{threat.title || 'Unknown Threat'}</h5>
                            <div class="text-sm text-gray-600">Component: {component.name}</div>
                          </div>
                          <div class="flex items-center mt-2 sm:mt-0">
                            <span class="px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800">
                              {threat.stride_category || 'Unknown'}
                            </span>
                            <div class="ml-3 px-3 py-1 rounded-full text-sm font-semibold bg-yellow-100 text-yellow-800">
                              {threat.risk_level || 'Medium'}
                            </div>
                          </div>
                        </div>
                        <p class="text-sm text-gray-700 mb-3">{threat.description || 'No description available'}</p>
                      </div>
                    {/if}
                  {/each}
                {/if}
              {/each}
            {/if}
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>
