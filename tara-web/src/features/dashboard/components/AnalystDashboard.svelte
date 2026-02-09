<script lang="ts">
  import { goto } from '$app/navigation';
  import MetricCard from '../../../components/ui/MetricCard.svelte';
  import EmptyState from '../../../components/ui/EmptyState.svelte';
  import { FileText, Package, Zap, AlertTriangle, Shield, Pill } from '@lucide/svelte';

  interface Props {
    productScopes: any[];
    totalProducts: number;
    totalAssets: number;
    totalDamageScenarios: number;
    totalThreatScenarios: number;
    totalRiskAssessments: number;
    totalTreatments: number;
  }

  const {
    productScopes, totalProducts, totalAssets,
    totalDamageScenarios, totalThreatScenarios,
    totalRiskAssessments, totalTreatments
  }: Props = $props();

  const pipelineSteps = [
    { id: 'scope',   label: 'Scope',   icon: FileText,      route: '/products',          count: totalProducts },
    { id: 'assets',  label: 'Assets',  icon: Package,       route: '/assets',            count: totalAssets },
    { id: 'damage',  label: 'Damage',  icon: Zap,           route: '/damage-scenarios',  count: totalDamageScenarios },
    { id: 'threats', label: 'Threats', icon: AlertTriangle,  route: '/threat-scenarios',  count: totalThreatScenarios },
    { id: 'risk',    label: 'Risk',    icon: Shield,         route: '/risk-assessment',   count: totalRiskAssessments },
    { id: 'treat',   label: 'Treat',   icon: Pill,           route: '/risk-treatment',    count: totalTreatments },
  ];

  function generateReport(scopeId: string): void {
    window.open(`/api/reports/tara-pdf/${scopeId}`, '_blank');
  }
</script>

<!-- Metrics strip -->
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
  {#each pipelineSteps as step}
    <MetricCard value={step.count} label={step.label} icon={step.icon} accent="var(--color-accent-primary)" />
  {/each}
</div>

<!-- Pipeline visualisation -->
<div
  class="rounded-lg p-5 mb-6"
  style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);"
>
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-sm font-semibold uppercase tracking-wider" style="color: var(--color-text-secondary);">
      TARA Pipeline
    </h2>
    <button
      onclick={() => goto('/products')}
      class="px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
      style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
      onmouseenter={(e) => e.currentTarget.style.background = 'var(--color-accent-primary-hover)'}
      onmouseleave={(e) => e.currentTarget.style.background = 'var(--color-accent-primary)'}
    >
      + New TARA
    </button>
  </div>

  <div class="flex items-center gap-1">
    {#each pipelineSteps as step, i}
      <a
        href={step.route}
        class="flex-1 group"
      >
        <div
          class="relative rounded-md px-3 py-3 text-center transition-all"
          style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-subtle);"
          role="presentation"
          onmouseenter={(e) => { e.currentTarget.style.borderColor = 'var(--color-accent-primary)'; e.currentTarget.style.background = 'var(--color-bg-surface-hover)'; }}
          onmouseleave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-subtle)'; e.currentTarget.style.background = 'var(--color-bg-elevated)'; }}
        >
          <step.icon class="w-4 h-4 mx-auto mb-1.5" style="color: var(--color-accent-primary);" />
          <div class="text-lg font-bold" style="color: var(--color-text-primary);">{step.count}</div>
          <div class="text-[10px] font-medium uppercase tracking-wide" style="color: var(--color-text-tertiary);">
            {step.label}
          </div>
        </div>
      </a>
      {#if i < pipelineSteps.length - 1}
        <div class="flex-shrink-0 w-4 text-center" style="color: var(--color-text-tertiary);">
          <svg class="w-3 h-3 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      {/if}
    {/each}
  </div>
</div>

<!-- Recent projects -->
<div
  class="rounded-lg p-5"
  style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);"
>
  <h2 class="text-sm font-semibold uppercase tracking-wider mb-4" style="color: var(--color-text-secondary);">
    Recent Projects
  </h2>

  {#if productScopes.length === 0}
    <EmptyState
      title="No TARA projects yet"
      description="Define your first product scope to begin threat analysis and risk assessment."
      ctaLabel="Create Product Scope"
      ctaHref="/products"
    />
  {:else}
    <div class="space-y-2">
      {#each productScopes.slice(0, 8) as scope}
        <div
          class="flex items-center justify-between rounded-md px-4 py-3 transition-colors cursor-pointer"
          style="border: 1px solid var(--color-border-subtle);"
          onmouseenter={(e) => e.currentTarget.style.background = 'var(--color-bg-surface-hover)'}
          onmouseleave={(e) => e.currentTarget.style.background = 'transparent'}
          onclick={() => goto('/products')}
          onkeydown={(e) => e.key === 'Enter' && goto('/products')}
          role="button"
          tabindex="0"
        >
          <div class="flex items-center gap-3 min-w-0">
            <div
              class="w-8 h-8 rounded-md flex items-center justify-center flex-shrink-0"
              style="background: var(--color-info-bg);"
            >
              <FileText class="w-4 h-4" style="color: var(--color-accent-primary);" />
            </div>
            <div class="min-w-0">
              <div class="text-sm font-medium truncate" style="color: var(--color-text-primary);">{scope.name}</div>
              <div class="text-xs" style="color: var(--color-text-tertiary);">
                {scope.product_type} · v{scope.version}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <span
              class="px-2 py-0.5 rounded-full text-[10px] font-medium"
              style="background: var(--color-status-draft-bg); color: var(--color-status-draft);"
            >
              {scope.status ?? 'active'}
            </span>
            <button
              onclick={(e) => { e.stopPropagation(); generateReport(scope.scope_id); }}
              class="px-2 py-1 rounded text-[11px] font-medium transition-colors"
              style="color: var(--color-text-link);"
              onmouseenter={(e) => e.currentTarget.style.background = 'var(--color-info-bg)'}
              onmouseleave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              Report
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
