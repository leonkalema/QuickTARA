<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { goto } from '$app/navigation';
  import { MoreVertical, Edit, Trash2 } from '@lucide/svelte';
  import type { Product } from '../../../lib/types/product';

  export let product: Product;
  export let isSelected: boolean = false;

  const dispatch = createEventDispatcher();

  let showMenu = false;
  let isDeleting = false;

  function handleSelect() {
    dispatch('select');
    // Navigate to product detail page
    goto(`/products/${product.scope_id}`);
  }

  function handleEdit() {
    dispatch('edit', product);
    showMenu = false;
  }

  function handleDelete() {
    dispatch('delete', product);
    showMenu = false;
  }

  function getStatusColor(status: string) {
    switch (status) {
      case 'production': return 'bg-green-100 text-green-800';
      case 'testing': return 'bg-yellow-100 text-yellow-800';
      case 'development': return 'bg-blue-100 text-blue-800';
      case 'deprecated': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }

  function getTypeIcon(type: string) {
    switch (type) {
      case 'automotive': return '🚗';
      case 'industrial': return '🏭';
      case 'iot': return '📡';
      case 'medical': return '🏥';
      case 'aerospace': return '✈️';
      default: return '📦';
    }
  }

  function formatDate(dateString?: string) {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString();
  }
</script>

<div 
  class="bg-white rounded-lg border border-gray-200 hover:border-slate-300 transition-all duration-200 cursor-pointer group relative {isSelected ? 'ring-2 ring-slate-500 border-slate-500' : ''}"
  on:click={handleSelect}
  role="button"
  tabindex="0"
  on:keydown={(e) => e.key === 'Enter' && handleSelect()}
>
  <!-- Card Header -->
  <div class="p-4 border-b border-gray-100">
    <div class="flex items-start justify-between">
      <div class="flex items-center space-x-3">
        <div class="text-2xl">{getTypeIcon(product.product_type)}</div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 group-hover:text-slate-700">
            {product.name}
          </h3>
          <p class="text-sm text-gray-500 capitalize">
            {product.product_type} • v{product.version}
          </p>
        </div>
      </div>

      <!-- Status Badge -->
      <div class="flex items-center">
        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(product.status)}">
          {product.status}
        </span>
      </div>
    </div>
  </div>

  <!-- Card Body -->
  <div class="p-4 space-y-3">
    <!-- Description -->
    {#if product.description}
      <p class="text-sm text-gray-600 line-clamp-2">
        {product.description}
      </p>
    {/if}

    <!-- Team -->
    {#if product.owner_team}
      <div class="flex items-center">
        <span class="text-xs text-gray-500">
          Team: {product.owner_team}
        </span>
      </div>
    {/if}

    <!-- Compliance Standards -->
    {#if product.compliance_standards && product.compliance_standards.length > 0}
      <div class="flex flex-wrap gap-1">
        {#each product.compliance_standards.slice(0, 3) as standard}
          <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-slate-100 text-slate-700">
            {standard}
          </span>
        {/each}
        {#if product.compliance_standards.length > 3}
          <span class="text-xs text-gray-500">
            +{product.compliance_standards.length - 3} more
          </span>
        {/if}
      </div>
    {/if}

    <!-- Footer -->
    <div class="text-xs text-gray-400 pt-2 border-t border-gray-100">
      Created: {formatDate(product.created_at)}
    </div>
  </div>

  <!-- Selected Indicator -->
  {#if isSelected}
    <div class="absolute top-3 right-3">
      <div class="w-3 h-3 bg-slate-600 rounded-full"></div>
    </div>
  {/if}
</div>

<!-- Click outside to close menu -->
{#if showMenu}
  <div 
    class="fixed inset-0 z-0" 
    on:click={() => showMenu = false}
    role="button"
    tabindex="-1"
  ></div>
{/if}
