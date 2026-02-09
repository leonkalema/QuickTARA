<script lang="ts">
  import type { GapAnalysisResponse, GapRequirementItem } from '$lib/types/cra';
  import { Shield, Printer, Download, X } from '@lucide/svelte';

  interface Props {
    analysis: GapAnalysisResponse;
    productName: string;
    onclose: () => void;
  }

  let { analysis, productName, onclose }: Props = $props();

  const STATUS_LABELS: Record<string, string> = {
    not_started: 'Not Started',
    partial: 'Partial',
    compliant: 'Compliant',
    not_applicable: 'N/A',
  };

  const STATUS_DEFINITIONS: Record<string, string> = {
    not_started: 'No implementation activity has begun for this requirement.',
    partial: 'Implementation is in progress but not yet complete. Evidence may be incomplete or controls not fully deployed.',
    compliant: 'Requirement is fully implemented, verified through testing or review, and supporting evidence is documented.',
    not_applicable: 'Requirement does not apply to this product. A documented justification must be provided.',
  };

  const RISK_LABELS: Record<string, string> = {
    none: 'None', low: 'Low', medium: 'Medium', high: 'High', critical: 'Critical',
  };

  const CLASSIFICATION_LABELS: Record<string, string> = {
    default: 'Default', class_i: 'Class I', class_ii: 'Class II', critical: 'Critical',
  };

  function getResidualRisk(req: GapRequirementItem): string {
    if (!req.is_gap) return 'None — Compliant';
    if (req.applied_controls.length === 0) return RISK_LABELS[req.risk_level] ?? req.risk_level;
    const hasVerified = req.applied_controls.some(c => c.status === 'verified');
    const hasImplemented = req.applied_controls.some(c => c.status === 'implemented');
    const allPlanned = req.applied_controls.every(c => c.status === 'planned');
    if (hasVerified) return 'Low — Control verified';
    if (hasImplemented) return 'Medium — Control implemented, not verified';
    if (allPlanned) return 'High — Control planned, not yet implemented';
    return 'Medium — Control in progress';
  }

  function getControlsSummary(req: GapRequirementItem): string {
    if (req.applied_controls.length === 0) return '—';
    return req.applied_controls.map(c => `[${c.control_id}] ${c.name} (${c.status})`).join('; ');
  }

  function getJustification(req: GapRequirementItem): string {
    return req.evidence_notes || '—';
  }

  function getEvidenceSummary(req: GapRequirementItem): string {
    if (req.tara_evidence.length === 0) return '—';
    return req.tara_evidence.map(e => `${e.count} ${e.type}(s)`).join(', ');
  }

  function handlePrint(): void {
    window.print();
  }

  function exportCsv(): void {
    const headers = [
      'Requirement ID', 'Requirement', 'Article', 'Category',
      'Status', 'Is Gap', 'Risk Level', 'Applied Controls',
      'Residual Risk', 'TARA Evidence', 'Justification / Notes', 'Owner', 'Target Date',
    ];
    const rows = analysis.requirements.map(r => [
      r.requirement_id,
      r.requirement_name,
      r.article,
      r.category,
      STATUS_LABELS[r.status] ?? r.status,
      r.is_gap ? 'Yes' : 'No',
      RISK_LABELS[r.risk_level] ?? r.risk_level,
      getControlsSummary(r),
      getResidualRisk(r),
      getEvidenceSummary(r),
      getJustification(r),
      r.owner ?? '',
      r.target_date ?? '',
    ]);
    const csvContent = [headers, ...rows]
      .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
      .join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `CRA_Traceability_${productName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  function today(): string {
    return new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }
</script>

<!-- Print styles -->
<svelte:head>
  <style>
    @media print {
      body * { visibility: hidden !important; }
      .traceability-report, .traceability-report * { visibility: visible !important; }
      .traceability-report { position: absolute; left: 0; top: 0; width: 100%; }
      .no-print { display: none !important; }
      .print-table { font-size: 9px; }
      .print-table th, .print-table td { padding: 4px 6px; border: 1px solid #333; }
    }
  </style>
</svelte:head>

<div class="traceability-report">
  <!-- Toolbar (hidden on print) -->
  <div class="no-print flex items-center justify-between mb-4 px-4 py-3 rounded-lg border" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
    <div class="flex items-center gap-2">
      <Shield class="w-4 h-4" style="color: var(--color-accent-primary);" />
      <span class="text-sm font-semibold" style="color: var(--color-text-primary);">CRA Traceability Report</span>
    </div>
    <div class="flex items-center gap-2">
      <button
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        onclick={handlePrint}
      >
        <Printer class="w-3 h-3" /> Print
      </button>
      <button
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
        style="background: var(--color-bg-surface-hover); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
        onclick={exportCsv}
      >
        <Download class="w-3 h-3" /> Export CSV
      </button>
      <button
        class="p-1.5 rounded cursor-pointer"
        style="color: var(--color-text-tertiary);"
        onclick={onclose}
      >
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>

  <!-- Report header -->
  <div class="mb-4 px-1">
    <h2 class="text-base font-bold" style="color: var(--color-text-primary);">
      CRA Compliance Traceability — {productName}
    </h2>
    <div class="flex gap-4 mt-1 text-xs" style="color: var(--color-text-secondary);">
      <span>Classification: <strong>{CLASSIFICATION_LABELS[analysis.classification] ?? analysis.classification}</strong></span>
      <span>Product Type: <strong>{analysis.is_legacy ? 'Legacy' : 'Current'}</strong></span>
      <span>Generated: <strong>{today()}</strong></span>
    </div>
    <div class="flex gap-4 mt-1 text-xs" style="color: var(--color-text-secondary);">
      <span>Compliant: <strong style="color: var(--color-status-success);">{analysis.summary.compliant}/{analysis.summary.total}</strong></span>
      <span>Gaps: <strong style="color: var(--color-status-error);">{analysis.summary.gaps}</strong></span>
      <span>With Controls: <strong style="color: var(--color-accent-primary);">{analysis.summary.with_controls}</strong></span>
    </div>
  </div>

  <!-- Status definitions legend -->
  <div class="mb-4 rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
    <div class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--color-text-tertiary);">Status Definitions</div>
    <div class="grid grid-cols-2 gap-x-6 gap-y-1.5">
      {#each Object.entries(STATUS_DEFINITIONS) as [key, definition]}
        <div class="flex items-start gap-2 text-xs">
          <span class="font-semibold whitespace-nowrap" style="color: {key === 'compliant' ? 'var(--color-status-success)' : key === 'partial' ? 'var(--color-status-warning)' : 'var(--color-text-secondary)'};">
            {STATUS_LABELS[key]}:
          </span>
          <span style="color: var(--color-text-secondary);">{definition}</span>
        </div>
      {/each}
    </div>
  </div>

  <!-- Traceability table -->
  <div class="overflow-x-auto rounded-lg border" style="border-color: var(--color-border-default);">
    <table class="print-table w-full text-xs" style="border-collapse: collapse;">
      <thead>
        <tr style="background: var(--color-bg-surface-hover);">
          <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Req ID</th>
          <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Requirement</th>
          <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Status</th>
          <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Gap?</th>
          <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Controls Applied</th>
          <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Residual Risk</th>
          <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Evidence</th>
          <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Justification / Notes</th>
          <th class="px-3 py-2 text-left font-semibold" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-default);">Owner</th>
        </tr>
      </thead>
      <tbody>
        {#each analysis.requirements as req (req.requirement_id)}
          {@const residual = getResidualRisk(req)}
          <tr style="background: var(--color-bg-surface); border-bottom: 1px solid var(--color-border-subtle);">
            <td class="px-3 py-2 font-mono" style="color: var(--color-text-tertiary);">{req.requirement_id}</td>
            <td class="px-3 py-2" style="color: var(--color-text-primary);">
              {req.requirement_name}
              <span class="ml-1" style="color: var(--color-text-tertiary);">({req.article})</span>
            </td>
            <td class="px-3 py-2" style="color: {req.status === 'compliant' ? 'var(--color-status-success)' : req.status === 'partial' ? 'var(--color-status-warning)' : 'var(--color-text-secondary)'};">
              {STATUS_LABELS[req.status] ?? req.status}
            </td>
            <td class="px-3 py-2" style="color: {req.is_gap ? 'var(--color-status-error)' : 'var(--color-status-success)'};">
              {req.is_gap ? 'Yes' : 'No'}
            </td>
            <td class="px-3 py-2" style="color: var(--color-text-secondary);">
              {#if req.applied_controls.length > 0}
                {#each req.applied_controls as ctrl}
                  <div>
                    <span class="font-mono" style="color: var(--color-text-tertiary);">[{ctrl.control_id}]</span>
                    {ctrl.name}
                    <span style="color: var(--color-text-tertiary);">({ctrl.status})</span>
                  </div>
                {/each}
              {:else}
                <span style="color: var(--color-text-tertiary);">—</span>
              {/if}
            </td>
            <td class="px-3 py-2 font-medium" style="color: {residual.includes('None') ? 'var(--color-status-success)' : residual.includes('Low') ? 'var(--color-text-tertiary)' : residual.includes('Medium') ? 'var(--color-status-warning)' : 'var(--color-status-error)'};">
              {residual}
            </td>
            <td class="px-3 py-2" style="color: var(--color-text-secondary);">
              {getEvidenceSummary(req)}
            </td>
            <td class="px-3 py-2" style="color: {(req.status === 'not_applicable' || req.status === 'partial') && !req.evidence_notes ? 'var(--color-status-warning)' : 'var(--color-text-secondary)'};">
              {#if req.evidence_notes}
                {req.evidence_notes}
              {:else if req.status === 'not_applicable'}
                <em>Justification required</em>
              {:else if req.status === 'partial'}
                <em>Notes recommended</em>
              {:else}
                —
              {/if}
            </td>
            <td class="px-3 py-2" style="color: var(--color-text-secondary);">
              {req.owner ?? '—'}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
