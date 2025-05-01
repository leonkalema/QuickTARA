<!-- Attack Path Analysis Results Component -->
<script>
  import { onMount } from 'svelte';
  import { getAttackPaths, getAttackChains } from '../../api/attackPath';
  import AttackPathVisualizer from './AttackPathVisualizer.svelte';
  import Loading from '../common/Loading.svelte';
  import Alert from '../common/Alert.svelte';
  
  // Props
  export let analysisId = '';
  
  // Component state
  let loading = false;
  let error = null;
  let paths = [];
  let chains = [];
  let selectedPathId = '';
  let activeTab = 'paths'; // 'paths' or 'chains'
  
  onMount(async () => {
    if (analysisId) {
      await fetchAnalysisData();
    }
  });
  
  async function fetchAnalysisData() {
    try {
      loading = true;
      error = null;
      
      console.log('Fetching analysis data for ID:', analysisId);
      
      // Get paths for this analysis
      const result = await getAttackPaths(analysisId);
      console.log('Attack paths result:', result);
      
      // Get the paths from the result
      paths = result.paths || [];
      console.log('Paths loaded:', paths.length);
      
      // Get chains for this analysis
      const chainResult = await getAttackChains(analysisId);
      console.log('Attack chains result:', chainResult);
      
      // Get the chains from the result
      chains = chainResult.chains || [];
      console.log('Chains loaded:', chains.length);
      
      // Select the first path if we have any
      if (paths.length > 0 && !selectedPathId) {
        selectedPathId = paths[0].path_id;
      }
      
      loading = false;
    } catch (err) {
      console.error('Error fetching data:', err);
      error = 'Failed to fetch data';
      loading = false;
    }
  }
  
  function selectPath(pathId) {
    selectedPathId = pathId;
    activeTab = 'paths';
  }
  
  function switchTab(tab) {
    activeTab = tab;
    // If switching to paths tab and no path selected, select the first one
    if (tab === 'paths' && !selectedPathId && paths.length > 0) {
      selectedPathId = paths[0].path_id;
    }
  }
  
  // Sort paths by risk score (high to low)
  $: sortedPaths = [...paths].sort((a, b) => b.risk_score - a.risk_score);
  
  // Sort chains by risk score (high to low)
  $: sortedChains = [...chains].sort((a, b) => b.risk_score - a.risk_score);
  
  // Find the selected path object
  $: selectedPath = paths.find(p => p.path_id === selectedPathId);
</script>

<div class="attack-path-results">
  <h2 class="text-2xl font-bold mb-6">Attack Path Analysis Results</h2>
  
  {#if error}
    <Alert type="error" message={error} />
  {/if}
  
  {#if loading}
    <Loading message="Loading analysis results..." />
  {:else if !analysisId}
    <Alert type="info" message="No analysis ID provided. Please start an analysis first." />
  {:else if paths.length === 0}
    <Alert type="info" message="No attack paths found for this analysis." />
  {:else}
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- Sidebar -->
      <div class="lg:col-span-1 bg-white shadow rounded-lg p-4">
        <!-- Tab navigation -->
        <div class="flex border-b border-gray-200 mb-4">
          <button 
            class="py-2 px-4 font-medium text-sm {activeTab === 'paths' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}"
            on:click={() => switchTab('paths')}
          >
            Paths ({paths.length})
          </button>
          <button 
            class="py-2 px-4 font-medium text-sm {activeTab === 'chains' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'}"
            on:click={() => switchTab('chains')}
          >
            Chains ({chains.length})
          </button>
        </div>
        
        <!-- List of paths or chains -->
        {#if activeTab === 'paths'}
          <div class="space-y-2 max-h-[600px] overflow-y-auto">
            {#each sortedPaths as path}
              <button 
                class="w-full p-3 text-left rounded border {selectedPathId === path.path_id ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200 hover:bg-gray-100'}"
                on:click={() => selectPath(path.path_id)}
              >
                <div class="flex justify-between items-center">
                  <span class="text-sm font-medium truncate flex-grow">{path.name}</span>
                  <span 
                    class="ml-2 px-2 py-1 text-xs font-medium rounded-full {
                      path.risk_score >= 7 ? 'bg-red-100 text-red-800' : 
                      path.risk_score >= 4 ? 'bg-yellow-100 text-yellow-800' : 
                      'bg-green-100 text-green-800'
                    }"
                  >
                    {path.risk_score.toFixed(1)}
                  </span>
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  {path.entry_point_id} → {path.target_id}
                </div>
              </button>
            {/each}
          </div>
        {:else if activeTab === 'chains'}
          <div class="space-y-2 max-h-[600px] overflow-y-auto">
            {#each sortedChains as chain}
              <div class="p-3 bg-gray-50 rounded border border-gray-200">
                <div class="flex justify-between items-center">
                  <span class="text-sm font-medium truncate flex-grow">{chain.name}</span>
                  <span 
                    class="ml-2 px-2 py-1 text-xs font-medium rounded-full {
                      chain.risk_score >= 7 ? 'bg-red-100 text-red-800' : 
                      chain.risk_score >= 4 ? 'bg-yellow-100 text-yellow-800' : 
                      'bg-green-100 text-green-800'
                    }"
                  >
                    {chain.risk_score.toFixed(1)}
                  </span>
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  {chain.entry_point_id} → {chain.final_target_id}
                </div>
                <div class="text-xs text-gray-500 mt-1">
                  {chain.total_steps} steps | {chain.complexity} complexity
                </div>
                <div class="mt-2">
                  <h4 class="text-xs font-medium">Paths in this chain:</h4>
                  <div class="ml-2 mt-1 space-y-1">
                    {#each chain.paths || [] as chainPath}
                      <button 
                        class="block text-xs text-blue-600 hover:underline"
                        on:click={() => selectPath(chainPath.path_id)}
                      >
                        {chainPath.name}
                      </button>
                    {/each}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
      
      <!-- Main content area -->
      <div class="lg:col-span-3 bg-white shadow rounded-lg p-4">
        {#if activeTab === 'paths' && selectedPath}
          <AttackPathVisualizer pathData={selectedPath} />
        {:else if activeTab === 'chains'}
          <div class="p-6 text-center">
            <h3 class="text-xl font-semibold mb-4">Attack Chain Details</h3>
            <p class="text-gray-600 mb-4">
              Attack chains represent multiple connected attack paths that an attacker could use to achieve their objectives.
            </p>
            <p class="text-gray-600">
              Select a path from a chain in the sidebar to view its details and visualization.
            </p>
          </div>
        {:else}
          <div class="p-6 text-center">
            <p class="text-gray-600">
              Select an attack path from the sidebar to view its details.
            </p>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>
