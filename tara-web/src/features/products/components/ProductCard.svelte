<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { MoreVertical, Edit, Trash2 } from '@lucide/svelte';
  import type { Product, ProductPermissions } from '../../../lib/types/product';
  import { productPermissions } from '../../../lib/stores/productPermissions';

  export let product: Product;
  export let isSelected: boolean = false;

  const dispatch = createEventDispatcher();

  let showMenu = false;
  let isDeleting = false;
  let permissions: ProductPermissions | null = null;

  onMount(async () => {
    permissions = await productPermissions.fetchPermissions(product.scope_id);
  });

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

  function getStatusStyle(status: string): { bg: string; fg: string } {
    switch (status) {
      case 'production': return { bg: 'var(--color-success-bg)', fg: 'var(--color-success)' };
      case 'testing': return { bg: 'var(--color-warning-bg)', fg: 'var(--color-warning)' };
      case 'development': return { bg: 'var(--color-info-bg)', fg: 'var(--color-info)' };
      case 'deprecated': return { bg: 'var(--color-error-bg)', fg: 'var(--color-error)' };
      default: return { bg: 'var(--color-bg-elevated)', fg: 'var(--color-text-tertiary)' };
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

  function formatDate(dateString?: string): string {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString();
  }

  $: ss = getStatusStyle(product.status ?? 'development');
</script>
<div 
  class="rounded-lg transition-all duration-200 cursor-pointer group relative"
  style="background: var(--color-bg-surface); border: 1px solid {isSelected ? 'var(--color-accent-primary)' : 'var(--color-border-default)'};"
  on:click={handleSelect}
  role="button"
  tabindex="0"
  on:keydown={(e) => e.key === 'Enter' && handleSelect()}
>
  <div class="p-4" style="border-bottom: 1px solid var(--color-border-subtle);">
    <div class="flex items-start justify-between">
      <div class="flex items-center space-x-3">
        <div class="text-xl">{getTypeIcon(product.product_type)}</div>
        <div>
          <h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">
            {product.name}
          </h3>
          <p class="text-xs capitalize" style="color: var(--color-text-tertiary);">
            {product.product_type} · v{product.version}
          </p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="px-2 py-0.5 rounded-full text-[10px] font-medium" style="background: {ss.bg}; color: {ss.fg};">
          {product.status}
        </span>
        {#if permissions?.can_edit || permissions?.can_delete}
          <div class="relative">
            <button
              class="p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity"
              style="color: var(--color-text-tertiary);"
              on:click|stopPropagation={() => showMenu = !showMenu}
              aria-label="Product actions"
            >
              <MoreVertical class="w-4 h-4" />
            </button>
            {#if showMenu}
              <div class="absolute right-0 mt-1 w-36 rounded-md z-10" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); box-shadow: var(--shadow-lg);">
                {#if permissions?.can_edit}
                  <button class="w-full px-3 py-2 text-left text-xs flex items-center space-x-2 transition-colors" style="color: var(--color-text-secondary);" on:click|stopPropagation={handleEdit}>
                    <Edit class="w-3.5 h-3.5" /><span>Edit</span>
                  </button>
                {/if}
                {#if permissions?.can_delete}
                  <button class="w-full px-3 py-2 text-left text-xs flex items-center space-x-2 transition-colors" style="color: var(--color-error);" on:click|stopPropagation={handleDelete}>
                    <Trash2 class="w-3.5 h-3.5" /><span>Delete</span>
                  </button>
                {/if}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>

  <div class="p-4 space-y-2.5">
    {#if product.description}
      <p class="text-xs line-clamp-2" style="color: var(--color-text-secondary);">{product.description}</p>
    {/if}
    {#if product.owner_team}
      <span class="text-[11px]" style="color: var(--color-text-tertiary);">Team: {product.owner_team}</span>
    {/if}
    {#if product.compliance_standards && product.compliance_standards.length > 0}
      <div class="flex flex-wrap gap-1">
        {#each product.compliance_standards.slice(0, 3) as standard}
          <span class="px-1.5 py-0.5 rounded text-[10px] font-medium" style="background: var(--color-bg-elevated); color: var(--color-text-tertiary);">{standard}</span>
        {/each}
        {#if product.compliance_standards.length > 3}
          <span class="text-[10px]" style="color: var(--color-text-tertiary);">+{product.compliance_standards.length - 3} more</span>
        {/if}
      </div>
    {/if}
    <div class="text-[11px] pt-2" style="border-top: 1px solid var(--color-border-subtle); color: var(--color-text-tertiary);">
      Created: {formatDate(product.created_at)}
    </div>
  </div>

  {#if isSelected}
    <div class="absolute top-3 right-3">
      <div class="w-2.5 h-2.5 rounded-full" style="background: var(--color-accent-primary);"></div>
    </div>
  {/if}
</div>

<!-- Click outside to close menu -->
{#if showMenu}
  <button 
    class="fixed inset-0 z-0 cursor-default" 
    on:click={() => showMenu = false}
    aria-label="Close menu"
  ></button>
{/if}
