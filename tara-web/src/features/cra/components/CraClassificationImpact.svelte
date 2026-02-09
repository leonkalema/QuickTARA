<script lang="ts">
  import type { CraClassification, CraProductType } from '$lib/types/cra';
  import { Shield, Clock, AlertTriangle, FileCheck, Banknote, CalendarClock } from '@lucide/svelte';

  interface Props {
    classification: CraClassification;
    productType: CraProductType;
    complianceDeadline?: string;
    automotiveException: boolean;
  }

  let { classification, productType, complianceDeadline, automotiveException }: Props = $props();

  interface ClassificationInfo {
    readonly label: string;
    readonly color: string;
    readonly conformityPath: string;
    readonly conformityDetail: string;
    readonly costMin: number;
    readonly costMax: number;
    readonly securityUpdateYears: number;
    readonly warnings: string[];
    readonly obligations: string[];
  }

  const CLASSIFICATION_INFO: Record<string, ClassificationInfo> = {
    default: {
      label: 'Default',
      color: 'var(--color-status-info)',
      conformityPath: 'Self-Assessment (Module A)',
      conformityDetail: 'Internal conformity assessment based on CRA Annex VIII. No third-party body required.',
      costMin: 0,
      costMax: 5000,
      securityUpdateYears: 5,
      warnings: [],
      obligations: [
        'Perform internal conformity assessment per Annex VIII',
        'Prepare EU Declaration of Conformity',
        'Apply CE marking before placing on market',
        'Provide security updates for at least 5 years',
      ],
    },
    class_i: {
      label: 'Class I — Important',
      color: 'var(--color-status-warning)',
      conformityPath: 'Self-Assessment with Harmonised Standards OR Third-Party',
      conformityDetail: 'Can self-assess if harmonised standards cover all requirements. Otherwise, third-party conformity assessment (Module B+C) is mandatory.',
      costMin: 5000,
      costMax: 20000,
      securityUpdateYears: 5,
      warnings: [
        'If no harmonised standard exists for your product category, third-party assessment is required.',
      ],
      obligations: [
        'Apply harmonised standards (if available) and self-assess',
        'OR engage a Conformity Assessment Body (CAB) for Module B+C',
        'Prepare technical documentation per Annex VII',
        'Implement vulnerability handling process (Art. 13)',
        'Report actively exploited vulnerabilities within 24h to ENISA',
      ],
    },
    class_ii: {
      label: 'Class II — Important',
      color: 'var(--color-status-error)',
      conformityPath: 'Mandatory Third-Party Assessment',
      conformityDetail: 'Third-party conformity assessment by a notified body is mandatory. Module H (full QA) or Module B+C (type examination + production QA).',
      costMin: 20000,
      costMax: 50000,
      securityUpdateYears: 5,
      warnings: [
        'You MUST engage a notified Conformity Assessment Body (CAB).',
        'Budget and plan timeline — CAB assessments take 3-6 months.',
      ],
      obligations: [
        'Engage a notified Conformity Assessment Body (CAB)',
        'Choose Module H (full QA) or Module B+C (type examination)',
        'Maintain quality management system documentation',
        'Implement coordinated vulnerability disclosure',
        'Report actively exploited vulnerabilities within 24h to ENISA',
      ],
    },
    critical: {
      label: 'Critical',
      color: '#dc2626',
      conformityPath: 'European Cybersecurity Certification',
      conformityDetail: 'Must obtain certification under a European cybersecurity certification scheme (EUCC or successor). This is the highest level of assurance.',
      costMin: 50000,
      costMax: 100000,
      securityUpdateYears: 5,
      warnings: [
        'European cybersecurity certification is mandatory — this is the most rigorous path.',
        'Certification schemes may not yet be fully available. Monitor ENISA publications.',
        'Plan 6-12 months for the certification process.',
      ],
      obligations: [
        'Obtain European cybersecurity certification (EUCC or applicable scheme)',
        'Maintain certified quality management system',
        'Implement full vulnerability handling and disclosure process',
        'Report actively exploited vulnerabilities within 24h to ENISA',
        'Provide security updates for at least 5 years or product lifetime',
      ],
    },
  } as const;

  function getInfo(): ClassificationInfo {
    return CLASSIFICATION_INFO[classification] ?? CLASSIFICATION_INFO.default;
  }

  function getDeadlineUrgency(): { label: string; color: string } {
    if (!complianceDeadline) return { label: 'Not set', color: 'var(--color-text-tertiary)' };
    const now = new Date();
    const deadline = new Date(complianceDeadline);
    const monthsLeft = Math.round((deadline.getTime() - now.getTime()) / (1000 * 60 * 60 * 24 * 30));
    if (monthsLeft <= 0) return { label: 'Deadline passed — ongoing compliance required', color: 'var(--color-status-warning)' };
    if (monthsLeft <= 6) return { label: `${monthsLeft} months to initial compliance`, color: 'var(--color-status-error)' };
    if (monthsLeft <= 12) return { label: `${monthsLeft} months to initial compliance`, color: 'var(--color-status-warning)' };
    return { label: `${monthsLeft} months to initial compliance`, color: 'var(--color-status-success)' };
  }

  function formatCost(amount: number): string {
    if (amount === 0) return '€0';
    return `€${(amount / 1000).toFixed(0)}k`;
  }

  function formatDate(d?: string): string {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }
