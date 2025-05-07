<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { RefreshCw, AlertTriangle, Shield, Activity, Edit, Trash2, Eye } from '@lucide/svelte';
  import type { DamageScenario } from '../../api/damage-scenarios';
  
  // Props
  export let scenarios: DamageScenario[] = [];
  export let totalScenarios: number = 0;
  export let currentPage: number = 1;
  export let pageSize: number = 10;
  export let isLoading: boolean = false;
  export let error: string = '';
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Computed properties
  $: totalPages = Math.ceil(totalScenarios / pageSize);
  $: startItem = (currentPage - 1) * pageSize + 1;
  $: endItem = Math.min(startItem + pageSize - 1, totalScenarios);
  
  // Methods
  function handleEdit(scenario: DamageScenario) {
    dispatch('edit', scenario);
  }
  
  function handleDelete(scenario: DamageScenario) {
    dispatch('delete', scenario);
  }
  
  function handleView(scenario: DamageScenario) {
    dispatch('view', scenario);
  }
  
  function handlePageChange(page: number) {
    if (page < 1 || page > totalPages) return;
    dispatch('pageChange', page);
  }
  
  function getSeverityColor(severity: string): string {
    switch(severity) {
      case 'Critical':
        return 'text-red-600 bg-red-100';
      case 'High':
        return 'text-orange-600 bg-orange-100';
      case 'Medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'Low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }
  
  function getImpactTypeColor(impactType: string): string {
    switch(impactType) {
      case 'Direct':
        return 'text-blue-600 bg-blue-100';
      case 'Indirect':
        return 'text-purple-600 bg-purple-100';
      case 'Cascading':
        return 'text-teal-600 bg-teal-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  }
  
  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleString();
  }
</script>

<div>
  {#if isLoading}
    <div class="flex justify-center items-center h-64">
      <div class="text-center">
        <RefreshCw size={36} class="animate-spin mx-auto text-primary mb-4" />
        <p class="text-gray-600">Loading damage scenarios...</p>
      </div>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <div class="flex">
        <AlertTriangle class="h-5 w-5 text-red-500 mr-2" />
        <p class="text-red-700">{error}</p>
      </div>
    </div>
  {:else if scenarios.length === 0}
    <div class="flex flex-col items-center justify-center h-64 text-center">
      <Shield size={48} class="text-gray-400 mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No damage scenarios found</h3>
      <p class="text-gray-500 mb-4">Create your first damage scenario to start analyzing potential impacts.</p>
    </div>
  {:else}
    <div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Category
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Impact Type
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Severity
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              CIA Impact
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Created
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
                <div class="text-xs text-gray-500 truncate max-w-xs">{scenario.description}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{scenario.damage_category}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getImpactTypeColor(scenario.impact_type)}">
                  {scenario.impact_type}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full {getSeverityColor(scenario.severity)}">
                  {scenario.severity}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex space-x-1">
                  {#if scenario.confidentiality_impact}
                    <span class="px-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">C</span>
                  {/if}
                  {#if scenario.integrity_impact}
                    <span class="px-1 text-xs font-semibold rounded bg-green-100 text-green-800">I</span>
                  {/if}
                  {#if scenario.availability_impact}
                    <span class="px-1 text-xs font-semibold rounded bg-purple-100 text-purple-800">A</span>
                  {/if}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {formatDate(scenario.created_at)}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex space-x-2">
                  <button 
                    on:click={() => handleView(scenario)}
                    class="text-indigo-600 hover:text-indigo-900"
                    title="View details"
                  >
                    <Eye size={16} />
                  </button>
                  <button 
                    on:click={() => handleEdit(scenario)}
                    class="text-blue-600 hover:text-blue-900"
                    title="Edit scenario"
                  >
                    <Edit size={16} />
                  </button>
                  <button 
                    on:click={() => handleDelete(scenario)}
                    class="text-red-600 hover:text-red-900"
                    title="Delete scenario"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      
      <!-- Pagination -->
      {#if totalPages > 1}
        <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              on:click={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              on:click={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Showing <span class="font-medium">{startItem}</span> to <span class="font-medium">{endItem}</span> of <span class="font-medium">{totalScenarios}</span> results
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  on:click={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span class="sr-only">Previous</span>
                  <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
                
                {#each Array(totalPages) as _, i}
                  {#if i + 1 === currentPage || i + 1 === 1 || i + 1 === totalPages || (i + 1 >= currentPage - 1 && i + 1 <= currentPage + 1)}
                    <button
                      on:click={() => handlePageChange(i + 1)}
                      class={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        i + 1 === currentPage
                          ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {i + 1}
                    </button>
                  {:else if i + 1 === currentPage - 2 || i + 1 === currentPage + 2}
                    <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                      ...
                    </span>
                  {/if}
                {/each}
                
                <button
                  on:click={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span class="sr-only">Next</span>
                  <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>
