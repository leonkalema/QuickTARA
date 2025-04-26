<script lang="ts">
  import { onMount } from 'svelte';
  import type { RiskMatrix, RiskMatrixCell } from '../../api/risk';
  
  // Props
  export let riskMatrix: RiskMatrix;
  export let title: string = 'Risk Matrix';
  export let showLabels: boolean = true;
  export let interactive: boolean = false;
  export let selectedCell: RiskMatrixCell | null = null;
  
  // Derived variables
  $: matrix = riskMatrix?.matrix || [];
  $: uniqueImpacts = [...new Set(matrix.map(cell => cell.impact))].sort((a, b) => b - a); // Descending order (5 to 1)
  $: uniqueLikelihoods = [...new Set(matrix.map(cell => cell.likelihood))].sort(); // Ascending order (1 to 5)
  
  // Get risk level class for a cell
  function getRiskLevelClass(level: string): string {
    switch (level.toLowerCase()) {
      case 'low':
        return 'bg-green-200 hover:bg-green-300';
      case 'medium':
        return 'bg-yellow-200 hover:bg-yellow-300';
      case 'high':
        return 'bg-orange-200 hover:bg-orange-300';
      case 'critical':
        return 'bg-red-200 hover:bg-red-300';
      default:
        return 'bg-gray-200 hover:bg-gray-300';
    }
  }
  
  // Get a cell for a specific impact and likelihood
  function getCell(impact: number, likelihood: number): RiskMatrixCell | undefined {
    return matrix.find(cell => cell.impact === impact && cell.likelihood === likelihood);
  }
  
  // Handle cell click when interactive mode is enabled
  function handleCellClick(cell: RiskMatrixCell) {
    if (interactive) {
      selectedCell = cell;
      dispatch('cellSelect', cell);
    }
  }
  
  // Event dispatcher
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
  
  // Impact level labels
  const impactLabels = {
    1: 'Negligible',
    2: 'Minor', 
    3: 'Moderate',
    4: 'Major',
    5: 'Critical'
  };
  
  // Likelihood level labels
  const likelihoodLabels = {
    1: 'Rare',
    2: 'Unlikely',
    3: 'Possible', 
    4: 'Likely',
    5: 'Almost Certain'
  };
</script>

<div class="risk-matrix-container">
  <h3 class="text-lg font-semibold mb-4">{title}</h3>
  
  <div class="risk-matrix relative overflow-x-auto">
    <table class="min-w-full border-collapse">
      <!-- Header with likelihood labels -->
      <thead>
        <tr>
          <th class="border p-2 bg-gray-100">Impact ↓ / Likelihood →</th>
          {#each uniqueLikelihoods as likelihood}
            <th class="border p-2 bg-gray-100 text-center">
              {#if showLabels}
                <div class="text-xs font-normal">{likelihoodLabels[likelihood] || likelihood}</div>
                <div class="font-bold">{likelihood}</div>
              {:else}
                <div class="font-bold">{likelihood}</div>
              {/if}
            </th>
          {/each}
        </tr>
      </thead>
      
      <!-- Matrix body -->
      <tbody>
        {#each uniqueImpacts as impact}
          <tr>
            <!-- Impact label -->
            <td class="border p-2 bg-gray-100 text-center">
              {#if showLabels}
                <div class="text-xs font-normal">{impactLabels[impact] || impact}</div>
                <div class="font-bold">{impact}</div>
              {:else}
                <div class="font-bold">{impact}</div>
              {/if}
            </td>
            
            <!-- Risk cells -->
            {#each uniqueLikelihoods as likelihood}
              {@const cell = getCell(impact, likelihood)}
              {#if cell}
                <td 
                  class="border text-center p-3 cursor-pointer transition-colors {getRiskLevelClass(cell.risk_level)} {selectedCell === cell ? 'ring-2 ring-blue-500' : ''}"
                  on:click={() => handleCellClick(cell)}
                  title="Impact: {impact}, Likelihood: {likelihood}, Risk: {cell.risk_level}, Score: {cell.numerical_score}"
                >
                  <div class="text-sm font-semibold">{cell.numerical_score}</div>
                  <div class="text-xs capitalize">{cell.risk_level}</div>
                </td>
              {:else}
                <td class="border p-3 bg-gray-100"></td>
              {/if}
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
  
  {#if riskMatrix?.description}
    <div class="mt-2 text-sm text-gray-600">{riskMatrix.description}</div>
  {/if}
</div>

<style>
  .risk-matrix-container {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
  }
  
  .risk-matrix table {
    table-layout: fixed;
  }
</style>
