<script lang="ts">
  /**
   * Phase-organised editor for one CRA Art. 14 incident. Each section maps
   * directly to a sub-paragraph of Art. 14(2): (a) early warning content,
   * (b) incident-report addenda, (c) final-report fields.
   */
  import { craApi } from '$lib/api/craApi';
  import type { CraIncident, IncidentUpdateRequest } from '$lib/types/cra';

  interface Props {
    incident: CraIncident;
    onsaved?: () => void;
  }

  let { incident, onsaved }: Props = $props();

  // Local working copy. Reset whenever incident.id changes.
  let working = $state(initWorking(incident));
  let savedKey = $state(incident.id + incident.updated_at);
  let saving = $state(false);
  let saveError: string | null = $state(null);
  let saveSuccess = $state(false);

  $effect(() => {
    const key = incident.id + incident.updated_at;
    if (key !== savedKey) {
      working = initWorking(incident);
      savedKey = key;
    }
  });

  function initWorking(i: CraIncident): IncidentUpdateRequest & {
    member_states_csv: string;
    corrective_local: string;
  } {
    return {
      title: i.title,
      severity: i.severity,
      actively_exploited: i.actively_exploited,
      product_description: i.product_description ?? '',
      vulnerability_nature: i.vulnerability_nature ?? '',
      mitigations_taken: i.mitigations_taken ?? '',
      mitigations_recommended: i.mitigations_recommended ?? '',
      vulnerability_description: i.vulnerability_description ?? '',
      impact_description: i.impact_description ?? '',
      malicious_actor_info: i.malicious_actor_info ?? '',
      fixes_applied: i.fixes_applied ?? '',
      cve_id: i.cve_id ?? '',
      notes: i.notes ?? '',
      member_states_csv: (i.member_states_affected ?? []).join(', '),
      corrective_local: i.corrective_measure_available_at
        ? i.corrective_measure_available_at.slice(0, 19)
        : '',
    };
  }

  async function save(): Promise<void> {
    saving = true;
    saveError = null;
    saveSuccess = false;
    try {
      const member_states = working.member_states_csv
        .split(',')
        .map((s) => s.trim().toUpperCase())
        .filter((s) => s.length === 2);

      const payload: IncidentUpdateRequest = {
        title: working.title,
        severity: working.severity,
        actively_exploited: working.actively_exploited,
        member_states_affected: member_states.length > 0 ? member_states : undefined,
        product_description: working.product_description || undefined,
        vulnerability_nature: working.vulnerability_nature || undefined,
        mitigations_taken: working.mitigations_taken || undefined,
        mitigations_recommended: working.mitigations_recommended || undefined,
        vulnerability_description: working.vulnerability_description || undefined,
        impact_description: working.impact_description || undefined,
        malicious_actor_info: working.malicious_actor_info || undefined,
        fixes_applied: working.fixes_applied || undefined,
        cve_id: working.cve_id || undefined,
        notes: working.notes || undefined,
        corrective_measure_available_at: working.corrective_local
          ? new Date(working.corrective_local + 'Z').toISOString()
          : undefined,
      };

      await craApi.updateIncident(incident.id, payload);
      saveSuccess = true;
      setTimeout(() => { saveSuccess = false; }, 2000);
      onsaved?.();
    } catch (err) {
      saveError = err instanceof Error ? err.message : 'Save failed';
    } finally {
      saving = false;
    }
  }

  const inputStyle =
    'background: var(--color-bg-surface); border-color: var(--color-border-default); color: var(--color-text-primary);';
  const labelStyle = 'color: var(--color-text-secondary);';
  const sectionStyle = 'border-color: var(--color-border-subtle);';
</script>

