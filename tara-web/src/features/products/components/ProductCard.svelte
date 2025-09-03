<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { Product } from '../../../lib/types/product';
  import { productApi } from '../../../lib/api/productApi';

  export let product: Product;
  export let isSelected: boolean = false;

  const dispatch = createEventDispatcher();

  let showMenu = false;
  let isDeleting = false;

  function handleSelect() {
    dispatch('select');
  }

  function handleEdit() {
    // TODO: Implement edit functionality
    showMenu = false;
  }

  async function handleDelete() {
    if (!confirm(`Are you sure you want to delete "${product.name}"? This action cannot be undone.`)) {
      return;
    }

    isDeleting = true;
    try {
      await productApi.delete(product.scope_id);
      dispatch('deleted');
    } catch (error) {
      console.error('Failed to delete product:', error);
      alert('Failed to delete product. Please try again.');
    } finally {
      isDeleting = false;
      showMenu = false;
    }
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

      <!-- Actions Menu -->
      <div class="relative">
        <button
          class="opacity-0 group-hover:opacity-100 p-1 rounded-md hover:bg-gray-100 transition-opacity"
          on:click|stopPropagation={() => showMenu = !showMenu}
        >
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
          </svg>
        </button>

        {#if showMenu}
          <div class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-10">
            <div class="py-1">
              <button
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                on:click|stopPropagation={handleEdit}
              >
                Edit Product
              </button>
              <button
                class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                on:click|stopPropagation={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Deleting...' : 'Delete Product'}
              </button>
            </div>
          </div>
        {/if}
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

    <!-- Status and Team -->
    <div class="flex items-center justify-between">
      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(product.status)}">
        {product.status}
      </span>
      
      {#if product.owner_team}
        <span class="text-xs text-gray-500">
          Team: {product.owner_team}
        </span>
      {/if}
    </div>

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
