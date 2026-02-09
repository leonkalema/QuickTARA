<script lang="ts">
  import { onMount } from 'svelte';
  import { craApi } from '$lib/api/craApi';
  import type { GapAnalysisResponse, GapRequirementItem, CompensatingControlCatalogItem, CraClassification } from '$lib/types/cra';
  import { ShieldCheck, AlertTriangle, ChevronDown, ChevronRight, Plus, Shield, Check, Loader2, FileText, Users } from '@lucide/svelte';
  import CraTraceabilityReport from './CraTraceabilityReport.svelte';
  import CraCustomerSummary from './CraCustomerSummary.svelte';

  interface Props {
    assessmentId: string;
    productName?: string;
    classification?: CraClassification;
    complianceDeadline?: string;
  }

  let { assessmentId, productName = 'Product', classification, complianceDeadline }: Props = $props();
  let showReport = $state(false);
  let showCustomerSummary = $state(false);

  let analysis: GapAnalysisResponse | null = $state(null);
  let catalog: CompensatingControlCatalogItem[] = $state([]);
  let loading = $state(true);
  let error: string | null = $state(null);
  let expandedId: string | null = $state(null);
  let applyingControlId: string | null = $state(null);
  let appliedFlash: string | null = $state(null);

  const RISK_CONFIG: Record<string, { label: string; color: string }> = {
    none: { label: 'No Risk', color: 'var(--color-status-success)' },
    low: { label: 'Low', color: 'var(--color-text-tertiary)' },
    medium: { label: 'Medium', color: 'var(--color-status-warning)' },
    high: { label: 'High', color: 'var(--color-status-error)' },
    critical: { label: 'Critical', color: '#dc2626' },
  };

  const STATUS_LABELS: Record<string, string> = {
    not_started: 'Not Started',
    partial: 'Partial',
    compliant: 'Compliant',
    not_applicable: 'N/A',
  };

  async function loadData(): Promise<void> {
    loading = true;
    error = null;
    try {
      const [gapData, catalogData] = await Promise.all([
        craApi.getGapAnalysis(assessmentId),
        craApi.getCompensatingControlsCatalog(),
      ]);
      analysis = gapData;
      catalog = catalogData;
    } catch (err) {
      console.error('Failed to load gap analysis:', err);
      error = 'Failed to load gap analysis';
    } finally {
      loading = false;
    }
  }

  onMount(() => { loadData(); });

  function getCatalogItem(controlId: string): CompensatingControlCatalogItem | undefined {
    return catalog.find((c: CompensatingControlCatalogItem) => c.control_id === controlId);
  }

  function getControlName(controlId: string): string {
    return getCatalogItem(controlId)?.name ?? controlId;
  }

  function isAlreadyApplied(gap: GapRequirementItem, controlId: string): boolean {
    return gap.applied_controls.some(c => c.control_id === controlId);
  }

  async function applyControl(gap: GapRequirementItem, controlId: string): Promise<void> {
    const catalogItem = getCatalogItem(controlId);
    if (!catalogItem) return;
    const key = `${gap.requirement_id}:${controlId}`;
    applyingControlId = key;
    try {
      await craApi.createCompensatingControl(assessmentId, {
        control_id: catalogItem.control_id,
        name: catalogItem.name,
        description: catalogItem.description,
        implementation_status: 'planned',
        mitigated_requirement_ids: [gap.requirement_status_id],
      });
      appliedFlash = key;
      setTimeout(() => { appliedFlash = null; }, 1500);
      await loadData();
    } catch (err) {
      console.error('Failed to apply control:', err);
      error = 'Failed to apply control';
    } finally {
      applyingControlId = null;
    }
  }

  function toggleExpand(reqId: string): void {
    expandedId = expandedId === reqId ? null : reqId;
  }

  function getGaps(): GapRequirementItem[] {
    if (!analysis) return [];
    return analysis.requirements
      .filter((r: GapRequirementItem) => r.is_gap)
      .sort((a: GapRequirementItem, b: GapRequirementItem) => {
        const order: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3, none: 4 };
        return (order[a.risk_level] ?? 4) - (order[b.risk_level] ?? 4);
      });
  }

  function getCompliant(): GapRequirementItem[] {
    if (!analysis) return [];
    return analysis.requirements.filter((r: GapRequirementItem) => !r.is_gap);
  }
</script>

