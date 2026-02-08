<script lang="ts">
  import type { Product } from '$lib/types/product';

  export let products: readonly Product[];
  export let selectedProductId: string | null;
  export let onSelect: (product: Product) => void;

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString();
  };
</script>

<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
  <div class="divide-y divide-gray-200">
    {#each products as product (product.scope_id)}
      <div
        class="p-4 hover:bg-gray-50 cursor-pointer transition-colors {selectedProductId === product.scope_id ? 'bg-slate-50 border-l-4 border-slate-500' : ''}"
        on:click={() => onSelect(product)}
        role="button"
        tabindex="0"
        on:keydown={(e) => e.key === 'Enter' && onSelect(product)}
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4 flex-1">
            <div class="flex-shrink-0">
              <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-3">
                <h3 class="text-lg font-medium text-gray-900 truncate">{product.name}</h3>
                {#if product.version}
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                    v{product.version}
                  </span>
                {/if}
              </div>
              <div class="flex items-center space-x-4 mt-1">
                <span class="text-sm text-gray-500 capitalize">{product.product_type}</span>
                {#if product.owner_team}
                  <span class="text-sm text-gray-500 flex items-center">
                    <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a4 4 0 11-8 0 4 4 0 018 0z"></path>
                    </svg>
                    {product.owner_team}
                  </span>
                {/if}
                <span class="text-sm text-gray-500 flex items-center">
                  <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                  {formatDate(product.created_at)}
                </span>
              </div>
              {#if product.description}
                <p class="text-sm text-gray-600 mt-2 line-clamp-2">{product.description}</p>
              {/if}
            </div>
          </div>
          <div class="flex items-center space-x-3">
            {#if product.status}
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {product.status === 'production' ? 'bg-green-100 text-green-800' : product.status === 'testing' ? 'bg-yellow-100 text-yellow-800' : product.status === 'development' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'}"
              >
                {product.status}
              </span>
            {/if}
            {#if selectedProductId === product.scope_id}
              <div class="w-3 h-3 bg-slate-600 rounded-full"></div>
            {/if}
          </div>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
