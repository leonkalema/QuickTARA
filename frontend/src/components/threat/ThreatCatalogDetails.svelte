<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { onMount } from 'svelte';
  import { 
    getThreatCatalogItem,
    StrideCategory,
    type ThreatCatalogItem,
  } from '../../api/threat';
  import { showNotification } from '../../stores/notification';
  import Spinner from '../ui/Spinner.svelte';
  
  export let threatId: string;
  
  const dispatch = createEventDispatcher();
  
  let threat: ThreatCatalogItem | null = null;
  let loading = true;
  let error = '';
  
  // STRIDE category display names
  const strideCategoryNames = {
    [StrideCategory.SPOOFING]: 'Spoofing',
    [StrideCategory.TAMPERING]: 'Tampering',
    [StrideCategory.REPUDIATION]: 'Repudiation',
    [StrideCategory.INFO_DISCLOSURE]: 'Information Disclosure',
    [StrideCategory.DENIAL_OF_SERVICE]: 'Denial of Service',
    [StrideCategory.ELEVATION]: 'Elevation of Privilege'
  };
  
  // Format date function
  function formatDate(dateStr: string): string {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString();
    } catch (e) {
      return dateStr;
    }
  }
  
  // Handle edit button click
  function handleEdit() {
    dispatch('edit', threatId);
  }
  
  // Handle close button click
  function handleClose() {
    dispatch('close');
  }
  
  // Load threat data
  async function loadThreatData() {
    loading = true;
    error = '';
    
    try {
      threat = await getThreatCatalogItem(threatId);
    } catch (err) {
      console.error('Error loading threat details:', err);
      error = 'Failed to load threat details';
      showNotification('Failed to load threat details', 'error');
    } finally {
      loading = false;
    }
  }
  
  onMount(() => {
    loadThreatData();
  });
</script>

