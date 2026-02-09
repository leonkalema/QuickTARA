<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { craApi } from '$lib/api/craApi';
  import type { CraAssessment, ClassificationResult } from '$lib/types/cra';
  import CraRequirementsTable from '../../../features/cra/components/CraRequirementsTable.svelte';
  import CraCompensatingControls from '../../../features/cra/components/CraCompensatingControls.svelte';
  import CraInventory from '../../../features/cra/components/CraInventory.svelte';
  import CraClassificationWizard from '../../../features/cra/components/CraClassificationWizard.svelte';
  import CraGapAnalysis from '../../../features/cra/components/CraGapAnalysis.svelte';
  import CraClassificationImpact from '../../../features/cra/components/CraClassificationImpact.svelte';
  import {
    ArrowLeft, Shield, Calendar, Wand2, Trash2,
    FileText, ShieldCheck, Settings2, BarChart3, X, Check, Package
  } from '@lucide/svelte';

  let assessment: CraAssessment | null = $state(null);
  let loading = $state(true);
  let error: string | null = $state(null);
  let activeTab: 'overview' | 'requirements' | 'controls' | 'gap_analysis' | 'inventory' = $state('overview');
  let showClassifyWizard = $state(false);
  let autoMapping = $state(false);
  let deleting = $state(false);
  let autoMapResult: { mapped: number; total: number } | null = $state(null);
  let nextStepsDismissed = $state(false);

  const assessmentId: string = $derived($page.params.id ?? '');

  function isLegacyProduct(): boolean {
    if (!assessment) return false;
    return assessment.product_type === 'legacy_b' || assessment.product_type === 'legacy_c';
  }

  function isCurrentProduct(): boolean {
    if (!assessment) return false;
    return assessment.product_type === 'current';
  }

  function hasAutoMappedReqs(): boolean {
    if (!assessment) return false;
    return assessment.requirement_statuses.some(r => r.auto_mapped);
  }


  onMount(() => loadAssessment());

  async function loadAssessment(): Promise<void> {
    loading = true;
    error = null;
    try {
      if (assessmentId) assessment = await craApi.getAssessment(assessmentId);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load assessment';
    } finally {
      loading = false;
    }
  }

  async function runAutoMap(): Promise<void> {
    autoMapping = true;
    autoMapResult = null;
    try {
      if (assessmentId) {
        const result = await craApi.autoMap(assessmentId);
        autoMapResult = { mapped: result.mapped_count, total: 18 };
      }
      await loadAssessment();
    } catch (err) {
      console.error('Auto-map failed:', err);
      error = 'Auto-map failed. Make sure this product has TARA data (assets, damage scenarios).';
    } finally {
      autoMapping = false;
    }
  }

  async function deleteAssessment(): Promise<void> {
    if (!confirm('Delete this CRA assessment? This cannot be undone.')) return;
    deleting = true;
    try {
      if (assessmentId) await craApi.deleteAssessment(assessmentId);
      await goto('/cra');
    } catch (err) {
      console.error('Delete failed:', err);
    } finally {
      deleting = false;
    }
  }

  function onClassificationComplete(result: ClassificationResult): void {
    showClassifyWizard = false;
    loadAssessment();
  }

  function getComplianceColor(pct: number): string {
    if (pct >= 80) return 'var(--color-status-success)';
    if (pct >= 40) return 'var(--color-status-warning)';
    return 'var(--color-status-error)';
  }

  function formatDeadline(d?: string): string {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  }

  function getDeadlineColor(): string {
    if (!assessment?.compliance_deadline) return 'var(--color-text-tertiary)';
    const months = Math.round((new Date(assessment.compliance_deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24 * 30));
    if (months <= 0) return '#dc2626';
    if (months <= 6) return 'var(--color-status-error)';
    if (months <= 12) return 'var(--color-status-warning)';
    return 'var(--color-text-primary)';
  }

  const CLASSIFICATION_LABELS: Record<string, string> = {
    default: 'Default', class_i: 'Class I', class_ii: 'Class II', critical: 'Critical',
  };
  const CLASSIFICATION_COLORS: Record<string, string> = {
    default: 'var(--color-status-info)', class_i: 'var(--color-status-warning)',
    class_ii: 'var(--color-status-error)', critical: '#dc2626',
  };
  const PRODUCT_TYPE_LABELS: Record<string, string> = {
    current: 'Current Product', legacy_a: 'Legacy A — Maintainable',
    legacy_b: 'Legacy B — Partial', legacy_c: 'Legacy C — Orphaned',
  };
  const STATUS_LABELS: Record<string, string> = {
    draft: 'Draft', in_progress: 'In Progress', complete: 'Complete',
  };

  const tabs: Array<{ id: 'overview' | 'requirements' | 'controls' | 'gap_analysis' | 'inventory'; label: string; icon: any }> = $derived([
    { id: 'overview' as const, label: 'Overview', icon: FileText },
    { id: 'requirements' as const, label: 'Requirements', icon: ShieldCheck },
    { id: 'gap_analysis' as const, label: 'Gap Analysis', icon: BarChart3 },
    ...(isLegacyProduct() ? [{ id: 'controls' as const, label: 'Compensating Controls', icon: Settings2 }] : []),
    ...(isLegacyProduct() ? [{ id: 'inventory' as const, label: 'Inventory', icon: Package }] : []),
  ]);
</script>

{#if loading}
  <div class="flex items-center justify-center py-16">
    <div class="animate-spin rounded-full h-6 w-6 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
  </div>
{:else if error}
  <div class="space-y-4">
    <button class="inline-flex items-center gap-1 text-sm cursor-pointer" style="color: var(--color-text-secondary);" onclick={() => goto('/cra')}>
      <ArrowLeft class="w-4 h-4" /> Back
    </button>
    <div class="rounded-lg border p-4 text-sm" style="background: var(--color-status-error)10; border-color: var(--color-status-error); color: var(--color-status-error);">
      {error}
    </div>
  </div>
{:else if showClassifyWizard}
  <div class="space-y-4">
    <button class="inline-flex items-center gap-1 text-sm cursor-pointer" style="color: var(--color-text-secondary);" onclick={() => { showClassifyWizard = false; }}>
      <ArrowLeft class="w-4 h-4" /> Back to Assessment
    </button>
    <CraClassificationWizard
      {assessmentId}
      oncomplete={onClassificationComplete}
      oncancel={() => { showClassifyWizard = false; }}
    />
  </div>
{:else if assessment}
  <div class="space-y-6">
    <!-- Back + Actions -->
    <div class="flex items-center justify-between">
      <button class="inline-flex items-center gap-1 text-sm cursor-pointer" style="color: var(--color-text-secondary);" onclick={() => goto('/cra')}>
        <ArrowLeft class="w-4 h-4" /> Back to Assessments
      </button>
      <div class="flex items-center gap-2">
        {#if isCurrentProduct()}
          <div class="relative group">
            <button
              class="inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium cursor-pointer transition-colors"
              style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
              onclick={runAutoMap}
              disabled={autoMapping}
            >
              <Wand2 class="w-3 h-3" />
              {#if autoMapping}
                Scanning TARA...
              {:else if hasAutoMappedReqs()}
                Re-sync with TARA
              {:else}
                Link to TARA
              {/if}
            </button>
            <!-- Tooltip -->
            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 rounded-lg text-xs w-64 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-opacity z-10" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default); color: var(--color-text-secondary); box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
              <strong style="color: var(--color-text-primary);">What this does:</strong>
              <p class="mt-1">Scans your existing TARA work (assets, damage scenarios, threat scenarios) and automatically marks CRA requirements that are already addressed.</p>
              {#if hasAutoMappedReqs()}
                <p class="mt-1 flex items-center gap-1" style="color: var(--color-accent-primary);"><Check class="w-3.5 h-3.5" /> {assessment?.requirement_statuses.filter(r => r.auto_mapped).length} requirements already linked</p>
              {/if}
            </div>
          </div>
        {:else}
          <span class="inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs" style="background: var(--color-bg-surface-hover); color: var(--color-text-tertiary);">
            <Wand2 class="w-3 h-3" />
            TARA link N/A (legacy product)
          </span>
        {/if}
        {#if !assessment.classification}
          <button
            class="inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
            style="background: var(--color-bg-surface-hover); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
            onclick={() => { showClassifyWizard = true; }}
          >
            <Shield class="w-3 h-3" />
            Classify Product
          </button>
        {/if}
        <button
          class="inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium cursor-pointer"
          style="color: var(--color-status-error);"
          onclick={deleteAssessment}
          disabled={deleting}
        >
          <Trash2 class="w-3 h-3" />
        </button>
      </div>
    </div>

    <!-- Header -->
    <div class="rounded-lg border p-5" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
      <div class="flex items-start justify-between mb-4">
        <div>
          <h1 class="text-lg font-bold" style="color: var(--color-text-primary);">
            {assessment.product_name ?? assessment.product_id}
          </h1>
          <div class="flex items-center gap-3 mt-1">
            <span class="text-xs px-2 py-0.5 rounded" style="background: var(--color-bg-surface-hover); color: var(--color-text-secondary);">
              {PRODUCT_TYPE_LABELS[assessment.product_type] ?? assessment.product_type}
            </span>
            <span class="text-xs px-2 py-0.5 rounded" style="background: var(--color-bg-surface-hover); color: var(--color-text-secondary);">
              {STATUS_LABELS[assessment.status] ?? assessment.status}
            </span>
          </div>
        </div>
        {#if assessment.classification}
          {@const clsColor = CLASSIFICATION_COLORS[assessment.classification] ?? 'var(--color-text-secondary)'}
          <span class="inline-flex items-center gap-1 px-3 py-1 rounded-lg text-sm font-semibold" style="background: {clsColor}15; color: {clsColor};">
            <Shield class="w-4 h-4" />
            {CLASSIFICATION_LABELS[assessment.classification] ?? assessment.classification}
          </span>
        {/if}
      </div>

      <!-- Stats row -->
      <div class="grid grid-cols-4 gap-4">
        <div>
          <div class="text-xs mb-1" style="color: var(--color-text-tertiary);">Compliance</div>
          <div class="flex items-center gap-2">
            <div class="flex-1 h-2 rounded-full" style="background: var(--color-bg-surface-hover);">
              <div class="h-2 rounded-full transition-all" style="width: {assessment.overall_compliance_pct}%; background: {getComplianceColor(assessment.overall_compliance_pct)};"></div>
            </div>
            <span class="text-sm font-bold" style="color: {getComplianceColor(assessment.overall_compliance_pct)};">
              {assessment.overall_compliance_pct}%
            </span>
          </div>
        </div>
        <div>
          <div class="text-xs mb-1" style="color: var(--color-text-tertiary);">Conformity Path</div>
          <div class="text-sm font-medium" style="color: {assessment.classification === 'critical' ? '#dc2626' : assessment.classification === 'class_ii' ? 'var(--color-status-error)' : assessment.classification === 'class_i' ? 'var(--color-status-warning)' : 'var(--color-status-success)'};">
            {assessment.classification === 'critical' ? 'EU Certification' : assessment.classification === 'class_ii' ? 'Third-Party' : assessment.classification === 'class_i' ? 'Self + Standards' : assessment.classification ? 'Self-Assessment' : 'Not classified'}
          </div>
        </div>
        <div>
          <div class="text-xs mb-1" style="color: var(--color-text-tertiary);">Deadline</div>
          <div class="flex items-center gap-1 text-sm font-medium" style="color: {getDeadlineColor()};">
            <Calendar class="w-3.5 h-3.5" />
            {formatDeadline(assessment.compliance_deadline)}
          </div>
        </div>
        <div>
          <div class="text-xs mb-1" style="color: var(--color-text-tertiary);">Requirements</div>
          <div class="text-sm font-medium" style="color: var(--color-text-primary);">
            {assessment.requirement_statuses.filter(r => r.status === 'compliant' || r.status === 'not_applicable').length}
            / {assessment.requirement_statuses.length} done
          </div>
        </div>
      </div>
    </div>

    <!-- Auto-map result banner -->
    {#if autoMapResult}
      <div class="rounded-lg border p-4 flex items-center justify-between" style="background: var(--color-status-success)10; border-color: var(--color-status-success);">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full flex items-center justify-center" style="background: var(--color-status-success)20;">
            <Wand2 class="w-4 h-4" style="color: var(--color-status-success);" />
          </div>
          <div>
            <div class="text-sm font-medium" style="color: var(--color-status-success);">
              TARA Sync Complete
            </div>
            <div class="text-xs" style="color: var(--color-text-secondary);">
              {autoMapResult.mapped} of {autoMapResult.total} requirements linked to existing TARA artifacts
            </div>
          </div>
        </div>
        <button
          class="text-xs px-2 py-1 rounded cursor-pointer"
          style="color: var(--color-text-tertiary);"
          onclick={() => { autoMapResult = null; }}
        >
          Dismiss
        </button>
      </div>
    {/if}

    <!-- Tabs -->
    <div class="flex gap-1 border-b" style="border-color: var(--color-border-default);">
      {#each tabs as tab}
        <button
          class="inline-flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors cursor-pointer"
          style="
            border-color: {activeTab === tab.id ? 'var(--color-accent-primary)' : 'transparent'};
            color: {activeTab === tab.id ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)'};
          "
          onclick={() => { activeTab = tab.id; }}
        >
          <tab.icon class="w-4 h-4" />
          {tab.label}
        </button>
      {/each}
    </div>

    <!-- Tab content -->
    {#if activeTab === 'overview'}
      <!-- Next Steps guidance -->
      {@const completedReqs = assessment.requirement_statuses.filter(r => r.status === 'compliant' || r.status === 'not_applicable').length}
      {@const totalReqs = assessment.requirement_statuses.length}
      {@const hasCompensatingControls = assessment.compensating_controls.length > 0}
      {@const isLegacyC = assessment.product_type === 'legacy_c'}

      {#if !nextStepsDismissed && (completedReqs < totalReqs || (isLegacyC && !hasCompensatingControls))}
        <div class="rounded-lg border p-5 mb-6 relative" style="background: var(--color-accent-primary)08; border-color: var(--color-accent-primary);">
          <button
            class="absolute top-3 right-3 p-1 rounded cursor-pointer transition-opacity opacity-50 hover:opacity-100"
            style="color: var(--color-text-tertiary);"
            onclick={() => { nextStepsDismissed = true; }}
            title="Dismiss"
          >
            <X class="w-4 h-4" />
          </button>
          <div class="text-sm font-semibold mb-3" style="color: var(--color-accent-primary);">
            📋 Next Steps
          </div>
          <div class="space-y-3">
            {#if completedReqs === 0}
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">1</div>
                <div>
                  <div class="text-sm font-medium" style="color: var(--color-text-primary);">Review Requirements</div>
                  <p class="text-xs mt-0.5" style="color: var(--color-text-secondary);">
                    Go to the <button class="underline cursor-pointer" onclick={() => { activeTab = 'requirements'; }}>Requirements tab</button> and update the status of each CRA requirement. Mark items as Compliant, Partial, or Not Applicable.
                  </p>
                </div>
              </div>
            {:else if completedReqs < totalReqs}
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0" style="background: var(--color-status-warning); color: var(--color-text-inverse);">!</div>
                <div>
                  <div class="text-sm font-medium" style="color: var(--color-text-primary);">Continue Requirements Review</div>
                  <p class="text-xs mt-0.5" style="color: var(--color-text-secondary);">
                    You've completed {completedReqs} of {totalReqs} requirements. <button class="underline cursor-pointer" onclick={() => { activeTab = 'requirements'; }}>Continue reviewing</button> and update remaining items.
                  </p>
                </div>
              </div>
            {/if}

            {#if isLegacyC && !hasCompensatingControls}
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0" style="background: var(--color-status-error); color: var(--color-text-inverse);">{completedReqs === 0 ? '2' : '!'}</div>
                <div>
                  <div class="text-sm font-medium" style="color: var(--color-text-primary);">Add Compensating Controls</div>
                  <p class="text-xs mt-0.5" style="color: var(--color-text-secondary);">
                    Legacy C products require Art. 5(3) compensating controls. Go to <button class="underline cursor-pointer" onclick={() => { activeTab = 'controls'; }}>Compensating Controls tab</button> and add measures like network segmentation, monitoring, or access restrictions.
                  </p>
                </div>
              </div>
            {:else if isLegacyC && hasCompensatingControls}
              <div class="flex items-start gap-3">
                <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style="background: var(--color-status-success); color: var(--color-text-inverse);"><Check class="w-3.5 h-3.5" /></div>
                <div>
                  <div class="text-sm font-medium" style="color: var(--color-text-primary);">Compensating Controls Added</div>
                  <p class="text-xs mt-0.5" style="color: var(--color-text-secondary);">
                    {assessment.compensating_controls.length} compensating control(s) documented.
                  </p>
                </div>
              </div>
            {/if}
          </div>
        </div>
      {:else}
        <div class="rounded-lg border p-4 mb-6 flex items-center gap-3" style="background: var(--color-status-success)10; border-color: var(--color-status-success);">
          <div class="w-8 h-8 rounded-full flex items-center justify-center" style="background: var(--color-status-success)20;">
            <Shield class="w-4 h-4" style="color: var(--color-status-success);" />
          </div>
          <div>
            <div class="text-sm font-medium" style="color: var(--color-status-success);">Assessment Complete</div>
            <p class="text-xs" style="color: var(--color-text-secondary);">All requirements reviewed. Ready for report generation.</p>
          </div>
        </div>
      {/if}

      <div class="grid grid-cols-2 gap-4">
        <!-- Requirement summary by category -->
        {#each ['technical', 'process', 'documentation'] as category}
          {@const catReqs = assessment.requirement_statuses.filter(r => r.requirement_category === category)}
          {@const catDone = catReqs.filter(r => r.status === 'compliant' || r.status === 'not_applicable').length}
          <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
            <div class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--color-text-tertiary);">
              {category}
            </div>
            <div class="text-2xl font-bold mb-1" style="color: var(--color-text-primary);">
              {catDone}/{catReqs.length}
            </div>
            <div class="h-1.5 rounded-full" style="background: var(--color-bg-surface-hover);">
              <div
                class="h-1.5 rounded-full"
                style="width: {catReqs.length ? (catDone / catReqs.length) * 100 : 0}%; background: var(--color-accent-primary);"
              ></div>
            </div>
          </div>
        {/each}

        <!-- Auto-mapped summary -->
        <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--color-text-tertiary);">
            Auto-Mapped from TARA
          </div>
          <div class="text-2xl font-bold mb-1" style="color: var(--color-accent-primary);">
            {assessment.requirement_statuses.filter(r => r.auto_mapped).length}
          </div>
          <div class="text-xs" style="color: var(--color-text-secondary);">
            requirements linked to existing artifacts
          </div>
        </div>
      </div>

      <!-- Notes -->
      {#if assessment.notes}
        <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
          <div class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--color-text-tertiary);">Notes</div>
          <p class="text-sm" style="color: var(--color-text-secondary);">{assessment.notes}</p>
        </div>
      {/if}

      <!-- Classification impact -->
      {#if assessment.classification}
        <CraClassificationImpact
          classification={assessment.classification}
          productType={assessment.product_type}
          complianceDeadline={assessment.compliance_deadline}
          automotiveException={assessment.automotive_exception}
        />
      {:else}
        <div class="rounded-lg border border-dashed p-6 text-center" style="border-color: var(--color-border-default);">
          <Shield class="w-8 h-8 mx-auto mb-2" style="color: var(--color-text-tertiary);" />
          <p class="text-sm mb-3" style="color: var(--color-text-secondary);">Product not yet classified — classification determines your conformity path, deadline, and obligations.</p>
          <button
            class="px-4 py-2 rounded-lg text-sm font-medium cursor-pointer"
            style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
            onclick={() => { showClassifyWizard = true; }}
          >
            Run Classification Wizard
          </button>
        </div>
      {/if}
    {:else if activeTab === 'requirements'}
      <CraRequirementsTable
        requirements={assessment.requirement_statuses}
        onupdate={loadAssessment}
      />
    {:else if activeTab === 'gap_analysis'}
      <CraGapAnalysis
        assessmentId={assessment.id ?? ''}
        productName={assessment.product_name ?? assessment.product_id}
        classification={assessment.classification}
        complianceDeadline={assessment.compliance_deadline}
      />
    {:else if activeTab === 'controls'}
      <CraCompensatingControls
        assessmentId={assessment.id ?? ''}
        controls={assessment.compensating_controls}
        requirements={assessment.requirement_statuses}
        onupdate={loadAssessment}
      />
    {:else if activeTab === 'inventory'}
      <CraInventory
        assessmentId={assessment.id ?? ''}
        onupdate={loadAssessment}
      />
    {/if}
  </div>
{/if}
