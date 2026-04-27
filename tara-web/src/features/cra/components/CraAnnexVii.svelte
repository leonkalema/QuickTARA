<script lang="ts">
  /**
   * CRA Annex VII — Technical documentation preview.
   * Regulation (EU) 2024/2847, Annex VII (seven mandatory sections).
   * Pulls the auto-generated document from the backend and exposes a
   * one-click Markdown download for notified-body submission.
   */
  import { onMount } from 'svelte';
  import { craApi } from '$lib/api/craApi';
  import type { AnnexViiDocument } from '$lib/types/cra';
  import { FileText, Download, RefreshCw, AlertTriangle, CheckCircle2 } from '@lucide/svelte';

  interface Props {
    assessmentId: string;
  }

  let { assessmentId }: Props = $props();

  let doc: AnnexViiDocument | null = $state(null);
  let loading = $state(true);
  let error: string | null = $state(null);
  let downloading = $state(false);
  let expanded: Record<string, boolean> = $state({});

  onMount(() => { load(); });

  async function load(): Promise<void> {
    loading = true;
    error = null;
    try {
      doc = await craApi.getAnnexVii(assessmentId);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load Annex VII';
    } finally {
      loading = false;
    }
  }

  async function download(): Promise<void> {
    if (!doc) return;
    downloading = true;
    try {
      await craApi.downloadAnnexViiMarkdown(assessmentId, doc.product_name);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Download failed';
    } finally {
      downloading = false;
    }
  }

  function toggle(sectionNumber: string): void {
    expanded[sectionNumber] = !expanded[sectionNumber];
  }

  const completenessColor = $derived.by(() => {
    if (!doc) return 'var(--color-text-secondary)';
    if (doc.completeness_pct >= 80) return 'var(--color-status-success)';
    if (doc.completeness_pct >= 50) return '#fbbf24';
    return 'var(--color-status-error)';
  });

  const actionCount: number = $derived.by(() => {
    if (!doc) return 0;
    return doc.sections.filter((s) => s.is_action_required).length;
  });
</script>

