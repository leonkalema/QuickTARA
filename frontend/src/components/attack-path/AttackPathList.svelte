<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { AttackPath, AttackPathType, AttackComplexity } from '../../api/attackPath';
  
  export let paths: AttackPath[] = [];
  export let selectedPathId: string | null = null;
  export let complexityColors: Record<string, string> = {};
  export let pathTypeNames: Record<string, string> = {};
  
  const dispatch = createEventDispatcher();
  
  function selectPath(pathId: string) {
    dispatch('selectPath', pathId);
  }
  
  // Format risk score with one decimal place
  function formatRiskScore(score: number): string {
    return score.toFixed(1);
  }
</script>

<div class="bg-white rounded-lg shadow-md overflow-hidden">
  <div class="p-4 bg-gray-50 border-b border-gray-200">
    <h2 class="text-lg font-semibold text-gray-700">Attack Paths</h2>
  </div>
  
  {#if paths.length === 0}
    <div class="p-6 text-center">
      <p class="text-gray-500">No attack paths found</p>
    </div>
  {:else}
    <div class="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
      {#each paths as path}
        <button 
          type="button"
          class="w-full text-left p-4 hover:bg-gray-50 cursor-pointer transition-colors {selectedPathId === path.path_id ? 'bg-blue-50' : ''}"
          on:click={() => selectPath(path.path_id)}
          on:keydown={(e) => e.key === 'Enter' && selectPath(path.path_id)}
        >
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-medium text-gray-900">{path.name}</h3>
            <span 
              class="text-xs font-medium mr-2 px-2.5 py-0.5 rounded-full {complexityColors[path.complexity] || 'bg-gray-100 text-gray-800'}"
            >
              {path.complexity}
            </span>
          </div>
          
          <div class="flex items-center text-sm text-gray-500 mb-2">
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>{pathTypeNames[path.path_type] || path.path_type}</span>
          </div>
          
          <div class="grid grid-cols-2 gap-2 mb-2 text-sm">
            <div class="flex items-center">
              <span class="text-gray-600 mr-1">From:</span>
              <span class="font-medium text-gray-900">{path.entry_point_id}</span>
            </div>
            <div class="flex items-center">
              <span class="text-gray-600 mr-1">To:</span>
              <span class="font-medium text-gray-900">{path.target_id}</span>
            </div>
          </div>
          
          <div class="flex justify-between items-center text-sm">
            <div class="flex items-center">
              <span class="text-gray-600 mr-1">Steps:</span>
              <span class="font-medium text-gray-900">{path.steps.length}</span>
            </div>
            <div class="flex items-center">
              <span class="text-gray-600 mr-1">Risk Score:</span>
              <span class="font-medium {path.risk_score > 6 ? 'text-red-600' : path.risk_score > 3 ? 'text-yellow-600' : 'text-green-600'}">
                {formatRiskScore(path.risk_score)}
              </span>
            </div>
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>
