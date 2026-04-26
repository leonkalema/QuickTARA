<script lang="ts">
  import type { CraAssessmentListItem } from '$lib/types/cra';
  import { Shield, Calendar } from '@lucide/svelte';

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

  const classColor = $derived(CLASSIFICATION_COLORS[assessment.classification ?? ''] ?? '#94a3b8');
</script>

<button
  class="w-full text-left rounded-xl border overflow-hidden transition-all duration-200 cursor-pointer group"
  style="background: var(--color-bg-surface); border-color: var(--color-border-default);"
  onmouseenter={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-focus)'; e.currentTarget.style.background = 'var(--color-bg-elevated)'; }}
  onmouseleave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-default)'; e.currentTarget.style.background = 'var(--color-bg-surface)'; }}
  {onclick}
>
  <div class="flex">
    <!-- Left classification stripe -->
    <div class="w-1 flex-shrink-0 rounded-l-xl" style="background: {classColor};"></div>

    <div class="flex-1 p-5">
      <!-- Top: name + classification -->
      <div class="flex items-start justify-between gap-3 mb-4">
        <div class="min-w-0">
          <h3 class="text-sm font-semibold leading-snug" style="color: var(--color-text-primary);">
            {assessment.product_name ?? assessment.product_id}
          </h3>
          <span class="text-xs" style="color: var(--color-text-tertiary);">
            {PRODUCT_TYPE_LABELS[assessment.product_type] ?? assessment.product_type}
          </span>
        </div>
        {#if assessment.classification}
          <span
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold flex-shrink-0"
            style="background: {classColor}18; color: {classColor};"
          >
            <Shield class="w-3 h-3" />
            {CLASSIFICATION_LABELS[assessment.classification] ?? assessment.classification}
          </span>
        {:else}
          <span class="text-[11px] flex-shrink-0" style="color: var(--color-text-tertiary);">Unclassified</span>
        {/if}
      </div>

      <!-- Compliance number + bar -->
      <div class="mb-4">
        <div class="flex items-baseline justify-between mb-1.5">
          <span class="text-3xl font-bold tabular-nums leading-none"
            style="color: {getComplianceColor(assessment.overall_compliance_pct)};">
            {assessment.overall_compliance_pct}%
          </span>
          <span class="text-xs" style="color: var(--color-text-tertiary);">compliant</span>
        </div>
        <div class="w-full h-1.5 rounded-full" style="background: var(--color-bg-elevated);">
          <div class="h-1.5 rounded-full transition-all duration-500"
            style="width: {Math.max(assessment.overall_compliance_pct, 1)}%; background: {getComplianceColor(assessment.overall_compliance_pct)};"></div>
        </div>
      </div>

      <!-- Footer: status + deadline -->
      <div class="flex items-center justify-between">
        <span class="text-[11px] font-medium px-2 py-0.5 rounded"
          style="background: var(--color-bg-elevated); color: var(--color-text-secondary);">
          {STATUS_LABELS[assessment.status] ?? assessment.status}
        </span>
        {#if assessment.compliance_deadline}
          <span class="inline-flex items-center gap-1 text-[11px]" style="color: var(--color-text-tertiary);">
            <Calendar class="w-3 h-3" />
            {formatDeadline(assessment.compliance_deadline)}
          </span>
        {/if}
      </div>
    </div>
  </div>
</button>
