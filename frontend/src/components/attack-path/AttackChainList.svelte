<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { AttackChain, AttackComplexity } from '../../api/attackPath';
  
  export let chains: AttackChain[] = [];
  export let selectedChainId: string | null = null;
  export let complexityColors: Record<string, string> = {};
  
  const dispatch = createEventDispatcher();
  
  function selectChain(chainId: string) {
    dispatch('selectChain', chainId);
  }
  
  // Format risk score with one decimal place
  function formatRiskScore(score: number): string {
    return score.toFixed(1);
  }
</script>

<div class="bg-white rounded-lg shadow-md overflow-hidden">
  <div class="p-4 bg-gray-50 border-b border-gray-200">
    <h2 class="text-lg font-semibold text-gray-700">Attack Chains</h2>
  </div>
  
  {#if chains.length === 0}
    <div class="p-6 text-center">
      <p class="text-gray-500">No attack chains found</p>
    </div>
  {:else}
    <div class="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
      {#each chains as chain}
        <button 
          type="button"
          class="w-full text-left p-4 hover:bg-gray-50 cursor-pointer transition-colors {selectedChainId === chain.chain_id ? 'bg-blue-50' : ''}"
          on:click={() => selectChain(chain.chain_id)}
          on:keydown={(e) => e.key === 'Enter' && selectChain(chain.chain_id)}
        >
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-medium text-gray-900">{chain.name}</h3>
            <span 
              class="text-xs font-medium mr-2 px-2.5 py-0.5 rounded-full {complexityColors[chain.complexity] || 'bg-gray-100 text-gray-800'}"
            >
              {chain.complexity}
            </span>
          </div>
          
          <p class="text-sm text-gray-500 mb-2 line-clamp-2">{chain.description}</p>
          
          <div class="grid grid-cols-2 gap-2 mb-2 text-sm">
            <div class="flex flex-col">
              <span class="text-gray-600">Entry Point:</span>
              <span class="font-medium text-gray-900">{chain.entry_point_id}</span>
            </div>
            <div class="flex flex-col">
              <span class="text-gray-600">Final Target:</span>
              <span class="font-medium text-gray-900">{chain.final_target_id}</span>
            </div>
          </div>
          
          <div class="flex justify-between items-center text-sm">
            <div class="flex items-center">
              <span class="text-gray-600 mr-1">Paths:</span>
              <span class="font-medium text-gray-900">{chain.paths ? chain.paths.length : '0'}</span>
            </div>
            <div class="flex items-center">
              <span class="text-gray-600 mr-1">Total Steps:</span>
              <span class="font-medium text-gray-900">{chain.total_steps}</span>
            </div>
          </div>
          
          <div class="mt-2 flex justify-between items-center">
            <div class="flex items-center text-sm">
              <span class="text-gray-600 mr-1">Risk Score:</span>
              <span class="font-medium {chain.risk_score > 6 ? 'text-red-600' : chain.risk_score > 3 ? 'text-yellow-600' : 'text-green-600'}">
                {formatRiskScore(chain.risk_score)}
              </span>
            </div>
            <div class="flex items-center text-sm">
              <span class="text-gray-600 mr-1">Success Likelihood:</span>
              <span class="font-medium text-gray-900">{(chain.success_likelihood * 100).toFixed(0)}%</span>
            </div>
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>
