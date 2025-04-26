<script lang="ts">
  import { onMount } from 'svelte';
  import ThreatCatalogManager from './ThreatCatalogManager.svelte';
  import ThreatAnalysisVisualizer from './ThreatAnalysisVisualizer.svelte';
  
  // Tab management
  let activeTab = 'catalog'; // 'catalog' or 'analysis'
  let selectedComponentIds: string[] = [];
  
  function setActiveTab(tab: string) {
    activeTab = tab;
  }
</script>

<div class="container mx-auto px-4 py-6">
  <h1 class="text-3xl font-semibold mb-6">STRIDE Threat Identification</h1>
  
  <!-- Tab Navigation -->
  <div class="flex border-b mb-6">
    <button 
      class="py-2 px-4 font-medium text-sm {activeTab === 'catalog' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}"
      on:click={() => setActiveTab('catalog')}
    >
      <div class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
        </svg>
        Threat Catalog
      </div>
    </button>
    <button 
      class="py-2 px-4 font-medium text-sm {activeTab === 'analysis' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}"
      on:click={() => setActiveTab('analysis')}
    >
      <div class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 0l-2 2a1 1 0 101.414 1.414L8 10.414l1.293 1.293a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
        </svg>
        Threat Analysis
      </div>
    </button>
  </div>
  
  <!-- Tab Content -->
  <div>
    {#if activeTab === 'catalog'}
      <ThreatCatalogManager />
    {:else if activeTab === 'analysis'}
      <ThreatAnalysisVisualizer bind:selectedComponentIds={selectedComponentIds} />
    {/if}
  </div>
</div>
