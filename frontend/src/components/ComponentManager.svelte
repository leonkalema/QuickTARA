<script lang="ts">
  import { onMount } from 'svelte';
  import { RefreshCw, Database, Settings, Shield, BarChart, AlertTriangle, Plus, Upload, Download } from '@lucide/svelte';
  import ComponentList from './ComponentList.svelte';
  import { componentApi } from '../api/components';
  import { safeApiCall } from '../utils/error-handler';
  
  // ComponentList instance reference
  // Add proper type to avoid TypeScript warnings
  let componentListInstance: any;
  
  // Summary stats
  let stats = {
    totalComponents: 0,
    unreviewedThreats: 5, // This would normally come from an API call to get actual pending threats
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
  <!-- Stats cards area with new warm color palette -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
    <!-- Simple Critical Status Metric -->
    <div class="metric-card">
      <div class="flex items-start">
        <AlertTriangle size={20} 
          class="mr-3 mt-1"
          style={`color: ${stats.unreviewedThreats > 0 ? 'var(--color-danger)' : 'var(--color-success)'}`} 
        />
        <div>
          <p class="metric-label">Unreviewed Threats</p>
          <p class="metric-value" style={`color: ${stats.unreviewedThreats > 0 ? 'var(--color-danger)' : 'var(--color-success)'}`}>
            {stats.unreviewedThreats}
          </p>
        </div>
      </div>
    </div>
    
    <div class="metric-card">
      <div class="flex items-start">
        <Database size={24} style="color: var(--color-primary);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Total Components</p>
          <p class="metric-value">{stats.totalComponents}</p>
        </div>
      </div>
    </div>
    
    <div class="metric-card">
      <div class="flex items-start">
        <Shield size={24} style="color: var(--color-secondary);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">ASIL D Components</p>
          <p class="metric-value">{stats.bySafetyLevel['ASIL D']}</p>
        </div>
      </div>
    </div>
    
    <div class="metric-card">
      <div class="flex items-start">
        <Settings size={24} style="color: var(--color-success);" class="mr-3 mt-1" />
        <div>
          <p class="metric-label">Electronic Control Units</p>
          <p class="metric-value">{stats.byType.ECU}</p>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Action bar with warm styling -->
  <div class="flex justify-between items-center mb-6">
    <h2 class="text-xl font-semibold" style="color: var(--color-text-main);">Component List</h2>
    <div class="flex space-x-2">
      <button 
        on:click={loadComponents}
        style="color: var(--color-text-muted); background-color: rgba(255, 255, 255, 0.5);" 
        class="p-2 rounded-md flex items-center gap-1 transition-all duration-200 hover:shadow-sm border border-transparent hover:border-gray-200">
        <RefreshCw size={16} class="{isLoading ? 'animate-spin' : ''}" />
        <span class="sr-only md:not-sr-only">Refresh</span>
      </button>
      
      <button 
        on:click={() => componentListInstance.handleOpenImport()}
        style="color: var(--color-text-muted); background-color: rgba(255, 255, 255, 0.5);"
        class="p-2 rounded-md flex items-center gap-1 transition-all duration-200 hover:shadow-sm border border-transparent hover:border-gray-200">
        <Upload size={16} />
        <span class="sr-only md:not-sr-only">Import</span>
      </button>
      
      <button 
        on:click={() => componentListInstance.handleExportCSV()}
        style="color: var(--color-text-muted); background-color: rgba(255, 255, 255, 0.5);"
        class="p-2 rounded-md flex items-center gap-1 transition-all duration-200 hover:shadow-sm border border-transparent hover:border-gray-200">
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