<div class="space-y-4">
  <!-- Art. 14(2)(a) — Early warning -->
  <details open class="rounded border" style={sectionStyle}>
    <summary class="px-3 py-2 cursor-pointer text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-secondary);">
      Art. 14(2)(a) — Early warning content
    </summary>
    <div class="px-3 py-3 space-y-3 border-t" style={sectionStyle}>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>Title</span>
        <input type="text" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.title} />
      </label>
      <div class="grid grid-cols-2 gap-3">
        <label class="block">
          <span class="block text-xs mb-1" style={labelStyle}>Severity</span>
          <select class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.severity}>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </label>
        <label class="block">
          <span class="block text-xs mb-1" style={labelStyle}>CVE ID (if assigned)</span>
          <input type="text" class="w-full rounded border px-2.5 py-1.5 text-sm font-mono" style={inputStyle} bind:value={working.cve_id} placeholder="CVE-2026-1234" />
        </label>
      </div>
      <label class="flex items-center gap-2 text-xs" style={labelStyle}>
        <input type="checkbox" bind:checked={working.actively_exploited} />
        Actively exploited
      </label>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>
          Member States affected (ISO-3166 alpha-2, comma-separated, e.g. <code>DE, FR, IT</code>)
        </span>
        <input type="text" class="w-full rounded border px-2.5 py-1.5 text-sm font-mono" style={inputStyle} bind:value={working.member_states_csv} />
      </label>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>General product description</span>
        <textarea rows="2" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.product_description}></textarea>
      </label>
    </div>
  </details>

  <!-- Art. 14(2)(b) — Incident report addenda -->
  <details class="rounded border" style={sectionStyle}>
    <summary class="px-3 py-2 cursor-pointer text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-secondary);">
      Art. 14(2)(b) — Incident report (within 72h)
    </summary>
    <div class="px-3 py-3 space-y-3 border-t" style={sectionStyle}>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>Nature of exploitation / vulnerability</span>
        <textarea rows="3" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.vulnerability_nature}></textarea>
      </label>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>Mitigations taken</span>
        <textarea rows="3" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.mitigations_taken}></textarea>
      </label>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>Mitigations recommended (to users)</span>
        <textarea rows="3" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.mitigations_recommended}></textarea>
      </label>
    </div>
  </details>

  <!-- Art. 14(2)(c) — Final report -->
  <details class="rounded border" style={sectionStyle}>
    <summary class="px-3 py-2 cursor-pointer text-xs font-semibold uppercase tracking-wider" style="color: var(--color-text-secondary);">
      Art. 14(2)(c) — Final report (within 14d of fix being available)
    </summary>
    <div class="px-3 py-3 space-y-3 border-t" style={sectionStyle}>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>
          Corrective measure available at (UTC) — <em>this starts the 14-day clock</em>
        </span>
        <input
          type="datetime-local"
          step="1"
          class="w-full rounded border px-2.5 py-1.5 text-sm"
          style={inputStyle}
          bind:value={working.corrective_local}
        />
      </label>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>Vulnerability description (severity, impact)</span>
        <textarea rows="3" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.vulnerability_description}></textarea>
      </label>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>Impact description</span>
        <textarea rows="3" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.impact_description}></textarea>
      </label>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>Malicious actor info (if known)</span>
        <textarea rows="2" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.malicious_actor_info}></textarea>
      </label>
      <label class="block">
        <span class="block text-xs mb-1" style={labelStyle}>Fixes / patches applied</span>
        <textarea rows="3" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.fixes_applied}></textarea>
      </label>
    </div>
  </details>

  <label class="block">
    <span class="block text-xs mb-1" style={labelStyle}>Internal notes</span>
    <textarea rows="2" class="w-full rounded border px-2.5 py-1.5 text-sm" style={inputStyle} bind:value={working.notes}></textarea>
  </label>

  <div class="flex items-center justify-end gap-2">
    {#if saveError}
      <span class="text-xs" style="color: var(--color-status-error);">{saveError}</span>
    {/if}
    {#if saveSuccess}
      <span class="text-xs" style="color: var(--color-status-success);">Saved</span>
    {/if}
    <button
      class="px-3 py-1.5 rounded text-xs font-medium cursor-pointer disabled:opacity-50"
      style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
      onclick={save}
      disabled={saving}
    >
      {saving ? 'Saving…' : 'Save'}
    </button>
  </div>
</div>
