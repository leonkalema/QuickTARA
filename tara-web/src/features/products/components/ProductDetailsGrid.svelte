<script lang="ts">
  import { User } from '@lucide/svelte';
  import type { Product } from '$lib/types/product';

  export let product: Product;
</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <h2 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Technical Details</h2>
    <div class="space-y-3">
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Product ID</div>
        <p class="text-xs font-mono px-2 py-1 rounded" style="color: var(--color-text-primary); background: var(--color-bg-inset);">{product.scope_id}</p>
      </div>
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Trust Zone</div>
        <p class="text-xs" style="color: var(--color-text-primary);">{product.trust_zone || 'Standard'}</p>
      </div>
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Version</div>
        <p class="text-xs" style="color: var(--color-text-primary);">{product.version || 1}</p>
      </div>
    </div>
  </div>

  <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <h2 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Configuration</h2>
    <div class="space-y-3">
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Interfaces</div>
        {#if product.interfaces && product.interfaces.length > 0}
          <div class="flex flex-wrap gap-1">
            {#each product.interfaces as productInterface}
              <span class="px-2 py-0.5 text-[10px] rounded" style="background: var(--color-info-bg); color: var(--color-info);">{productInterface}</span>
            {/each}
          </div>
        {:else}
          <p class="text-xs" style="color: var(--color-text-tertiary);">No interfaces defined</p>
        {/if}
      </div>
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Access Points</div>
        {#if product.access_points && product.access_points.length > 0}
          <div class="flex flex-wrap gap-1">
            {#each product.access_points as point}
              <span class="px-2 py-0.5 text-[10px] rounded" style="background: var(--color-success-bg); color: var(--color-success);">{point}</span>
            {/each}
          </div>
        {:else}
          <p class="text-xs" style="color: var(--color-text-tertiary);">No access points defined</p>
        {/if}
      </div>
    </div>
  </div>

  <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <h2 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Analysis Scope</h2>
    <div class="space-y-3">
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Boundaries</div>
        {#if product.boundaries && product.boundaries.length > 0}
          <ul class="text-xs space-y-1" style="color: var(--color-text-primary);">
            {#each product.boundaries as boundary}
              <li class="flex items-start">
                <span class="w-1 h-1 rounded-full mt-1.5 mr-2 flex-shrink-0" style="background: var(--color-text-tertiary);"></span>
                {boundary}
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-xs" style="color: var(--color-text-tertiary);">No boundaries defined</p>
        {/if}
      </div>
      <div>
        <div class="text-[11px] font-medium mb-1" style="color: var(--color-text-tertiary);">Objectives</div>
        {#if product.objectives && product.objectives.length > 0}
          <ul class="text-xs space-y-1" style="color: var(--color-text-primary);">
            {#each product.objectives as objective}
              <li class="flex items-start">
                <span class="w-1 h-1 rounded-full mt-1.5 mr-2 flex-shrink-0" style="background: var(--color-text-tertiary);"></span>
                {objective}
              </li>
            {/each}
          </ul>
        {:else}
          <p class="text-xs" style="color: var(--color-text-tertiary);">No objectives defined</p>
        {/if}
      </div>
    </div>
  </div>

  <div class="rounded-lg p-5" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <h2 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">Stakeholders</h2>
    {#if product.stakeholders && product.stakeholders.length > 0}
      <div class="space-y-2">
        {#each product.stakeholders as stakeholder}
          <div class="flex items-center">
            <User class="w-3.5 h-3.5 mr-2" style="color: var(--color-text-tertiary);" />
            <span class="text-xs" style="color: var(--color-text-primary);">{stakeholder}</span>
          </div>
        {/each}
      </div>
    {:else}
      <p class="text-xs" style="color: var(--color-text-tertiary);">No stakeholders defined</p>
    {/if}
  </div>
</div>