</script>

{#if true}
{@const info = getInfo()}
{@const urgency = getDeadlineUrgency()}

<div class="space-y-4">
  <!-- Classification badge + conformity path -->
  <div class="rounded-lg border p-5" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
    <div class="flex items-start justify-between mb-4">
      <div>
        <div class="text-xs font-semibold uppercase tracking-wider mb-1" style="color: var(--color-text-tertiary);">Classification Result</div>
        <div class="flex items-center gap-2">
          <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-sm font-semibold" style="background: {info.color}15; color: {info.color};">
            <Shield class="w-4 h-4" />
            {info.label}
          </span>
          {#if automotiveException}
            <span class="px-2 py-0.5 rounded text-xs" style="background: var(--color-status-warning)15; color: var(--color-status-warning);">
              Automotive Exception Claimed
            </span>
          {/if}
        </div>
      </div>
    </div>
    <!-- Key metrics row -->
    <div class="grid grid-cols-3 gap-4">
      <div class="rounded-lg p-3" style="background: var(--color-bg-surface-hover);">
        <div class="flex items-center gap-1.5 mb-1">
          <FileCheck class="w-3.5 h-3.5" style="color: {info.color};" />
          <span class="text-xs font-medium" style="color: var(--color-text-tertiary);">Conformity Path</span>
        </div>
        <div class="text-sm font-semibold" style="color: var(--color-text-primary);">{info.conformityPath}</div>
        <p class="text-xs mt-1" style="color: var(--color-text-secondary);">{info.conformityDetail}</p>
      </div>
      <div class="rounded-lg p-3" style="background: var(--color-bg-surface-hover);">
        <div class="flex items-center gap-1.5 mb-1">
          <CalendarClock class="w-3.5 h-3.5" style="color: {urgency.color};" />
          <span class="text-xs font-medium" style="color: var(--color-text-tertiary);">Initial Compliance Deadline</span>
        </div>
        <div class="text-sm font-semibold" style="color: var(--color-text-primary);">{formatDate(complianceDeadline)}</div>
        <div class="flex items-center gap-1 mt-1">
          <Clock class="w-3 h-3" style="color: {urgency.color};" />
          <span class="text-xs font-medium" style="color: {urgency.color};">{urgency.label}</span>
        </div>
      </div>
      <div class="rounded-lg p-3" style="background: var(--color-bg-surface-hover);">
        <div class="flex items-center gap-1.5 mb-1">
          <Banknote class="w-3.5 h-3.5" style="color: var(--color-text-tertiary);" />
          <span class="text-xs font-medium" style="color: var(--color-text-tertiary);">Est. Assessment Cost</span>
        </div>
        <div class="text-sm font-semibold" style="color: var(--color-text-primary);">
          {formatCost(info.costMin)} — {formatCost(info.costMax)}
        </div>
        <p class="text-xs mt-1" style="color: var(--color-text-secondary);">Conformity assessment budget range</p>
      </div>
    </div>
  </div>

  <!-- Warnings -->
  {#if info.warnings.length > 0}
    <div class="rounded-lg border p-4 space-y-2" style="background: {info.color}08; border-color: {info.color}30;">
      {#each info.warnings as warning}
        <div class="flex items-start gap-2">
          <AlertTriangle class="w-4 h-4 flex-shrink-0 mt-0.5" style="color: {info.color};" />
          <p class="text-sm" style="color: var(--color-text-primary);">{warning}</p>
        </div>
      {/each}
    </div>
  {/if}

  <!-- Obligations checklist -->
  <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
    <div class="text-xs font-semibold uppercase tracking-wider mb-3" style="color: var(--color-text-tertiary);">
      Required Obligations ({info.label})
    </div>
    <div class="space-y-2">
      {#each info.obligations as obligation, i}
        <div class="flex items-start gap-2 text-sm">
          <span class="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0" style="background: {info.color}15; color: {info.color};">
            {i + 1}
          </span>
          <span style="color: var(--color-text-secondary);">{obligation}</span>
        </div>
      {/each}
    </div>
  </div>
</div>
{/if}
