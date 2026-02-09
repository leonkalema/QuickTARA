<script lang="ts">
  import { ChevronDown, Plus } from '@lucide/svelte';
  import { selectedProduct } from '../../lib/stores/productStore';
  import { goto } from '$app/navigation';

  let showDropdown = false;

  function selectProduct() {
    showDropdown = false;
    goto('/products');
  }

  function manageProducts() {
    showDropdown = false;
    goto('/products');
  }
</script>

<div class="relative">
  {#if $selectedProduct}
    <button
      class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-all focus-ring"
      style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); color: var(--color-text-primary);"
      onclick={() => showDropdown = !showDropdown}
    >
      <div class="w-1.5 h-1.5 rounded-full" style="background: var(--color-accent-primary);"></div>
      <span class="font-medium max-w-[180px] truncate">{$selectedProduct.name}</span>
      <ChevronDown class="w-3.5 h-3.5" style="color: var(--color-text-tertiary);" />
    </button>
  {:else}
    <button
      class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-all focus-ring"
      style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); color: var(--color-text-secondary);"
      onclick={() => showDropdown = !showDropdown}
    >
      <span>Select Product</span>
      <ChevronDown class="w-3.5 h-3.5" style="color: var(--color-text-tertiary);" />
    </button>
  {/if}

  {#if showDropdown}
    <div
      class="absolute top-full left-0 mt-1 w-64 rounded-lg z-50"
      style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); box-shadow: var(--shadow-lg);"
    >
      <div class="p-2">
        {#if $selectedProduct}
          <div class="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider" style="color: var(--color-text-tertiary);">
            Current Product
          </div>
          <div class="px-3 py-2 rounded-md mb-2" style="background: var(--color-info-bg);">
            <div class="font-medium text-sm" style="color: var(--color-text-primary);">{$selectedProduct.name}</div>
            <div class="text-xs" style="color: var(--color-text-secondary);">{$selectedProduct.product_type}</div>
          </div>
        {/if}
        <div class="border-t pt-2" style="border-color: var(--color-border-subtle);">
          <button
            class="w-full flex items-center px-3 py-2 text-sm rounded-md transition-colors"
            style="color: var(--color-text-secondary);"
            onmouseenter={(e) => { e.currentTarget.style.background = 'var(--color-bg-surface-hover)'; e.currentTarget.style.color = 'var(--color-text-primary)'; }}
            onmouseleave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
            onclick={selectProduct}
          >
            <Plus class="w-4 h-4 mr-2" />
            Change Product
          </button>
          <button
            class="w-full flex items-center px-3 py-2 text-sm rounded-md transition-colors"
            style="color: var(--color-text-secondary);"
            onmouseenter={(e) => { e.currentTarget.style.background = 'var(--color-bg-surface-hover)'; e.currentTarget.style.color = 'var(--color-text-primary)'; }}
            onmouseleave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
            onclick={manageProducts}
          >
            Manage Products
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

{#if showDropdown}
  <div
    class="fixed inset-0 z-40"
    onclick={() => showDropdown = false}
    role="presentation"
  ></div>
{/if}
