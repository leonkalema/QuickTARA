<script lang="ts">
  import { onMount } from 'svelte';
  import { RefreshCw, Database, Settings, Shield, BarChart, AlertTriangle } from '@lucide/svelte';
  import ComponentList from './ComponentList.svelte';
  
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
  
  // Current tab
  let activeTab = 'components'; // 'components', 'analysis', 'settings'
  
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
  
  // Mock data for display
  onMount(() => {
    const mockComponents = [
      {
        component_id: "ECU001",
        name: "Engine Control Unit",
        type: "ECU",
        safety_level: "ASIL D",
        interfaces: ["CAN", "FlexRay"],
        access_points: ["OBD-II", "Debug Port"],
        data_types: ["Control Commands", "Sensor Data"],
        location: "Internal",
        trust_zone: "Critical",
        connected_to: ["ECU002", "ECU003", "SNS001"]
      },
      {
        component_id: "SNS001",
        name: "Wheel Speed Sensor",
        type: "Sensor",
        safety_level: "ASIL B",
        interfaces: ["CAN"],
        access_points: [],
        data_types: ["Sensor Data"],
        location: "External",
        trust_zone: "Untrusted",
        connected_to: ["ECU001"]
      },
      {
        component_id: "GWY001",
        name: "Telematics Gateway",
        type: "Gateway",
        safety_level: "ASIL C",
        interfaces: ["CAN", "Ethernet", "4G"],
        access_points: ["USB", "Debug Port"],
        data_types: ["All Traffic", "Diagnostic Data"],
        location: "Internal",
        trust_zone: "Boundary",
        connected_to: ["ECU001", "ECU004", "ECU005"]
      }
    ];
    
    updateStats(mockComponents);
  });
  
  function handleComponentsUpdate(components: any[]) {
    updateStats(components);
  }
  
  // Tab management
  function setActiveTab(tab: string) {
    activeTab = tab;
  }
</script>

<div class="bg-gray-50 min-h-screen">
  <!-- Header with statistics -->
  <div class="bg-white border-b border-gray-200 shadow-sm">
    <div class="container mx-auto px-4 py-3 max-w-7xl">
      <div class="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">QuickTARA</h1>
          <p class="text-gray-600">Automotive Security Analysis</p>
        </div>
        
        <div class="flex flex-wrap gap-4">
          <div class="bg-blue-50 rounded-lg px-4 py-2 flex items-center border border-blue-100">
            <Database size={20} class="text-blue-500 mr-2" />
            <div>
              <p class="text-xs text-blue-600 font-medium">Components</p>
              <p class="text-lg font-bold text-blue-700">{stats.totalComponents}</p>
            </div>
          </div>
          
          <div class="bg-red-50 rounded-lg px-4 py-2 flex items-center border border-red-100">
            <Shield size={20} class="text-red-500 mr-2" />
            <div>
              <p class="text-xs text-red-600 font-medium">ASIL D</p>
              <p class="text-lg font-bold text-red-700">{stats.bySafetyLevel['ASIL D']}</p>
            </div>
          </div>
          
          <div class="bg-orange-50 rounded-lg px-4 py-2 flex items-center border border-orange-100">
            <Settings size={20} class="text-orange-500 mr-2" />
            <div>
              <p class="text-xs text-orange-600 font-medium">ECUs</p>
              <p class="text-lg font-bold text-orange-700">{stats.byType.ECU}</p>
            </div>
          </div>
          
          <div class="bg-emerald-50 rounded-lg px-4 py-2 flex items-center border border-emerald-100">
            <AlertTriangle size={20} class="text-emerald-500 mr-2" />
            <div>
              <p class="text-xs text-emerald-600 font-medium">Sensors</p>
              <p class="text-lg font-bold text-emerald-700">{stats.byType.Sensor}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Tab Navigation -->
  <div class="bg-white border-b border-gray-200">
    <div class="container mx-auto max-w-7xl">
      <div class="flex overflow-x-auto">
        <button 
          class="px-4 py-3 font-medium text-sm border-b-2 focus:outline-none whitespace-nowrap {activeTab === 'components' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
          on:click={() => setActiveTab('components')}>
          Components
        </button>
        
        <button 
          class="px-4 py-3 font-medium text-sm border-b-2 focus:outline-none whitespace-nowrap {activeTab === 'analysis' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
          on:click={() => setActiveTab('analysis')}>
          Analysis
        </button>
        
        <button 
          class="px-4 py-3 font-medium text-sm border-b-2 focus:outline-none whitespace-nowrap {activeTab === 'reports' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
          on:click={() => setActiveTab('reports')}>
          Reports
        </button>
        
        <button 
          class="px-4 py-3 font-medium text-sm border-b-2 focus:outline-none whitespace-nowrap {activeTab === 'review' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
          on:click={() => setActiveTab('review')}>
          Risk Review
        </button>
        
        <button 
          class="px-4 py-3 font-medium text-sm border-b-2 focus:outline-none whitespace-nowrap {activeTab === 'settings' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
          on:click={() => setActiveTab('settings')}>
          Settings
        </button>
      </div>
    </div>
  </div>
  
  <!-- Content area -->
  <div class="container mx-auto max-w-7xl py-6">
    {#if activeTab === 'components'}
      <ComponentList on:update={e => handleComponentsUpdate(e.detail)} />
    {:else if activeTab === 'analysis'}
      <div class="p-4 bg-white rounded-lg shadow">
        <div class="flex justify-center items-center h-64">
          <div class="text-center">
            <BarChart size={48} class="mx-auto text-gray-400 mb-4" />
            <h2 class="text-xl font-semibold text-gray-700 mb-2">Analysis Module</h2>
            <p class="text-gray-600">Run security analysis on your components.</p>
            <button class="btn btn-primary mt-4">Start New Analysis</button>
          </div>
        </div>
      </div>
    {:else}
      <div class="p-4 bg-white rounded-lg shadow">
        <div class="flex justify-center items-center h-64">
          <div class="text-center">
            <RefreshCw size={48} class="mx-auto text-gray-400 mb-4" />
            <h2 class="text-xl font-semibold text-gray-700 mb-2">Coming Soon</h2>
            <p class="text-gray-600">This feature is under development.</p>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>
