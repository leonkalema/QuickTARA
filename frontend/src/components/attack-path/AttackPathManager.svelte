<script lang="ts">
  import { onMount } from 'svelte';
  import { 
    getAttackPaths, 
    getAttackChains,
    generateAttackPaths,
    type AttackPath,
    type AttackChain,
    type AttackPathRequest,
    type AttackPathAnalysisResult,
    type AttackPathAssumption,
    type AttackPathConstraint,
    type ThreatScenario,
    AttackPathType,
    AttackComplexity
  } from '../../api/attackPath';
  import { getComponents, type Component } from '../../api/component';
  import { getVulnerabilities } from '../../api/vulnerability';
  import { showNotification } from '../../stores/notification';
  import Spinner from '../ui/Spinner.svelte';
  import AttackPathForm from '../attackPath/AttackPathForm.svelte';
  import AttackPathResults from '../attackPath/AttackPathResults.svelte';
  import AttackPathVisualizer from '../attackPath/AttackPathVisualizer.svelte';
  import Loading from '../common/Loading.svelte';
  import Alert from '../common/Alert.svelte';
  import { fade } from 'svelte/transition';
  
  // State variables
  let paths: AttackPath[] = [];
  let chains: AttackChain[] = [];
  let loading = true;
  let error = '';
  let selectedPathId: string | null = null;
  let selectedChainId: string | null = null;
  let activeTab = 'analysis'; // 'analysis', 'results', or 'history'
  let filterByComplexity: string = '';

  // Component selection for analysis
  let components: Component[] = [];
  let selectedComponents: string[] = [];
  let selectedEntryPoints: string[] = []; 
  let generatingPaths = false;
  let analysisResult: AttackPathAnalysisResult | null = null;
  
  // Track analysis history
  let analysisHistory: { id: string, date: string, components: number, paths: number }[] = [];
  let selectedAnalysisId: string | null = null;
  
  // Access points from selected components
  let accessPointsByComponent: Record<string, string[]> = {};

  // Complexity display names
  const complexityNames = {
    [AttackComplexity.LOW]: 'Low',
    [AttackComplexity.MEDIUM]: 'Medium',
    [AttackComplexity.HIGH]: 'High'
  };
  
  // Complexity color classes
  const complexityColors = {
    [AttackComplexity.LOW]: 'bg-green-100 text-green-800',
    [AttackComplexity.MEDIUM]: 'bg-yellow-100 text-yellow-800',
    [AttackComplexity.HIGH]: 'bg-red-100 text-red-800'
  };

  // Path type display names
  const pathTypeNames = {
    [AttackPathType.DIRECT]: 'Direct',
    [AttackPathType.MULTI_STEP]: 'Multi-Step',
    [AttackPathType.LATERAL]: 'Lateral',
    [AttackPathType.PRIVILEGE_ESCALATION]: 'Privilege Escalation'
  };
  
  // Filtering for paths and chains
  $: filteredPaths = filterByComplexity 
    ? paths.filter(path => path.complexity === filterByComplexity)
    : paths;
    
  $: filteredChains = filterByComplexity 
    ? chains.filter(chain => chain.complexity === filterByComplexity)
    : chains;

  $: selectedPath = selectedPathId ? paths.find(p => p.path_id === selectedPathId) : null;
  $: selectedChain = selectedChainId ? chains.find(c => c.chain_id === selectedChainId) : null;
  
  // Load all data (paths, chains, analysis history)
  async function loadData() {
    try {
      // Get data from the API
      const pathData = await getAttackPaths();
      console.log('Attack paths data:', pathData);
      
      // Store the path data
      if (pathData && pathData.paths) {
        paths = pathData.paths;
      }
      
      // Get chain data
      const chainData = await getAttackChains();
      console.log('Attack chains data:', chainData);
      
      // Store the chain data
      if (chainData && chainData.chains) {
        chains = chainData.chains;
      }
    } catch (err) {
      console.error('Error loading data:', err);
      error = 'Error loading data from API';
    }
  }
  
  // Load components
  async function loadComponents() {
    try {
      const componentList = await getComponents();
      components = componentList || [];
      console.log('Loaded components:', components.length);
    } catch (err) {
      console.error('Error loading components:', err);
      showNotification({ message: 'Failed to load components', type: 'error' });
    }
  }
  
  // Generate attack paths for selected components
  async function generateAttackPathsForComponents() {
    if (selectedComponents.length === 0) {
      showNotification('Please select at least one component', 'warning');
      return;
    }
    
    generatingPaths = true;
    error = '';
    try {
      // Extract component IDs from the accessPointIds (format: "componentId:accessPoint")
      // and create a mapping of components to their access points for logging
      const entryPointComponentMap = {};
      
      if (selectedEntryPoints.length > 0) {
        selectedEntryPoints.forEach(ap => {
          const [compId, accessPoint] = ap.split(':');
          if (!entryPointComponentMap[compId]) {
            entryPointComponentMap[compId] = [];
          }
          entryPointComponentMap[compId].push(accessPoint);
        });
      }
      
      const entryPointComponents = Object.keys(entryPointComponentMap).length > 0 
        ? Object.keys(entryPointComponentMap) 
        : undefined;
      
      // Prepare the request
      const request: AttackPathRequest = {
        component_ids: selectedComponents,
        entry_point_ids: entryPointComponents,
        // We would ideally pass access points too, but the current API doesn't support it
        // So we're keeping the same API interface for now
        include_chains: true,
        max_depth: 5
      };
      
      // Log the selected access points for debugging
      console.log('Selected access points:', selectedEntryPoints);
      console.log('Entry point components and their access points:', entryPointComponentMap);
      console.log('Generating attack paths for components:', request);
      
      // Show progress notification
      showNotification('Generating attack paths, please wait...', 'info', 3000);
      
      // Call the API
      try {
        analysisResult = await generateAttackPaths(request);
        console.log('Analysis result:', analysisResult);
        
        // Show success notification with proper null checking
        if (analysisResult) {
          const totalPaths = analysisResult.total_paths || 0;
          const totalChains = analysisResult.total_chains || 0;
          
          showNotification(`Generated ${totalPaths} attack paths and ${totalChains} chains`, 'success');
          
          // If we got a successful result but no paths/chains, show a helpful message
          if (totalPaths === 0 && totalChains === 0) {
            showNotification(
              'No attack paths were found between the selected components. Try different components or entry points.',
              'info',
              5000
            );
          }
        } else {
          showNotification('Attack path analysis completed but no results were returned', 'info');
        }
      } catch (apiError) {
        console.error('API error generating attack paths:', apiError);
        showNotification('Error generating attack paths. Server may be unavailable.', 'error');
        throw apiError; // Re-throw to be caught by the outer try/catch
      }
      
      // Reload paths and chains
      await loadData();
    } catch (err) {
      console.error('Error generating attack paths:', err);
      error = 'Failed to generate attack paths. Please try again.';
      showNotification(error, 'error');
    } finally {
      generatingPaths = false;
    }
  }
  
  // Toggle component selection
  function toggleComponentSelection(componentId: string) {
    if (selectedComponents.includes(componentId)) {
      selectedComponents = selectedComponents.filter(id => id !== componentId);
      // Also remove any access points from this component from entry points
      selectedEntryPoints = selectedEntryPoints.filter(id => !id.startsWith(`${componentId}:`));
    } else {
      selectedComponents = [...selectedComponents, componentId];
      
      // Extract access points for this component
      const component = components.find(c => c.component_id === componentId || c.id === componentId);
      if (component) {
        // Handle different data structures for access_points
        let accessPoints: string[] = [];
        
        // First try access_points property
        if (component.access_points) {
          if (Array.isArray(component.access_points)) {
            accessPoints = component.access_points;
          } else if (typeof component.access_points === 'string') {
            accessPoints = component.access_points.split('|').filter(ap => ap.trim());
          }
        }
        // If no access_points, try interfaces (from the component model)
        else if (component.interfaces) {
          accessPoints = component.interfaces.map(intf => intf.name || intf.interface_type);
        }
        
        // If still no access points, check if there's a literal 'access_points' string property
        // This handles the case where the API returns a raw string instead of an array
        else if (typeof component['access_points'] === 'string') {
          accessPoints = component['access_points'].split('|').filter(ap => ap.trim());
        }
        
        // Add some default access points if none are defined
        if (accessPoints.length === 0) {
          // Add default access points based on component type
          const componentType = component.component_type || component.type || '';
          const componentTypeStr = String(componentType).toLowerCase();
          
          if (componentTypeStr.includes('gateway') || componentTypeStr.includes('telematics')) {
            accessPoints = ['Ethernet Port', 'Cellular Connection', 'Bluetooth', 'Wi-Fi'];
          } else if (componentTypeStr.includes('ecu')) {
            accessPoints = ['CAN Bus', 'OBD-II Port', 'Debug Port'];
          } else if (componentTypeStr.includes('sensor')) {
            accessPoints = ['Sensor Interface', 'Data Bus'];
          } else {
            accessPoints = ['Network Interface', 'Physical Access Point'];
          }
        }
        
        // Store access points for this component
        accessPointsByComponent[componentId] = accessPoints;
      }
    }
  }
  
  // Toggle access point selection as entry point
  function toggleAccessPointSelection(componentId: string, accessPoint: string) {
    // Create a unique identifier for this access point
    const accessPointId = `${componentId}:${accessPoint}`;
    
    if (selectedEntryPoints.includes(accessPointId)) {
      selectedEntryPoints = selectedEntryPoints.filter(id => id !== accessPointId);
    } else {
      selectedEntryPoints = [...selectedEntryPoints, accessPointId];
    }
  }

  // Check if an access point is selected
  function isAccessPointSelected(componentId: string, accessPoint: string): boolean {
    return selectedEntryPoints.includes(`${componentId}:${accessPoint}`);
  }
  
  // Function to handle completion of analysis
  function onAnalysisComplete(event) {
    // Extract result from the event detail (used when receiving from child component) 
    // or use the parameter directly (when called internally)
    const result = event.detail || event;
    analysisResult = result;
    selectedAnalysisId = result.analysis_id;
    
    // Add to history
    const newHistoryEntry = {
      id: result.analysis_id,
      date: new Date().toLocaleString(),
      components: result.component_count || 0,
      paths: result.total_paths || 0
    };
    analysisHistory = [newHistoryEntry, ...analysisHistory];
    
    // Switch to results tab
    activeTab = 'results';
  }
  
  // Functions implemented below with TypeScript types
  
  // Functions implemented below with TypeScript types

  // Load attack paths and chains on component mount
  onMount(async () => {
    try {
      await Promise.all([loadComponents(), loadData(), loadAnalysisHistory()]);
    } catch (err) {
      console.error('Error during initialization:', err);
      error = 'Failed to initialize. Please refresh the page.';
    } finally {
      loading = false;
    }
  });

  async function loadAnalysisHistory() {
    try {
      // Simple approach - get the data directly from the API
      const result = await getAttackPaths();
      console.log('Analysis history data:', result);
      
      // Reset the history array
      analysisHistory = [];
      
      // Get paths from result
      const paths = result.paths || [];
      console.log('Paths from API:', paths);
      
      // Extract unique analysis IDs
      const uniqueAnalysisIds = new Set();
      
      // Process each path to build history entries
      paths.forEach(path => {
        if (path && path.analysis_id && !uniqueAnalysisIds.has(path.analysis_id)) {
          // Add to set of unique IDs
          uniqueAnalysisIds.add(path.analysis_id);
          
          // Create a history entry
          analysisHistory.push({
            id: path.analysis_id,
            date: new Date(path.created_at || Date.now()).toLocaleString(),
            components: 0,
            paths: paths.filter(p => p.analysis_id === path.analysis_id).length
          });
        }
      });
      
      console.log('Analysis history entries:', analysisHistory);
    } catch (err) {
      console.error('Error loading attack path history:', err);
      error = 'Failed to load attack path history';
    }
  }
  
  // Function to update the analysis filter settings
  function updateAnalysisFilters(filters) {
    console.log('Updating analysis filters:', filters);
    // Implementation to handle filter changes
  }

  // Helper function for analyzing path complexity distribution
  function analyzePathComplexity() {
    const complexityDistribution = {
      low: paths.filter(p => p.complexity === AttackComplexity.LOW).length,
      medium: paths.filter(p => p.complexity === AttackComplexity.MEDIUM).length,
      high: paths.filter(p => p.complexity === AttackComplexity.HIGH).length
    };
    console.log('Path complexity distribution:', complexityDistribution);
    return complexityDistribution;
  }

  // Handle path selection
  function selectPath(pathId: string) {
    selectedPathId = pathId;
    selectedChainId = null;
  }

  // Handle chain selection
  function selectChain(chainId: string) {
    selectedChainId = chainId;
    selectedPathId = null;
  }

  // Switch between paths and chains tabs
  function setActiveTab(tab: string) {
    activeTab = tab;
    selectedPathId = null;
    selectedChainId = null;
  }

  // Filter paths by complexity
  function handleComplexityFilter(e) {
    filterByComplexity = e.target.value;
  }
  