<div class="p-4">
  {#if loading}
    <div class="flex justify-center py-8">
      <Spinner size="lg" />
    </div>
  {:else if error}
    <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline"> {error}</span>
    </div>
  {:else if threat}
    <div class="max-h-[70vh] overflow-y-auto pr-2">
      <!-- Header -->
      <div class="mb-6 pb-4 border-b">
        <h2 class="text-2xl font-semibold">{threat.title}</h2>
        <div class="flex flex-wrap items-center mt-2 gap-2">
          <span class="px-3 py-1 rounded-full text-sm font-semibold 
            {threat.stride_category === StrideCategory.SPOOFING ? 'bg-purple-100 text-purple-800' : 
             threat.stride_category === StrideCategory.TAMPERING ? 'bg-yellow-100 text-yellow-800' : 
             threat.stride_category === StrideCategory.REPUDIATION ? 'bg-blue-100 text-blue-800' : 
             threat.stride_category === StrideCategory.INFO_DISCLOSURE ? 'bg-green-100 text-green-800' : 
             threat.stride_category === StrideCategory.DENIAL_OF_SERVICE ? 'bg-red-100 text-red-800' : 
             'bg-orange-100 text-orange-800'}">
            {strideCategoryNames[threat.stride_category]}
          </span>
          
          <div class="flex items-center">
            <span class="text-sm font-medium text-gray-700">Risk Rating:</span>
            <div class="ml-2 flex items-center">
              <span class="mr-1 text-sm font-semibold
                {threat.typical_likelihood * threat.typical_severity <= 6 ? 'text-green-600' : 
                 threat.typical_likelihood * threat.typical_severity <= 15 ? 'text-yellow-600' : 
                 'text-red-600'}">
                {threat.typical_likelihood * threat.typical_severity}
              </span>
              <span class="text-xs text-gray-500">({threat.typical_likelihood} × {threat.typical_severity})</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Description -->
      <div class="mb-6">
        <h3 class="text-lg font-medium mb-2">Description</h3>
        <p class="text-gray-700">{threat.description}</p>
      </div>
      
      <!-- Applicability -->
      <div class="mb-6">
        <h3 class="text-lg font-medium mb-2">Applicability</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h4 class="text-sm font-semibold text-gray-700 mb-1">Component Types</h4>
            <div class="flex flex-wrap gap-1">
              {#each threat.applicable_component_types as type}
                <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-md">{type}</span>
              {/each}
            </div>
          </div>
          
          <div>
            <h4 class="text-sm font-semibold text-gray-700 mb-1">Trust Zones</h4>
            <div class="flex flex-wrap gap-1">
              {#each threat.applicable_trust_zones as zone}
                <span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-md">{zone}</span>
              {/each}
            </div>
          </div>
          
          <div>
            <h4 class="text-sm font-semibold text-gray-700 mb-1">Attack Vectors</h4>
            <div class="flex flex-wrap gap-1">
              {#each threat.attack_vectors as vector}
                <span class="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-md">{vector}</span>
              {/each}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Risk Assessment -->
      <div class="mb-6">
        <h3 class="text-lg font-medium mb-2">Risk Assessment</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 class="text-sm font-semibold text-gray-700 mb-1">Likelihood Rating: {threat.typical_likelihood}/5</h4>
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div class="bg-blue-600 h-2.5 rounded-full" style="width: {(threat.typical_likelihood / 5) * 100}%"></div>
            </div>
          </div>
          
          <div>
            <h4 class="text-sm font-semibold text-gray-700 mb-1">Severity Rating: {threat.typical_severity}/5</h4>
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div class="bg-red-600 h-2.5 rounded-full" style="width: {(threat.typical_severity / 5) * 100}%"></div>
            </div>
          </div>
        </div>
        
        {#if threat.prerequisites && threat.prerequisites.length > 0}
          <div class="mt-3">
            <h4 class="text-sm font-semibold text-gray-700 mb-1">Prerequisites</h4>
            <ul class="list-disc pl-5 text-gray-700">
              {#each threat.prerequisites as prerequisite}
                <li>{prerequisite}</li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
      
      <!-- Mitigation Strategies -->
      {#if threat.mitigation_strategies && threat.mitigation_strategies.length > 0}
        <div class="mb-6">
          <h3 class="text-lg font-medium mb-2">Mitigation Strategies</h3>
          
          {#each threat.mitigation_strategies as strategy, index}
            <div class="border rounded-md p-4 mb-3 {index % 2 === 0 ? 'bg-gray-50' : ''}">
              <h4 class="font-semibold">{strategy.title}</h4>
              <p class="text-gray-700 mt-1">{strategy.description}</p>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                <div>
                  <span class="text-sm text-gray-500">Effectiveness:</span>
                  <div class="flex items-center mt-1">
                    <div class="w-24 bg-gray-200 rounded-full h-1.5 mr-2">
                      <div class="bg-green-600 h-1.5 rounded-full" style="width: {(strategy.effectiveness / 5) * 100}%"></div>
                    </div>
                    <span class="text-sm font-medium">{strategy.effectiveness}/5</span>
                  </div>
                </div>
                
                <div>
                  <span class="text-sm text-gray-500">Implementation Complexity:</span>
                  <div class="flex items-center mt-1">
                    <div class="w-24 bg-gray-200 rounded-full h-1.5 mr-2">
                      <div class="bg-yellow-600 h-1.5 rounded-full" style="width: {(strategy.implementation_complexity / 5) * 100}%"></div>
                    </div>
                    <span class="text-sm font-medium">{strategy.implementation_complexity}/5</span>
                  </div>
                </div>
              </div>
              
              {#if strategy.references && strategy.references.length > 0}
                <div class="mt-2">
                  <span class="text-sm text-gray-500">References:</span>
                  <div class="flex flex-wrap gap-1 mt-1">
                    {#each strategy.references as reference}
                      <span class="px-2 py-0.5 bg-gray-100 text-gray-800 text-xs rounded-md">{reference}</span>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
      
      <!-- Additional Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {#if threat.cwe_ids && threat.cwe_ids.length > 0}
          <div>
            <h4 class="text-sm font-semibold text-gray-700 mb-1">CWE IDs</h4>
            <div class="flex flex-wrap gap-1">
              {#each threat.cwe_ids as cwe}
                <a 
                  href={`https://cwe.mitre.org/data/definitions/${cwe.replace('CWE-', '')}.html`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-md hover:bg-indigo-200"
                >
                  {cwe}
                </a>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if threat.capec_ids && threat.capec_ids.length > 0}
          <div>
            <h4 class="text-sm font-semibold text-gray-700 mb-1">CAPEC IDs</h4>
            <div class="flex flex-wrap gap-1">
              {#each threat.capec_ids as capec}
                <a 
                  href={`https://capec.mitre.org/data/definitions/${capec.replace('CAPEC-', '')}.html`} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="px-2 py-1 bg-violet-100 text-violet-800 text-xs rounded-md hover:bg-violet-200"
                >
                  {capec}
                </a>
              {/each}
            </div>
          </div>
        {/if}
      </div>
      
      {#if threat.examples && threat.examples.length > 0}
        <div class="mb-6">
          <h4 class="text-sm font-semibold text-gray-700 mb-1">Examples</h4>
          <ul class="list-disc pl-5 text-gray-700">
            {#each threat.examples as example}
              <li>{example}</li>
            {/each}
          </ul>
        </div>
      {/if}
      
      <!-- Metadata -->
      <div class="text-xs text-gray-500 mt-6 pt-4 border-t flex flex-wrap justify-between">
        <div>
          <span>Created: {formatDate(threat.created_at)}</span>
          <span class="mx-2">|</span>
          <span>Updated: {formatDate(threat.updated_at)}</span>
        </div>
        <div>
          <span>ID: {threat.id}</span>
        </div>
      </div>
    </div>
    
    <!-- Action Buttons -->
    <div class="flex justify-end space-x-3 mt-6 pt-4 border-t">
      <button 
        type="button"
        on:click={handleEdit}
        class="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-md flex items-center"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
        </svg>
        Edit
      </button>
      <button 
        type="button"
        on:click={handleClose}
        class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md"
      >
        Close
      </button>
    </div>
  {:else}
    <div class="p-8 text-center text-gray-500">
      No threat data found
    </div>
  {/if}
</div>
