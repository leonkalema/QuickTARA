<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Edit } from '@lucide/svelte';
  import type { DamageScenario } from '../../api/damage-scenarios';
  
  export let scenarios: DamageScenario[] = [];
  
  const dispatch = createEventDispatcher();
  
  function getImpactColor(level: string | null): string {
    switch(level) {
      case 'Critical':
        return 'bg-red-100 text-red-800';
      case 'High':
        return 'bg-orange-100 text-orange-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }
  
  function handleEdit(scenario: DamageScenario): void {
    dispatch('edit', scenario);
  }
</script>

<div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
  <table class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Scenario
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Safety
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Financial
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Operational
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Privacy
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Auto-generated
        </th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
          Actions
        </th>
      </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200">
      {#each scenarios as scenario}
        <tr class="hover:bg-gray-50">
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm font-medium text-gray-900">{scenario.name}</div>
            <div class="text-xs text-gray-500">{scenario.scenario_id}</div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            {#if scenario.safety_impact}
              <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getImpactColor(scenario.safety_impact)}`}>
                {scenario.safety_impact}
              </span>
            {:else}
              <span class="text-gray-400">—</span>
            {/if}
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            {#if scenario.financial_impact}
              <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getImpactColor(scenario.financial_impact)}`}>
                {scenario.financial_impact}
              </span>
            {:else}
              <span class="text-gray-400">—</span>
            {/if}
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            {#if scenario.operational_impact}
              <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getImpactColor(scenario.operational_impact)}`}>
                {scenario.operational_impact}
              </span>
            {:else}
              <span class="text-gray-400">—</span>
            {/if}
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            {#if scenario.privacy_impact}
              <span class={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getImpactColor(scenario.privacy_impact)}`}>
                {scenario.privacy_impact}
              </span>
            {:else}
              <span class="text-gray-400">—</span>
            {/if}
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            {#if scenario.sfop_rating_auto_generated}
              <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                Auto
              </span>
            {:else}
              <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                Manual
              </span>
            {/if}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
            <button 
              on:click={() => handleEdit(scenario)}
              class="text-indigo-600 hover:text-indigo-900 flex items-center gap-1"
            >
              <Edit size={16} />
              <span>Edit</span>
            </button>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