<div class="space-y-4">
  {#if loading}
    <div class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-6 w-6 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
    </div>
  {:else if error}
    <div class="rounded-lg border p-4 text-center" style="background: var(--color-status-error)10; border-color: var(--color-status-error);">
      <p class="text-sm" style="color: var(--color-status-error);">{error}</p>
      <button class="mt-2 text-xs underline cursor-pointer" style="color: var(--color-accent-primary);" onclick={loadData}>Retry</button>
    </div>
  {:else if analysis && showCustomerSummary}
    <CraCustomerSummary
      {assessmentId}
      {productName}
      {classification}
      {complianceDeadline}
      onclose={() => { showCustomerSummary = false; }}
    />
  {:else if analysis && showReport}
    <CraTraceabilityReport
      {analysis}
      {productName}
      onclose={() => { showReport = false; }}
    />
  {:else if analysis}
    <!-- Report buttons -->
    <div class="flex justify-end gap-2">
      <button
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
        style="background: var(--color-bg-surface-hover); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
        onclick={() => { showReport = true; }}
      >
        <FileText class="w-3 h-3" />
        Audit Report
      </button>
      <button
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
        style="background: var(--color-status-success)15; color: var(--color-status-success); border: 1px solid var(--color-status-success)30;"
        onclick={() => { showCustomerSummary = true; }}
      >
        <Users class="w-3 h-3" />
        Customer Summary
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-4 gap-4">
      <div class="rounded-lg border p-4 text-center" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="text-2xl font-bold" style="color: var(--color-text-primary);">{analysis.summary.total}</div>
        <div class="text-xs" style="color: var(--color-text-tertiary);">Total Requirements</div>
      </div>
      <div class="rounded-lg border p-4 text-center" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="text-2xl font-bold" style="color: var(--color-status-success);">{analysis.summary.compliant}</div>
        <div class="text-xs" style="color: var(--color-text-tertiary);">Compliant / N/A</div>
      </div>
      <div class="rounded-lg border p-4 text-center" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="text-2xl font-bold" style="color: var(--color-status-error);">{analysis.summary.gaps}</div>
        <div class="text-xs" style="color: var(--color-text-tertiary);">Open Gaps</div>
      </div>
      <div class="rounded-lg border p-4 text-center" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <div class="text-2xl font-bold" style="color: var(--color-accent-primary);">{analysis.summary.with_controls}</div>
        <div class="text-xs" style="color: var(--color-text-tertiary);">Gaps with Controls</div>
      </div>
    </div>

    <!-- Risk context banner -->
    {#if analysis.summary.gaps > 0}
      <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <p class="text-xs" style="color: var(--color-text-secondary);">
          Risk levels are based on product classification
          (<strong style="color: var(--color-text-primary);">{analysis.classification?.replace('_', ' ').toUpperCase()}</strong>).
          {#if analysis.is_legacy}
            Legacy products can reduce risk by applying compensating controls.
          {:else}
            Requirements with TARA evidence are shown under compliant.
          {/if}
          Applying and verifying controls reduces the risk level.
        </p>
      </div>
    {/if}

    <!-- Gap List sorted by risk -->
    {#if getGaps().length === 0}
      <div class="text-center py-8 rounded-lg border" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
        <ShieldCheck class="w-12 h-12 mx-auto mb-3" style="color: var(--color-status-success);" />
        <p class="text-sm font-medium" style="color: var(--color-status-success);">All Requirements Met</p>
        <p class="text-xs mt-1" style="color: var(--color-text-secondary);">All 18 CRA requirements are compliant or not applicable.</p>
      </div>
    {:else}
      <div class="rounded-lg border overflow-hidden" style="border-color: var(--color-border-default);">
        <div class="px-4 py-3 flex items-center justify-between" style="background: var(--color-bg-surface-hover);">
          <h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">
            Open Gaps ({getGaps().length}) — sorted by risk
          </h3>
          {#if analysis.summary.critical_risk + analysis.summary.high_risk > 0}
            <span class="px-2 py-0.5 rounded text-xs font-medium" style="background: #dc262615; color: #dc2626;">
              {analysis.summary.critical_risk + analysis.summary.high_risk} high/critical
            </span>
          {/if}
        </div>
        <div class="divide-y" style="border-color: var(--color-border-subtle);">
          {#each getGaps() as gap (gap.requirement_id)}
            {@const riskCfg = RISK_CONFIG[gap.risk_level] ?? RISK_CONFIG.medium}
            {@const isExpanded = expandedId === gap.requirement_id}
            <div style="background: var(--color-bg-surface);">
              <button
                class="w-full px-4 py-3 flex items-center justify-between text-left cursor-pointer"
                style="background: {isExpanded ? 'var(--color-bg-surface-hover)' : 'transparent'};"
                onclick={() => toggleExpand(gap.requirement_id)}
              >
                <div class="flex items-center gap-3">
                  {#if isExpanded}
                    <ChevronDown class="w-4 h-4" style="color: var(--color-text-tertiary);" />
                  {:else}
                    <ChevronRight class="w-4 h-4" style="color: var(--color-text-tertiary);" />
                  {/if}
                  <div>
                    <span class="text-xs font-mono" style="color: var(--color-text-tertiary);">{gap.requirement_id}</span>
                    <span class="text-sm font-medium ml-2" style="color: var(--color-text-primary);">{gap.requirement_name}</span>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded text-xs" style="color: var(--color-text-secondary); background: var(--color-bg-surface-hover);">
                    {STATUS_LABELS[gap.status] ?? gap.status}
                  </span>
                  <span class="px-2 py-0.5 rounded text-xs font-medium" style="background: {riskCfg.color}15; color: {riskCfg.color};">
                    {riskCfg.label} Risk
                  </span>
                </div>
              </button>
              {#if isExpanded}
                <div class="px-4 pb-4 pt-2 ml-7 space-y-3 border-l-2" style="border-color: {riskCfg.color};">
                  <!-- Info row -->
                  <div class="flex gap-4 text-xs" style="color: var(--color-text-secondary);">
                    <span><strong>Article:</strong> {gap.article}</span>
                    <span><strong>Category:</strong> {gap.category}</span>
                    {#if gap.owner}
                      <span><strong>Owner:</strong> {gap.owner}</span>
                    {/if}
                    {#if gap.target_date}
                      <span><strong>Target:</strong> {gap.target_date}</span>
                    {/if}
                  </div>
                  <!-- Applied controls -->
                  {#if gap.applied_controls.length > 0}
                    <div>
                      <div class="text-xs font-medium mb-1" style="color: var(--color-accent-primary);">Applied Controls</div>
                      <div class="flex flex-wrap gap-2">
                        {#each gap.applied_controls as ctrl}
                          <span class="inline-flex items-center gap-1 px-2 py-1 rounded text-xs" style="background: var(--color-accent-primary)15; color: var(--color-accent-primary);">
                            <Shield class="w-3 h-3" />
                            {ctrl.name}
                            <span style="color: var(--color-text-tertiary);">({ctrl.status})</span>
                          </span>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  <!-- Suggested controls (legacy only) -->
                  {#if gap.suggested_controls.length > 0 && analysis.is_legacy}
                    {@const unapplied = gap.suggested_controls.filter(cid => !isAlreadyApplied(gap, cid))}
                    {#if unapplied.length > 0}
                      <div>
                        <div class="text-xs font-medium mb-1" style="color: var(--color-text-tertiary);">Apply a Control to Reduce Risk</div>
                        <div class="flex flex-wrap gap-2">
                          {#each unapplied as controlId}
                            {@const key = `${gap.requirement_id}:${controlId}`}
                            {@const isApplying = applyingControlId === key}
                            {@const justApplied = appliedFlash === key}
                            <button
                              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer transition-all"
                              style="background: {justApplied ? 'var(--color-status-success)15' : 'var(--color-bg-surface-hover)'}; color: {justApplied ? 'var(--color-status-success)' : 'var(--color-accent-primary)'}; border: 1px solid {justApplied ? 'var(--color-status-success)' : 'var(--color-accent-primary)30'};"
                              onclick={() => applyControl(gap, controlId)}
                              disabled={isApplying}
                            >
                              {#if isApplying}
                                <Loader2 class="w-3 h-3 animate-spin" />
                                Applying...
                              {:else if justApplied}
                                <Check class="w-3 h-3" />
                                Applied!
                              {:else}
                                <Plus class="w-3 h-3" />
                                {getControlName(controlId)}
                              {/if}
                            </button>
                          {/each}
                        </div>
                      </div>
                    {/if}
                  {:else if !analysis.is_legacy && gap.applied_controls.length === 0}
                    <div class="flex items-center gap-2 text-xs" style="color: var(--color-text-tertiary);">
                      <AlertTriangle class="w-3 h-3" />
                      <span>Requires direct implementation — update status in Requirements tab when done</span>
                    </div>
                  {/if}
                  <!-- TARA evidence -->
                  {#if gap.tara_evidence.length > 0}
                    <div class="text-xs" style="color: var(--color-text-tertiary);">
                      TARA: {gap.tara_evidence[0].count} {gap.tara_evidence[0].type}(s) linked
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Compliant Requirements (collapsed) -->
    {#if getCompliant().length > 0}
      <details class="rounded-lg border overflow-hidden" style="border-color: var(--color-border-default);">
        <summary class="px-4 py-3 cursor-pointer" style="background: var(--color-bg-surface-hover);">
          <span class="text-sm font-semibold" style="color: var(--color-text-primary);">
            Compliant Requirements ({getCompliant().length})
          </span>
        </summary>
        <div class="divide-y" style="border-color: var(--color-border-subtle);">
          {#each getCompliant() as req (req.requirement_id)}
            <div class="px-4 py-3 flex items-center justify-between" style="background: var(--color-bg-surface);">
              <div>
                <span class="text-xs font-mono" style="color: var(--color-text-tertiary);">{req.requirement_id}</span>
                <span class="text-sm ml-2" style="color: var(--color-text-primary);">{req.requirement_name}</span>
              </div>
              <div class="flex items-center gap-2">
                <ShieldCheck class="w-4 h-4" style="color: var(--color-status-success);" />
                <span class="text-xs" style="color: var(--color-text-tertiary);">
                  {STATUS_LABELS[req.status] ?? req.status}
                </span>
                {#if req.tara_evidence.length > 0}
                  <span class="text-xs" style="color: var(--color-accent-primary);">
                    ({req.tara_evidence[0].count} {req.tara_evidence[0].type}s)
                  </span>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </details>
    {/if}
  {/if}
</div>
