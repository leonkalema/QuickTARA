<script lang="ts">
  import type { CraAssessmentListItem } from '$lib/types/cra';
  import { Shield, Calendar, TrendingUp } from '@lucide/svelte';

  interface Props {
    assessment: CraAssessmentListItem;
    onclick?: () => void;
  }

  let { assessment, onclick }: Props = $props();

  const CLASSIFICATION_LABELS: Record<string, string> = {
    default: 'Default',
    class_i: 'Class I',
    class_ii: 'Class II',
    critical: 'Critical',
  } as const;

  const CLASSIFICATION_COLORS: Record<string, string> = {
    default: 'var(--color-status-info)',
    class_i: 'var(--color-status-warning)',
    class_ii: 'var(--color-status-error)',
    critical: '#dc2626',
  } as const;

  const STATUS_LABELS: Record<string, string> = {
    draft: 'Draft',
    in_progress: 'In Progress',
    complete: 'Complete',
  } as const;

  const PRODUCT_TYPE_LABELS: Record<string, string> = {
    current: 'Current',
    legacy_a: 'Legacy A',
    legacy_b: 'Legacy B',
    legacy_c: 'Legacy C',
  } as const;

  function getComplianceColor(pct: number): string {
    if (pct >= 80) return 'var(--color-status-success)';
    if (pct >= 40) return 'var(--color-status-warning)';
    return 'var(--color-status-error)';
  }

  function formatDeadline(deadline?: string): string {
    if (!deadline) return '—';
    return new Date(deadline).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }
</script>

<button
  class="w-full text-left rounded-lg border p-4 transition-all duration-150 cursor-pointer"
  style="background: var(--color-bg-surface); border-color: var(--color-border-default);"
  onmouseenter={(e) => { e.currentTarget.style.borderColor = 'var(--color-accent-primary)'; }}
  onmouseleave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-default)'; }}
  {onclick}
>
  <!-- Header -->
  <div class="flex items-start justify-between mb-3">
    <div class="flex-1 min-w-0">
      <h3 class="text-sm font-semibold truncate" style="color: var(--color-text-primary);">
        {assessment.product_name ?? assessment.product_id}
      </h3>
      <span class="text-xs" style="color: var(--color-text-tertiary);">
        {PRODUCT_TYPE_LABELS[assessment.product_type] ?? assessment.product_type}
      </span>
    </div>
    {#if assessment.classification}
      <span
        class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
        style="background: {CLASSIFICATION_COLORS[assessment.classification] ?? 'var(--color-bg-surface-hover)'}20; color: {CLASSIFICATION_COLORS[assessment.classification] ?? 'var(--color-text-secondary)'};"
      >
        <Shield class="w-3 h-3 mr-1" />
        {CLASSIFICATION_LABELS[assessment.classification] ?? assessment.classification}
      </span>
    {:else}
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs" style="color: var(--color-text-tertiary); background: var(--color-bg-surface-hover);">
        Not classified
      </span>
    {/if}
  </div>

  <!-- Compliance -->
  <div class="mb-3 flex items-center gap-3">
    <svg width="36" height="36" viewBox="0 0 36 36">
      <circle cx="18" cy="18" r="14" fill="none" style="stroke: var(--color-bg-surface-hover);" stroke-width="3" />
      <circle
        cx="18" cy="18" r="14" fill="none"
        style="stroke: {getComplianceColor(assessment.overall_compliance_pct)};"
        stroke-width="3"
        stroke-linecap="round"
        stroke-dasharray="{(assessment.overall_compliance_pct / 100) * 87.96} 87.96"
        transform="rotate(-90 18 18)"
      />
    </svg>
    <div class="flex-1">
      <div class="flex items-center justify-between">
        <span class="text-xs" style="color: var(--color-text-secondary);">Compliance</span>
        <span class="text-xs font-bold" style="color: {getComplianceColor(assessment.overall_compliance_pct)};">
          {assessment.overall_compliance_pct}%
        </span>
      </div>
      <div class="w-full h-1.5 rounded-full mt-1" style="background: var(--color-bg-surface-hover);">
        <div
          class="h-1.5 rounded-full transition-all duration-300"
          style="width: {Math.max(assessment.overall_compliance_pct, 2)}%; background: {getComplianceColor(assessment.overall_compliance_pct)};"
        ></div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <div class="flex items-center justify-between">
    <span
      class="inline-flex items-center px-2 py-0.5 rounded text-xs"
      style="background: var(--color-bg-surface-hover); color: var(--color-text-secondary);"
    >
      {STATUS_LABELS[assessment.status] ?? assessment.status}
    </span>
    {#if assessment.compliance_deadline}
      <span class="inline-flex items-center gap-1 text-xs" style="color: var(--color-text-tertiary);">
        <Calendar class="w-3 h-3" />
        {formatDeadline(assessment.compliance_deadline)}
      </span>
    {/if}
  </div>
</button>
