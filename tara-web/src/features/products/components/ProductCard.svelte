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
      case 'production': return { bg: 'rgba(52,211,153,0.12)', fg: '#34d399' };
      case 'active':     return { bg: 'rgba(52,211,153,0.12)', fg: '#34d399' };
      case 'testing':    return { bg: 'rgba(251,191,36,0.12)',  fg: '#fbbf24' };
      case 'development':return { bg: 'rgba(79,143,247,0.12)',  fg: '#4f8ff7' };
      case 'deprecated': return { bg: 'rgba(248,113,113,0.12)', fg: '#f87171' };
      default:           return { bg: 'rgba(148,163,184,0.12)', fg: '#94a3b8' };
    }
  }

  function getTypeIcon(type: string): string {
    switch (type) {
      case 'automotive':  return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0"/>`;
      case 'industrial':  return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>`;
      case 'iot':         return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"/>`;
      case 'medical':     return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>`;
      case 'aerospace':   return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>`;
      default:            return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>`;
    }
  }

  function formatDate(dateString?: string): string {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString();
  }

  $: ss = getStatusStyle(product.status ?? 'development');
</script>
<div class="flex rounded-xl overflow-hidden border transition-all duration-200 cursor-pointer group"
  style="background: var(--color-bg-surface); border-color: {isSelected ? 'var(--color-accent-primary)' : 'var(--color-border-default)'};"
  role="button"
  tabindex="0"
  aria-label="Open TARA for {product.name}"
  on:click={handleSelect}
  on:keydown={(e) => e.key === 'Enter' && handleSelect()}
  on:mouseenter={(e) => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--color-border-focus)'; e.currentTarget.style.background = 'var(--color-bg-elevated)'; }}
  on:mouseleave={(e) => { if (!isSelected) e.currentTarget.style.borderColor = 'var(--color-border-default)'; e.currentTarget.style.background = 'var(--color-bg-surface)'; }}
>
  <!-- Left status stripe -->
  <div class="w-1 flex-shrink-0" style="background: {ss.fg};"></div>

  <div class="flex-1 p-4">
    <!-- Header -->
    <div class="flex items-start justify-between gap-2 mb-3">
      <div class="flex items-center gap-3 min-w-0">
        <!-- SVG icon box -->
        <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
          style="background: {ss.bg};">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="{ss.fg}">{@html getTypeIcon(product.product_type)}</svg>
        </div>
        <div class="min-w-0">
          <h3 class="text-sm font-semibold leading-tight truncate" style="color: var(--color-text-primary);">
            {product.name}
          </h3>
          <p class="text-[11px] capitalize mt-0.5" style="color: var(--color-text-tertiary);">
            {product.product_type} · v{product.version}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-1.5 flex-shrink-0">
        <span class="px-2 py-0.5 rounded text-[10px] font-semibold capitalize"
          style="background: {ss.bg}; color: {ss.fg};">
          {product.status ?? 'development'}
        </span>
        {#if permissions?.can_edit || permissions?.can_delete}
          <div class="relative">
            <button
              class="p-1 rounded transition-colors"
              style="color: var(--color-text-tertiary);"
              on:click|stopPropagation={() => showMenu = !showMenu}
              aria-label="Product actions"
            >
              <MoreVertical class="w-4 h-4" />
            </button>
            {#if showMenu}
              <div class="absolute right-0 mt-1 w-36 rounded-md z-10"
                style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); box-shadow: var(--shadow-lg);">
                {#if permissions?.can_edit}
                  <button class="w-full px-3 py-2 text-left text-xs flex items-center gap-2 transition-colors"
                    style="color: var(--color-text-secondary);"
                    on:click|stopPropagation={handleEdit}>
                    <Edit class="w-3.5 h-3.5" /><span>Edit</span>
                  </button>
                {/if}
                {#if permissions?.can_delete}
                  <button class="w-full px-3 py-2 text-left text-xs flex items-center gap-2 transition-colors"
                    style="color: var(--color-status-error);"
                    on:click|stopPropagation={handleDelete}>
                    <Trash2 class="w-3.5 h-3.5" /><span>Delete</span>
                  </button>
                {/if}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>

    {#if product.description}
      <p class="text-xs line-clamp-2 mb-3" style="color: var(--color-text-secondary);">{product.description}</p>
    {/if}

    <!-- Footer -->
    <div class="flex items-center justify-between pt-3" style="border-top: 1px solid var(--color-border-subtle);">
      <div class="flex items-center gap-2 min-w-0">
        {#if product.owner_team}
          <span class="text-[11px] truncate" style="color: var(--color-text-tertiary);">{product.owner_team}</span>
        {/if}
        {#if product.compliance_standards && product.compliance_standards.length > 0}
          {#each product.compliance_standards.slice(0, 2) as standard}
            <span class="px-1.5 py-0.5 rounded text-[10px] font-medium flex-shrink-0"
              style="background: var(--color-bg-elevated); color: var(--color-text-tertiary);">{standard}</span>
          {/each}
        {:else}
          <span class="text-[11px]" style="color: var(--color-text-tertiary);">
            {formatDate(product.created_at)}
          </span>
        {/if}
      </div>
      <span class="text-[11px] font-medium flex items-center gap-1 flex-shrink-0 transition-colors"
        style="color: var(--color-text-tertiary);">
        Open TARA
        <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
        </svg>
      </span>
    </div>
  </div>
</div>

{#if showMenu}
  <button
    class="fixed inset-0 z-0 cursor-default"
    on:click={() => showMenu = false}
    aria-label="Close menu"
  ></button>
{/if}
