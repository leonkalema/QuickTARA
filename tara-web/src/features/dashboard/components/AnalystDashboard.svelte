<script lang="ts">
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';

  interface ProductScope {
    scope_id: string;
    name: string;
    product_type: string;
    version: string;
    status?: string;
  }

  interface Props {
    productScopes: ProductScope[];
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

  const userName = $derived(
    $authStore.user?.username ?? $authStore.user?.email?.split('@')[0] ?? 'there'
  );

  const metrics = [
    { label: 'Products', value: totalProducts, color: '#4f8ff7', bg: 'rgba(79,143,247,0.12)', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>`, route: '/products' },
    { label: 'Assets', value: totalAssets, color: '#a78bfa', bg: 'rgba(167,139,250,0.12)', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>`, route: '/assets' },
    { label: 'Damage Scenarios', value: totalDamageScenarios, color: '#fb923c', bg: 'rgba(251,146,60,0.12)', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>`, route: '/damage-scenarios' },
    { label: 'Threat Scenarios', value: totalThreatScenarios, color: '#f87171', bg: 'rgba(248,113,113,0.12)', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>`, route: '/threat-scenarios' },
    { label: 'Risk Assessments', value: totalRiskAssessments, color: '#38bdf8', bg: 'rgba(56,189,248,0.12)', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>`, route: '/risk-assessment' },
    { label: 'Treatments', value: totalTreatments, color: '#34d399', bg: 'rgba(52,211,153,0.12)', icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>`, route: '/risk-treatment' },
  ];

  const workflowSteps = [
    { step: 1, label: 'Define Scope', desc: 'Set product boundaries', route: '/products', done: totalProducts > 0 },
    { step: 2, label: 'Add Assets', desc: 'Identify components', route: '/assets', done: totalAssets > 0 },
    { step: 3, label: 'Damage Scenarios', desc: 'What could go wrong', route: '/damage-scenarios', done: totalDamageScenarios > 0 },
    { step: 4, label: 'Threat Scenarios', desc: 'How it could happen', route: '/threat-scenarios', done: totalThreatScenarios > 0 },
    { step: 5, label: 'Risk Assessment', desc: 'Rate the risks', route: '/risk-assessment', done: totalRiskAssessments > 0 },
    { step: 6, label: 'Risk Treatment', desc: 'Mitigate & accept', route: '/risk-treatment', done: totalTreatments > 0 },
  ];

  const nextStep = workflowSteps.find(s => !s.done) ?? workflowSteps[workflowSteps.length - 1];

  function generateReport(scopeId: string): void {
    window.open(`/api/reports/tara-pdf/${scopeId}`, '_blank');
  }
</script>

<!-- Welcome banner -->
<div class="rounded-xl p-5 mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4"
  style="background: linear-gradient(135deg, #1e3a5f 0%, #0f2440 100%); border: 1px solid rgba(79,143,247,0.3);">
  <div>
    <p class="text-xs font-semibold uppercase tracking-widest mb-1" style="color: #4f8ff7;">ISO/SAE 21434 · TARA Workflow</p>
    <h2 class="text-lg font-bold mb-1" style="color: #f1f5f9;">
      {#if totalProducts === 0}
        Get started — define your first product
      {:else}
        Next: <span style="color: #4f8ff7;">{nextStep.label}</span>
      {/if}
    </h2>
    <p class="text-sm" style="color: #94a3b8;">
      {#if totalProducts === 0}
        A TARA starts with defining the product scope — what you're analyzing and why.
      {:else}
        {nextStep.desc} — step {nextStep.step} of 6 in the TARA pipeline.
      {/if}
    </p>
  </div>
  <button
    onclick={() => goto(nextStep.route)}
    class="flex-shrink-0 px-5 py-2.5 rounded-lg text-sm font-semibold transition-all"
    style="background: #4f8ff7; color: #fff;"
    onmouseenter={(e) => e.currentTarget.style.background = '#3b7de8'}
    onmouseleave={(e) => e.currentTarget.style.background = '#4f8ff7'}
  >
    {totalProducts === 0 ? 'Create First Product →' : `Continue: ${nextStep.label} →`}
  </button>
</div>

<!-- Metric cards -->
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
  {#each metrics as m}
    <a href={m.route} class="block rounded-lg p-4 transition-all duration-150"
      style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);"
      onmouseenter={(e) => { e.currentTarget.style.borderColor = m.color; e.currentTarget.style.background = 'var(--color-bg-elevated)'; }}
      onmouseleave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-default)'; e.currentTarget.style.background = 'var(--color-bg-surface)'; }}
    >
      <div class="w-8 h-8 rounded-md flex items-center justify-center mb-3" style="background: {m.bg}; opacity: {m.value === 0 ? '0.5' : '1'};">
        <svg class="w-4 h-4" fill="none" stroke="{m.color}" viewBox="0 0 24 24">{@html m.icon}</svg>
      </div>
      {#if m.value === 0}
        <div class="text-xl font-bold mb-0.5" style="color: var(--color-text-tertiary);">—</div>
        <div class="text-[11px] font-medium" style="color: var(--color-text-tertiary);">{m.label}</div>
        <div class="text-[10px] mt-1" style="color: var(--color-accent-primary);">Start →</div>
      {:else}
        <div class="text-2xl font-bold mb-0.5" style="color: var(--color-text-primary);">{m.value}</div>
        <div class="text-[11px] font-medium" style="color: var(--color-text-tertiary);">{m.label}</div>
      {/if}
    </a>
  {/each}
</div>

<!-- Workflow stepper + Recent projects side by side -->
<div class="grid grid-cols-1 lg:grid-cols-5 gap-4">

  <!-- Workflow stepper -->
  <div class="lg:col-span-2 rounded-lg p-5"
    style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <h2 class="text-xs font-semibold uppercase tracking-wider mb-4" style="color: var(--color-text-tertiary);">TARA Workflow</h2>
    <div class="space-y-1">
      {#each workflowSteps as s}
        {@const isNext = s.step === nextStep.step && !s.done}
        <a href={s.route}
          class="flex items-center gap-3 rounded-lg px-3 py-2.5 transition-all"
          style="background: {isNext ? 'rgba(79,143,247,0.1)' : 'transparent'}; border: 1px solid {isNext ? 'rgba(79,143,247,0.3)' : 'transparent'};"
          onmouseenter={(e) => { if (!isNext) e.currentTarget.style.background = 'var(--color-bg-surface-hover)'; }}
          onmouseleave={(e) => { if (!isNext) e.currentTarget.style.background = 'transparent'; }}
        >
          <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold"
            style="background: {s.done ? '#34d399' : isNext ? '#4f8ff7' : 'var(--color-bg-elevated)'}; color: {s.done || isNext ? '#fff' : 'var(--color-text-tertiary)'};">
            {#if s.done}
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
            {:else}
              {s.step}
            {/if}
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-sm font-medium" style="color: {s.done ? 'var(--color-text-secondary)' : isNext ? '#4f8ff7' : 'var(--color-text-primary)'};">{s.label}</div>
            <div class="text-[11px]" style="color: var(--color-text-tertiary);">{s.desc}</div>
          </div>
          {#if isNext}
            <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="#4f8ff7" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
          {/if}
        </a>
      {/each}
    </div>
  </div>

  <!-- Recent projects -->
  <div class="lg:col-span-3 rounded-lg p-5"
    style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-tertiary);">Recent Projects</h2>
      <button onclick={() => goto('/products')}
        class="text-xs font-medium px-3 py-1 rounded-md transition-colors"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);">
        + New TARA
      </button>
    </div>

    {#if productScopes.length === 0}
      <div class="flex flex-col items-center py-10 text-center">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center mb-3"
          style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
          </svg>
        </div>
        <p class="text-sm font-medium mb-1" style="color: var(--color-text-primary);">No projects yet</p>
        <p class="text-xs mb-4" style="color: var(--color-text-tertiary);">Create your first product scope to begin.</p>
        <button onclick={() => goto('/products')}
          class="px-4 py-2 rounded-md text-sm font-medium"
          style="background: var(--color-accent-primary); color: var(--color-text-inverse);">
          Create Product Scope
        </button>
      </div>
    {:else}
      <div class="space-y-1">
        {#each productScopes.slice(0, 6) as scope}
          <div class="flex items-center justify-between rounded-lg px-3 py-3 cursor-pointer transition-colors"
            onmouseenter={(e) => e.currentTarget.style.background = 'var(--color-bg-surface-hover)'}
            onmouseleave={(e) => e.currentTarget.style.background = 'transparent'}
            onclick={() => goto('/products')}
            onkeydown={(e) => e.key === 'Enter' && goto('/products')}
            role="button" tabindex="0">
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-8 h-8 rounded-md flex items-center justify-center flex-shrink-0"
                style="background: rgba(79,143,247,0.12);">
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="#4f8ff7" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                </svg>
              </div>
              <div class="min-w-0">
                <div class="text-sm font-medium truncate" style="color: var(--color-text-primary);">{scope.name}</div>
                <div class="text-[11px]" style="color: var(--color-text-tertiary);">{scope.product_type} · v{scope.version}</div>
              </div>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold"
                style="background: rgba(52,211,153,0.12); color: #34d399;">
                {scope.status ?? 'active'}
              </span>
              <button
                onclick={(e) => { e.stopPropagation(); generateReport(scope.scope_id); }}
                class="px-2 py-1 rounded text-[11px] font-medium transition-colors"
                style="color: #4f8ff7;"
                onmouseenter={(e) => e.currentTarget.style.background = 'rgba(79,143,247,0.1)'}
                onmouseleave={(e) => e.currentTarget.style.background = 'transparent'}>
                Report
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>
