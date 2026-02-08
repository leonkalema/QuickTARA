<script lang="ts">
  import { User } from '@lucide/svelte';
  import type { Product } from '$lib/types/product';

  export let product: Product;
</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <div class="bg-white rounded-lg border border-gray-200 p-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Technical Details</h2>
    <div class="space-y-4">
      <div>
        <div class="block text-sm font-medium text-gray-700 mb-1">Product ID</div>
        <p class="text-sm text-gray-900 font-mono bg-gray-50 px-2 py-1 rounded">{product.scope_id}</p>
      </div>
      <div>
        <div class="block text-sm font-medium text-gray-700 mb-1">Trust Zone</div>
        <p class="text-sm text-gray-900">{product.trust_zone || 'Standard'}</p>
      </div>
      <div>
        <div class="block text-sm font-medium text-gray-700 mb-1">Version</div>
        <p class="text-sm text-gray-900">{product.version || 1}</p>
      </div>
    </div>
  </div>

  <div class="bg-white rounded-lg border border-gray-200 p-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Configuration</h2>
    <div class="space-y-4">
      <div>
        <div class="block text-sm font-medium text-gray-700 mb-2">Interfaces</div>
        {#if product.interfaces && product.interfaces.length > 0}
          <div class="flex flex-wrap gap-2">
            {#each product.interfaces as productInterface}
              <span class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">{productInterface}</span>
            {/each}
          </div>
        {:else}
          <p class="text-sm text-gray-500">No interfaces defined</p>
        {/if}
      </div>
      <div>
        <div class="block text-sm font-medium text-gray-700 mb-2">Access Points</div>
        {#if product.access_points && product.access_points.length > 0}
          <div class="flex flex-wrap gap-2">
            {#each product.access_points as point}
              <span class="px-2 py-1 bg-green-50 text-green-700 text-xs rounded">{point}</span>
            {/each}
          </div>
        {:else}
          <p class="text-sm text-gray-500">No access points defined</p>
        {/if}
      </div>
    </div>
  </div>

  <div class="bg-white rounded-lg border border-gray-200 p-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Analysis Scope</h2>
    <div class="space-y-4">
      <div>
        <div class="block text-sm font-medium text-gray-700 mb-2">Boundaries</div>
        {#if product.boundaries && product.boundaries.length > 0}
          <ul class="text-sm text-gray-900 space-y-1">
            {#each product.boundaries as boundary}
              <li class="flex items-start">
                <span class="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                {boundary}
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-gray-500">No boundaries defined</p>
        {/if}
      </div>
      <div>
        <div class="block text-sm font-medium text-gray-700 mb-2">Objectives</div>
        {#if product.objectives && product.objectives.length > 0}
          <ul class="text-sm text-gray-900 space-y-1">
            {#each product.objectives as objective}
              <li class="flex items-start">
                <span class="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                {objective}
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-sm text-gray-500">No objectives defined</p>
        {/if}
      </div>
    </div>
  </div>

  <div class="bg-white rounded-lg border border-gray-200 p-6">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Stakeholders</h2>
    {#if product.stakeholders && product.stakeholders.length > 0}
      <div class="space-y-2">
        {#each product.stakeholders as stakeholder}
          <div class="flex items-center">
            <User class="w-4 h-4 text-gray-400 mr-2" />
            <span class="text-sm text-gray-900">{stakeholder}</span>
          </div>
        {/each}
      </div>
    {:else}
      <p class="text-sm text-gray-500">No stakeholders defined</p>
    {/if}
  </div>
</div>
