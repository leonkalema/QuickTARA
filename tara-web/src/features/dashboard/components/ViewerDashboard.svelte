<script lang="ts">
  import MetricCard from '../../../components/ui/MetricCard.svelte';
  import EmptyState from '../../../components/ui/EmptyState.svelte';
  import { FileText, BarChart3 } from '@lucide/svelte';

  interface Props {
    productScopes: any[];
    totalProducts: number;
  }

  const { productScopes, totalProducts }: Props = $props();

  function generateReport(scopeId: string): void {
    window.open(`/api/reports/tara-pdf/${scopeId}`, '_blank');
  }
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
  <MetricCard value={totalProducts} label="Available Products" icon={FileText} accent="var(--color-accent-primary)" />
  <MetricCard value={productScopes.length} label="Reports Available" icon={BarChart3} accent="var(--color-success)" />
</div>

<div
  class="rounded-lg p-5"
  style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);"
>
  <h2 class="text-sm font-semibold uppercase tracking-wider mb-4" style="color: var(--color-text-secondary);">
    Available Reports
  </h2>

  {#if productScopes.length === 0}
    <EmptyState
      title="No reports available yet"
      description="Reports will appear here once TARA assessments are completed for your assigned products."
    />
  {:else}
    <div class="space-y-2">
      {#each productScopes as scope}
        <div
          class="flex items-center justify-between rounded-md px-4 py-3"
          style="border: 1px solid var(--color-border-subtle);"
        >
          <div class="min-w-0">
            <div class="text-sm font-medium" style="color: var(--color-text-primary);">{scope.name}</div>
            <div class="text-xs" style="color: var(--color-text-tertiary);">
              {scope.product_type} · {scope.safety_level}
            </div>
          </div>
          <button
            onclick={() => generateReport(scope.scope_id)}
            class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex-shrink-0"
            style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
            onmouseenter={(e) => e.currentTarget.style.background = 'var(--color-accent-primary-hover)'}
            onmouseleave={(e) => e.currentTarget.style.background = 'var(--color-accent-primary)'}
          >
            View Report
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>
