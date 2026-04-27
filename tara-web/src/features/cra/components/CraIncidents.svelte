<script lang="ts">
  /**
   * CRA Art. 14 — incident list with countdown clocks, create, expand-to-edit,
   * and submit-phase actions. Uses CraIncidentClock for live countdowns and
   * CraIncidentEditor for the inline edit form.
   */
  import { onMount } from 'svelte';
  import { craApi } from '$lib/api/craApi';
  import type {
    CraIncident, IncidentCreateRequest, IncidentType, IncidentSeverity,
    DeadlinePhase,
  } from '$lib/types/cra';
  import CraIncidentClock from './CraIncidentClock.svelte';
  import CraIncidentEditor from './CraIncidentEditor.svelte';
  import {
    Plus, AlertTriangle, ChevronDown, ChevronRight, ShieldAlert,
    Trash2, Download,
  } from '@lucide/svelte';

  interface Props {
    assessmentId: string;
    onupdate?: () => void;
  }

  let { assessmentId, onupdate }: Props = $props();

  let incidents: CraIncident[] = $state([]);
  let loading = $state(true);
  let error: string | null = $state(null);
  let showCreate = $state(false);
  let saving = $state(false);
  let expandedId: string | null = $state(null);
  let submittingPhase: { id: string; phase: DeadlinePhase } | null = $state(null);
  let exportingPhase: { id: string; phase: DeadlinePhase } | null = $state(null);

  const initialNewIncident: IncidentCreateRequest = {
    title: '',
    incident_type: 'actively_exploited_vulnerability',
    discovered_at: new Date().toISOString(),
    assessment_id: assessmentId,
    severity: 'high',
    actively_exploited: true,
  };
  let newIncident: IncidentCreateRequest = $state({ ...initialNewIncident });

  async function load(): Promise<void> {
    loading = true;
    error = null;
    try {
      const res = await craApi.listIncidents({ assessmentId });
      incidents = [...res.incidents];
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load incidents';
    } finally {
      loading = false;
    }
  }

  onMount(() => { load(); });

  function resetCreateForm(): void {
    newIncident = { ...initialNewIncident, discovered_at: new Date().toISOString() };
    showCreate = false;
  }

  async function createIncident(): Promise<void> {
    if (!newIncident.title.trim()) return;
    saving = true;
    error = null;
    try {
      const created = await craApi.createIncident(newIncident);
      resetCreateForm();
      expandedId = created.id;
      await load();
      onupdate?.();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to create incident';
    } finally {
      saving = false;
    }
  }

  async function submitPhase(incident: CraIncident, phase: DeadlinePhase): Promise<void> {
    const phaseLabel = PHASE_LABELS[phase];
    if (!confirm(
      `Submit ${phaseLabel} to ENISA?\n\nThis records the submission timestamp and locks the phase. ` +
      `The submission to the Single Reporting Platform itself is performed outside this tool.`
    )) return;
    submittingPhase = { id: incident.id, phase };
    try {
      await craApi.submitIncidentPhase(incident.id, phase);
      await load();
      onupdate?.();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to submit phase';
    } finally {
      submittingPhase = null;
    }
  }

  async function exportEnisa(incident: CraIncident, phase: DeadlinePhase): Promise<void> {
    exportingPhase = { id: incident.id, phase };
    try {
      const data = await craApi.getEnisaExport(incident.id, phase);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `incident-${incident.id}-${phase}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to export';
    } finally {
      exportingPhase = null;
    }
  }

  async function deleteIncident(incident: CraIncident): Promise<void> {
    if (incident.status !== 'draft') return;
    if (!confirm('Delete this draft incident? This cannot be undone.')) return;
    try {
      await craApi.deleteIncident(incident.id);
      if (expandedId === incident.id) expandedId = null;
      await load();
      onupdate?.();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to delete';
    }
  }

  function findDeadline(incident: CraIncident, phase: DeadlinePhase) {
    return incident.deadlines.find(d => d.phase === phase);
  }

  const PHASE_LABELS: Record<DeadlinePhase, string> = {
    early_warning: 'Early Warning (24h)',
    incident_report: 'Incident Report (72h)',
    final_report: 'Final Report (14d)',
  };

  const TYPE_LABELS: Record<IncidentType, string> = {
    actively_exploited_vulnerability: 'Exploited Vulnerability',
    severe_incident: 'Severe Incident',
  };

  const SEVERITY_COLORS: Record<IncidentSeverity, string> = {
    critical: '#dc2626',
    high: '#f87171',
    medium: '#fbbf24',
    low: '#34d399',
  };

  const STATUS_LABELS: Record<string, string> = {
    draft: 'Draft',
    early_warning_submitted: 'Early Warning Sent',
    incident_report_submitted: 'Incident Report Sent',
    final_report_submitted: 'Final Report Sent',
    closed: 'Closed',
  };

  function nextPhase(incident: CraIncident): DeadlinePhase | null {
    if (!incident.early_warning_submitted_at) return 'early_warning';
    if (!incident.incident_report_submitted_at) return 'incident_report';
    if (!incident.final_report_submitted_at) return 'final_report';
    return null;
  }
</script>

<div class="space-y-4">
  <!-- Header -->
  <div class="rounded-lg border p-4" style="background: var(--color-bg-surface); border-color: var(--color-border-default);">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h2 class="text-sm font-semibold flex items-center gap-2" style="color: var(--color-text-primary);">
          <ShieldAlert class="w-4 h-4" style="color: var(--color-status-error);" />
          Incident Reports
        </h2>
        <p class="text-xs mt-1" style="color: var(--color-text-secondary);">
          CRA Art. 14 — manufacturers must notify ENISA within
          <strong>24h</strong> of becoming aware of an actively-exploited vulnerability or severe incident,
          a follow-up <strong>incident report within 72h</strong>, and a
          <strong>final report within 14 days</strong> of the corrective measure being available.
        </p>
      </div>
      <button
        class="inline-flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium cursor-pointer"
        style="background: var(--color-status-error); color: white;"
        onclick={() => { showCreate = true; }}
      >
        <Plus class="w-3.5 h-3.5" />
        Report Incident
      </button>
    </div>

    {#if error}
      <div class="mt-3 rounded-md p-3 flex items-start gap-2.5" role="alert" style="background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.35);">
        <AlertTriangle class="w-4 h-4 flex-shrink-0 mt-0.5" style="color: var(--color-status-error);" />
        <div class="text-xs" style="color: var(--color-status-error);">{error}</div>
      </div>
    {/if}
  </div>

  <!-- Create form -->
  {#if showCreate}
    <div class="rounded-lg border p-4 space-y-3" style="background: var(--color-bg-surface); border-color: var(--color-status-error);">
      <h3 class="text-sm font-semibold" style="color: var(--color-status-error);">New Incident</h3>
      <div class="grid grid-cols-2 gap-3">
        <label class="block col-span-2">
          <span class="block text-xs mb-1" style="color: var(--color-text-secondary);">Title *</span>
          <input
            type="text"
            class="w-full rounded border px-2.5 py-1.5 text-sm"
            style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
            bind:value={newIncident.title}
            placeholder="e.g. CVE-2026-1234 RCE in firmware update path"
          />
        </label>
        <label class="block">
          <span class="block text-xs mb-1" style="color: var(--color-text-secondary);">Type *</span>
          <select
            class="w-full rounded border px-2.5 py-1.5 text-sm"
            style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
            bind:value={newIncident.incident_type}
          >
            <option value="actively_exploited_vulnerability">Exploited Vulnerability (Art. 14(1))</option>
            <option value="severe_incident">Severe Incident (Art. 14(4))</option>
          </select>
        </label>
        <label class="block">
          <span class="block text-xs mb-1" style="color: var(--color-text-secondary);">Severity</span>
          <select
            class="w-full rounded border px-2.5 py-1.5 text-sm"
            style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
            bind:value={newIncident.severity}
          >
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>
        <label class="block col-span-2">
          <span class="block text-xs mb-1" style="color: var(--color-text-secondary);">
            Discovered at (UTC) — <em>this starts the 24h clock</em>
          </span>
          <input
            type="datetime-local"
            step="1"
            class="w-full rounded border px-2.5 py-1.5 text-sm"
            style="background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);"
            value={newIncident.discovered_at.slice(0, 19)}
            onchange={(e) => {
              const v = (e.target as HTMLInputElement).value;
              newIncident.discovered_at = v ? new Date(v + 'Z').toISOString() : new Date().toISOString();
            }}
          />
        </label>
        <label class="flex items-center gap-2 col-span-2 text-xs" style="color: var(--color-text-secondary);">
          <input type="checkbox" bind:checked={newIncident.actively_exploited} />
          Actively exploited (Art. 14(2)(a))
        </label>
      </div>
      <div class="flex justify-end gap-2">
        <button
          class="px-3 py-1.5 rounded text-xs cursor-pointer"
          style="background: var(--color-bg-surface-hover); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
          onclick={resetCreateForm}
          disabled={saving}
        >
          Cancel
        </button>
        <button
          class="px-3 py-1.5 rounded text-xs font-medium cursor-pointer disabled:opacity-50"
          style="background: var(--color-status-error); color: white;"
          onclick={createIncident}
          disabled={saving || !newIncident.title.trim()}
        >
          {saving ? 'Creating…' : 'Create Draft'}
        </button>
      </div>
    </div>
  {/if}

  <!-- List -->
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div role="status" class="animate-spin rounded-full h-5 w-5 border-2 border-t-transparent" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
    </div>
  {:else if incidents.length === 0}
    <div class="rounded-xl border border-dashed py-16 text-center" style="border-color: var(--color-border-default);">
      <ShieldAlert class="w-8 h-8 mx-auto mb-2" style="color: var(--color-text-tertiary);" />
      <h3 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">No incidents reported</h3>
      <p class="text-xs max-w-sm mx-auto" style="color: var(--color-text-tertiary);">
        Click <em>Report Incident</em> the moment you become aware of an actively-exploited vulnerability —
        the 24-hour clock starts at discovery, not at draft creation.
      </p>
    </div>
  {:else}
    <div class="space-y-3">
      {#each incidents as incident (incident.id)}
        {@const isOpen = expandedId === incident.id}
        {@const ew = findDeadline(incident, 'early_warning')}
        {@const ir = findDeadline(incident, 'incident_report')}
        {@const fr = findDeadline(incident, 'final_report')}
        {@const next = nextPhase(incident)}
        <div
          class="rounded-lg border overflow-hidden"
          style="background: var(--color-bg-surface); border-color: {incident.overall_overdue ? 'var(--color-status-error)' : 'var(--color-border-default)'};"
        >
          <div class="flex items-stretch">
            <button
              type="button"
              class="flex-1 min-w-0 text-left px-4 py-3 flex flex-col gap-2 cursor-pointer hover:bg-[var(--color-bg-surface-hover)]"
              onclick={() => { expandedId = isOpen ? null : incident.id; }}
              aria-expanded={isOpen}
            >
              <div class="flex items-center gap-2 min-w-0">
                {#if isOpen}<ChevronDown class="w-4 h-4 flex-shrink-0" style="color: var(--color-text-tertiary);" />
                {:else}<ChevronRight class="w-4 h-4 flex-shrink-0" style="color: var(--color-text-tertiary);" />{/if}
                <div class="text-sm font-medium truncate" style="color: var(--color-text-primary);">
                  {incident.title}
                </div>
                {#if incident.severity}
                  <span class="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded font-semibold" style="background: {SEVERITY_COLORS[incident.severity]}20; color: {SEVERITY_COLORS[incident.severity]};">
                    {incident.severity}
                  </span>
                {/if}
              </div>
              <div class="flex items-center gap-3 text-xs" style="color: var(--color-text-tertiary);">
                <span>{TYPE_LABELS[incident.incident_type]}</span>
                {#if incident.cve_id}<span class="font-mono">{incident.cve_id}</span>{/if}
                <span>{STATUS_LABELS[incident.status] ?? incident.status}</span>
                <span>Discovered {new Date(incident.discovered_at).toLocaleString('en-GB')}</span>
              </div>
              <div class="flex flex-wrap gap-2 mt-1">
                {#if ew}<CraIncidentClock deadline={ew} label="24h" />{/if}
                {#if ir}<CraIncidentClock deadline={ir} label="72h" />{/if}
                {#if fr}<CraIncidentClock deadline={fr} label="14d" />{/if}
              </div>
            </button>
            {#if incident.status === 'draft'}
              <button
                type="button"
                class="flex-shrink-0 px-3 cursor-pointer hover:bg-[rgba(239,68,68,0.1)]"
                style="color: var(--color-status-error);"
                onclick={() => deleteIncident(incident)}
                aria-label="Delete draft"
                title="Delete draft"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            {/if}
          </div>

          {#if isOpen}
            <div class="border-t px-4 py-4 space-y-4" style="border-color: var(--color-border-subtle); background: var(--color-bg-elevated);">
              <CraIncidentEditor
                {incident}
                onsaved={load}
              />

              <div class="flex flex-wrap gap-2 pt-2 border-t" style="border-color: var(--color-border-subtle);">
                {#if next}
                  <button
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer disabled:opacity-50"
                    style="background: var(--color-status-error); color: white;"
                    onclick={() => submitPhase(incident, next)}
                    disabled={submittingPhase?.id === incident.id}
                  >
                    {submittingPhase?.id === incident.id && submittingPhase?.phase === next
                      ? 'Submitting…'
                      : `Mark ${PHASE_LABELS[next]} Submitted`}
                  </button>
                {/if}
                {#each (['early_warning', 'incident_report', 'final_report'] as DeadlinePhase[]) as phase}
                  <button
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs cursor-pointer disabled:opacity-50"
                    style="background: var(--color-bg-surface-hover); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
                    onclick={() => exportEnisa(incident, phase)}
                    disabled={exportingPhase?.id === incident.id}
                  >
                    <Download class="w-3 h-3" />
                    Export {PHASE_LABELS[phase]} JSON
                  </button>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
