<script lang="ts">
  import { onMount } from 'svelte';
  import { RefreshCw, Database, Settings, Shield, BarChart, AlertTriangle, Plus, Upload, Download } from '@lucide/svelte';
  import ComponentList from './ComponentList.svelte';
  import { componentApi } from '../api/components';
  import { safeApiCall } from '../utils/error-handler';
  
  // ComponentList instance reference
  let componentListInstance;
  
  // Summary stats
  let stats = {
    totalComponents: 0,
    byType: {
      ECU: 0,
      Sensor: 0,
      Gateway: 0,
      Actuator: 0,
      Network: 0
    },
    bySafetyLevel: {
      'ASIL D': 0,
      'ASIL C': 0,
      'ASIL B': 0,
      'ASIL A': 0,
      'QM': 0
    }
  };
  
  // UI state
  let isLoading = false;
  
  // Demo data for stats
  function updateStats(components: any[]) {
    stats.totalComponents = components.length;
    
    // Reset counts
    Object.keys(stats.byType).forEach(key => {
      stats.byType[key as keyof typeof stats.byType] = 0;
    });
    
    Object.keys(stats.bySafetyLevel).forEach(key => {
      stats.bySafetyLevel[key as keyof typeof stats.bySafetyLevel] = 0;
    });
    
    // Count by type and safety level
    components.forEach(component => {
      if (component.type in stats.byType) {
        stats.byType[component.type as keyof typeof stats.byType]++;
      }
      
      if (component.safety_level in stats.bySafetyLevel) {
        stats.bySafetyLevel[component.safety_level as keyof typeof stats.bySafetyLevel]++;
      }
    });
  }
  
  // Load components on mount
  onMount(async () => {
    await loadComponents();
  });
  
  // Load components from API
  async function loadComponents() {
    isLoading = true;
    const result = await safeApiCall(componentApi.getAll);
    if (result) {
      updateStats(result);
    }
    isLoading = false;
  }
  
  function handleComponentsUpdate(components: any[]) {
    updateStats(components);
  }
  
  // Tab navigation removed - no need for tab management now
</script>

<div>
  <!-- Stats cards area - now uses consistent spacing -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
    <div class="bg-blue-50 rounded-lg p-4 flex items-center border border-blue-100 hover:shadow-md transition-shadow">
      <Database size={24} class="text-blue-500 mr-3" />
      <div>
        <p class="text-sm text-blue-600 font-medium">Total Components</p>
        <p class="text-2xl font-bold text-blue-700">{stats.totalComponents}</p>
      </div>
    </div>
    
    <div class="bg-red-50 rounded-lg p-4 flex items-center border border-red-100 hover:shadow-md transition-shadow">
      <Shield size={24} class="text-red-500 mr-3" />
      <div>
        <p class="text-sm text-red-600 font-medium">ASIL D Components</p>
        <p class="text-2xl font-bold text-red-700">{stats.bySafetyLevel['ASIL D']}</p>
      </div>
    </div>
    
    <div class="bg-orange-50 rounded-lg p-4 flex items-center border border-orange-100 hover:shadow-md transition-shadow">
      <Settings size={24} class="text-orange-500 mr-3" />
      <div>
        <p class="text-sm text-orange-600 font-medium">Electronic Control Units</p>
        <p class="text-2xl font-bold text-orange-700">{stats.byType.ECU}</p>
      </div>
    </div>
    
    <div class="bg-emerald-50 rounded-lg p-4 flex items-center border border-emerald-100 hover:shadow-md transition-shadow">
      <AlertTriangle size={24} class="text-emerald-500 mr-3" />
      <div>
        <p class="text-sm text-emerald-600 font-medium">Sensors</p>
        <p class="text-2xl font-bold text-emerald-700">{stats.byType.Sensor}</p>
      </div>
    </div>
  </div>
  
  <!-- Action bar -->
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold text-gray-800">Component List</h2>
    <div class="flex space-x-2">
      <button 
        on:click={loadComponents}
        class="p-2 text-gray-600 hover:bg-gray-100 rounded-md flex items-center gap-1">
        <RefreshCw size={16} class="{isLoading ? 'animate-spin' : ''}" />
        <span class="sr-only md:not-sr-only">Refresh</span>
      </button>
      
      <button 
        on:click={() => componentListInstance.handleOpenImport()}
        class="p-2 text-gray-600 hover:bg-gray-100 rounded-md flex items-center gap-1">
        <Upload size={16} />
        <span class="sr-only md:not-sr-only">Import</span>
      </button>
      
      <button 
        on:click={() => componentListInstance.handleExportCSV()}
        class="p-2 text-gray-600 hover:bg-gray-100 rounded-md flex items-center gap-1">
        <Download size={16} />
        <span class="sr-only md:not-sr-only">Export</span>
      </button>
      
      <button 
        on:click={() => componentListInstance.handleAddComponent()}
        class="btn btn-primary flex items-center gap-1">
        <Plus size={16} />
        <span>Add Component</span>
      </button>
    </div>
  </div>
  
  <!-- Content area - component list -->
  <ComponentList bind:this={componentListInstance} on:update={e => handleComponentsUpdate(e.detail)} />
</div>