<div class="space-y-4">
  <!-- Header -->
  <div class="flex items-center justify-between gap-3">
    <div class="flex items-center gap-2">
      <FileText class="w-5 h-5" style="color: var(--color-accent-primary);" />
      <h2 class="text-lg font-semibold" style="color: var(--color-text-primary);">
        Annex VII — Technical Documentation
      </h2>
    </div>
    <div class="flex items-center gap-2">
      <button
        class="flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs cursor-pointer"
        style="background: var(--color-bg-surface); color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
        onclick={load}
        disabled={loading}
        title="Rebuild from current data"
      >
        <RefreshCw class="w-3.5 h-3.5 {loading ? 'animate-spin' : ''}" />
        Refresh
      </button>
      <button
        class="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer disabled:opacity-50"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        onclick={download}
        disabled={!doc || downloading}
      >
        <Download class="w-3.5 h-3.5" />
        {downloading ? 'Downloading…' : 'Download Markdown'}
      </button>
    </div>
  </div>

  <p class="text-xs" style="color: var(--color-text-secondary);">
    Auto-generated from your product scope, TARA artefacts, requirement statuses,
    compensating controls, and SBOMs. Regeneration reflects the latest data on
    every refresh. Regulation (EU) 2024/2847, Annex VII.
  </p>

  {#if loading && !doc}
    <div class="flex items-center justify-center py-12">
      <div
        class="animate-spin rounded-full h-6 w-6 border-2 border-t-transparent"
        style="border-color: var(--color-accent-primary); border-top-color: transparent;"
      ></div>
    </div>
  {:else if error}
    <div
      class="rounded p-3 text-xs"
      style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.35); color: var(--color-status-error);"
    >
      {error}
    </div>
  {:else if doc}
    <!-- Metadata + completeness -->
    <div
      class="rounded border p-4 grid grid-cols-1 md:grid-cols-3 gap-4"
      style="background: var(--color-bg-surface); border-color: var(--color-border-subtle);"
    >
      <div class="md:col-span-2 space-y-1.5 text-xs" style="color: var(--color-text-secondary);">
        <div>
          <span class="inline-block w-36 font-semibold" style="color: var(--color-text-primary);">Product</span>
          {doc.product_name}
        </div>
        <div>
          <span class="inline-block w-36 font-semibold" style="color: var(--color-text-primary);">Classification</span>
          {doc.classification || '—'}
        </div>
        <div>
          <span class="inline-block w-36 font-semibold" style="color: var(--color-text-primary);">Conformity route</span>
          {doc.conformity_assessment || '—'}
        </div>
        <div>
          <span class="inline-block w-36 font-semibold" style="color: var(--color-text-primary);">Support period</span>
          {doc.support_period_years !== null ? `${doc.support_period_years} years` : '—'}
        </div>
        <div>
          <span class="inline-block w-36 font-semibold" style="color: var(--color-text-primary);">Compliance deadline</span>
          {doc.compliance_deadline || '—'}
        </div>
      </div>
      <div class="flex flex-col items-start md:items-end justify-center gap-1">
        <span class="text-[10px] uppercase tracking-wider" style="color: var(--color-text-secondary);">
          Completeness
        </span>
        <span class="text-3xl font-bold tabular-nums" style="color: {completenessColor};">
          {doc.completeness_pct}%
        </span>
        {#if actionCount > 0}
          <span class="text-[11px]" style="color: var(--color-text-secondary);">
            {actionCount} section{actionCount === 1 ? '' : 's'} need input
          </span>
        {:else}
          <span class="text-[11px] flex items-center gap-1" style="color: var(--color-status-success);">
            <CheckCircle2 class="w-3.5 h-3.5" /> All sections have data
          </span>
        {/if}
      </div>
    </div>

    <!-- Appendix counts -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      {#each [
        { label: 'Assets', value: doc.assets.length },
        { label: 'Damage scenarios', value: doc.damage_scenarios.length },
        { label: 'Compensating controls', value: doc.compensating_controls.length },
        { label: 'SBOMs', value: doc.sboms.length },
      ] as card}
        <div
          class="rounded p-3"
          style="background: var(--color-bg-surface); border: 1px solid var(--color-border-subtle);"
        >
          <div class="text-xs" style="color: var(--color-text-secondary);">{card.label}</div>
          <div class="text-xl font-bold tabular-nums" style="color: var(--color-text-primary);">
            {card.value}
          </div>
        </div>
      {/each}
    </div>

    <!-- Section list -->
    <div class="space-y-2">
      {#each doc.sections as section (section.number)}
        <div
          class="rounded border"
          style="background: var(--color-bg-surface); border-color: {section.is_action_required ? 'rgba(251,191,36,0.4)' : 'var(--color-border-subtle)'};"
        >
          <button
            type="button"
            class="w-full flex items-center gap-3 px-3 py-2.5 text-left cursor-pointer"
            onclick={() => toggle(section.number)}
          >
            <span
              class="inline-flex items-center justify-center w-6 h-6 rounded-full text-[11px] font-bold tabular-nums"
              style="background: {section.is_action_required ? 'rgba(251,191,36,0.15)' : 'rgba(52,211,153,0.12)'}; color: {section.is_action_required ? '#fbbf24' : '#34d399'};"
            >
              {section.number}
            </span>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium truncate" style="color: var(--color-text-primary);">
                {section.title}
              </div>
              <div class="text-[11px]" style="color: var(--color-text-secondary);">
                {section.article_ref}
              </div>
            </div>
            {#if section.is_action_required}
              <span class="flex items-center gap-1 text-[11px]" style="color: #fbbf24;">
                <AlertTriangle class="w-3.5 h-3.5" />
                Action required
              </span>
            {:else}
              <span class="flex items-center gap-1 text-[11px]" style="color: var(--color-status-success);">
                <CheckCircle2 class="w-3.5 h-3.5" />
                Data available
              </span>
            {/if}
          </button>
          {#if expanded[section.number]}
            <div
              class="px-3 py-3 border-t text-xs font-mono whitespace-pre-wrap"
              style="border-color: var(--color-border-subtle); color: var(--color-text-primary); background: var(--color-bg-base);"
            >{section.body}</div>
          {/if}
        </div>
      {/each}
    </div>

    <p class="text-[11px]" style="color: var(--color-text-secondary);">
      Generated {new Date(doc.generated_at).toLocaleString()} — the Markdown
      download includes all sections plus appendices A–D (assets, damage
      scenarios, requirement matrix, compensating controls, SBOMs).
    </p>
  {/if}
</div>