</script>

<div class="container mx-auto px-4 py-8" in:fade={{ duration: 250 }}>
  <div class="flex mb-4 border-b">
    <button 
      class="py-2 px-6 font-medium {activeTab === 'analysis' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}"
      on:click={() => activeTab = 'analysis'}
    >
      New Analysis
    </button>
    
    {#if analysisResult}
      <button 
        class="py-2 px-6 font-medium {activeTab === 'results' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}"
        on:click={() => activeTab = 'results'}
      >
        Current Results
      </button>
    {/if}
    
    <button 
      class="py-2 px-6 font-medium {activeTab === 'history' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}"
      on:click={() => activeTab = 'history'}
    >
      Analysis History
    </button>
  </div>

  {#if loading}
    <div class="flex items-center justify-center p-12">
      <Loading size="lg" message="Loading attack path analysis data..." />
    </div>
  {:else}
    {#if activeTab === 'analysis'}
      <!-- New Enhanced Attack Path Analysis Form -->
      <div transition:fade>
        <AttackPathForm on:analysis-complete={onAnalysisComplete} />
      </div>
    {:else if activeTab === 'results' && analysisResult}
      <!-- Results of current analysis -->
      <div transition:fade>
        <AttackPathResults analysisId={analysisResult.analysis_id} />
      </div>
    {:else if activeTab === 'history'}
      <!-- Analysis History -->
      <div class="bg-white shadow rounded-lg p-6" transition:fade>
        <h3 class="text-xl font-semibold mb-4">Analysis History</h3>
        
        {#if analysisHistory.length === 0}
          <div class="text-center py-8">
            <p class="text-gray-500">No previous analyses found.</p>
          </div>
        {:else}
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Analysis ID</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Components</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Paths</th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                {#each analysisHistory as entry}
                  <tr class={selectedAnalysisId === entry.id ? 'bg-blue-50' : 'hover:bg-gray-50'}>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {entry.date}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900 truncate max-w-[200px]">
                      {entry.id}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {entry.components || '-'}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {entry.paths || 0}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button 
                        class="text-blue-600 hover:text-blue-900 mr-2"
                        on:click={() => {
                          selectedAnalysisId = entry.id;
                          activeTab = 'results';
                        }}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    {:else if activeTab === 'results' && selectedAnalysisId}
      <!-- Results of selected historical analysis -->
      <div transition:fade>
        <AttackPathResults analysisId={selectedAnalysisId} />
      </div>
    {:else}
      <!-- Fallback if no valid tab content -->
      <div class="bg-white shadow rounded-lg p-6 text-center" transition:fade>
        <p class="text-gray-500">Please start a new analysis or select an analysis from history.</p>
      </div>
    {/if}
  {/if}
</div>
