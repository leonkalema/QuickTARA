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

<div class="rounded-lg overflow-hidden" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
  <div>
    {#each products as product (product.scope_id)}
      <div
        class="p-4 cursor-pointer transition-colors" style="border-bottom: 1px solid var(--color-border-subtle); {selectedProductId === product.scope_id ? 'background: var(--color-bg-elevated); border-left: 3px solid var(--color-accent-primary);' : ''}"
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
                <h3 class="text-sm font-medium truncate" style="color: var(--color-text-primary);">{product.name}</h3>
                {#if product.version}
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium" style="background: var(--color-bg-elevated); color: var(--color-text-secondary);">
                    v{product.version}
                  </span>
                {/if}
              </div>
              <div class="flex items-center space-x-4 mt-1">
                <span class="text-xs capitalize" style="color: var(--color-text-tertiary);">{product.product_type}</span>
                {#if product.owner_team}
                  <span class="text-xs flex items-center" style="color: var(--color-text-tertiary);">
                    <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a4 4 0 11-8 0 4 4 0 018 0z"></path>
                    </svg>
                    {product.owner_team}
                  </span>
                {/if}
                <span class="text-xs flex items-center" style="color: var(--color-text-tertiary);">
                  <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                  {formatDate(product.created_at)}
                </span>
              </div>
              {#if product.description}
                <p class="text-xs mt-1 line-clamp-2" style="color: var(--color-text-tertiary);">{product.description}</p>
              {/if}
            </div>
          </div>
          <div class="flex items-center space-x-3">
            {#if product.status}
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium" style="{product.status === 'production' ? 'background: var(--color-success-bg); color: var(--color-success);' : product.status === 'testing' ? 'background: var(--color-warning-bg); color: var(--color-warning);' : product.status === 'development' ? 'background: var(--color-info-bg); color: var(--color-info);' : 'background: var(--color-error-bg); color: var(--color-error);'}"
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
