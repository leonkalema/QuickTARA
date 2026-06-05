<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import {
    defaultConfigForAudience,
    type ReportAudience,
    type ReportClassification,
    type ReportConfig,
    type SectionKey
  } from '$lib/api/reportConfig';

  export let config: ReportConfig;

  const dispatch = createEventDispatcher<{ change: ReportConfig }>();

  const AUDIENCES: { value: ReportAudience; label: string; hint: string }[] = [
    { value: 'internal', label: 'Internal', hint: 'Full detail — engineering team' },
    { value: 'external', label: 'External', hint: 'Curated for customers / OEMs' },
    { value: 'auditor', label: 'Auditor', hint: 'ISO 21434 / type-approval body' }
  ];

  const SECTIONS: { key: SectionKey; label: string; wp: string }[] = [
    { key: 'document_control',      label: 'Document Control',               wp: 'Cover, version history, classification' },
    { key: 'executive_summary',     label: 'Executive Summary',              wp: 'Scope, counts, highest risk' },
    { key: 'report_status',         label: 'Report Status & Intended Use',   wp: 'Draft/approved statement, audience context' },
    { key: 'scope_and_assumptions', label: 'Scope & Assumptions',            wp: '§8.3 Item boundary and context' },
    { key: 'methodology',           label: 'Methodology',                    wp: 'SFOP, STRIDE, feasibility method' },
    { key: 'assessment_status',     label: 'Assessment Status',              wp: 'Draft vs reviewed vs approved counts' },
    { key: 'cra_compliance',        label: 'CRA Compliance',                 wp: 'Only if CRA assessment exists' },
    { key: 'asset_inventory',       label: 'Asset Inventory',                wp: 'WP-04 — assets and interfaces' },
    { key: 'damage_scenarios',      label: 'Damage Scenarios',               wp: 'WP-04 — damage scenario detail' },
    { key: 'threat_scenarios',      label: 'Threat Scenarios',               wp: 'WP-05 §15.4' },
    { key: 'attack_paths',          label: 'Attack Paths',                   wp: 'WP-06/07 §15.5–15.6' },
    { key: 'risk_summary',          label: 'Risk Summary',                   wp: 'High-level risk counts' },
    { key: 'risk_register',         label: 'Risk Register',                  wp: '§15.7 — full risk table with decisions' },
    { key: 'treatment_summary',     label: 'Treatment Summary',              wp: '§14 — treatment decisions per risk' },
    { key: 'cybersecurity_goals',   label: 'Cybersecurity Goals',            wp: 'WP-15 goals / claims' },
    { key: 'open_issues',           label: 'Open Issues & Customer Actions', wp: 'Draft items, customer confirmations' },
    { key: 'iso_compliance',        label: 'ISO 21434 Compliance',           wp: 'Work products — near end per OEM convention' },
    { key: 'traceability',          label: 'Traceability Matrix',            wp: 'Asset → Damage → Threat → Goal trace' },
    { key: 'appendices',            label: 'Appendices',                     wp: 'Placeholder — detail available in technical report' },
  ];

  // Reason shown when a section is locked off for the current audience
  const LOCKED_REASONS: Partial<Record<SectionKey, Partial<Record<ReportAudience, string>>>> = {
    cra_compliance:   { external: 'Exposes unresolved regulatory gaps', auditor: 'Separate regulatory track' },
    damage_scenarios: { external: 'Sensitive IP — reveals exploitable failure modes' },
    threat_scenarios: { external: 'Attack roadmap — never share externally' },
    attack_paths:     { external: 'Attacker guide — never share externally', auditor: 'Not required for process audit' },
    traceability:     { external: 'Exposes internal architecture decisions' },
  };


  const CLASSIFICATIONS: ReportClassification[] = ['public', 'internal', 'confidential'];

  function isLocked(key: SectionKey): boolean {
    const defaults = defaultConfigForAudience(config.audience);
    return !defaults.sections[key];
  }

  function lockReason(key: SectionKey): string | null {
    return LOCKED_REASONS[key]?.[config.audience] ?? null;
  }

  function selectAudience(audience: ReportAudience): void {
    const next = defaultConfigForAudience(audience);
    next.metadata = { ...config.metadata };
    config = next;
    dispatch('change', config);
  }

  function toggleSection(key: SectionKey): void {
    if (isLocked(key)) return;
    config.sections[key] = !config.sections[key];
    config = config;
    dispatch('change', config);
  }

  function onClassificationChange(): void {
    dispatch('change', config);
  }
</script>

<div class="space-y-5">
  <!-- Audience -->
  <div>
    <p class="text-xs font-semibold mb-2" style="color: var(--color-text-primary);">Audience</p>
    <div class="grid grid-cols-3 gap-2">
      {#each AUDIENCES as a}
        <button
          type="button"
          on:click={() => selectAudience(a.value)}
          class="rounded-lg px-3 py-2 text-left transition-colors"
          style="border: 1px solid {config.audience === a.value ? 'var(--color-accent-primary)' : 'var(--color-border-default)'};
                 background: {config.audience === a.value ? 'var(--color-bg-elevated)' : 'transparent'};"
        >
          <span class="block text-xs font-semibold" style="color: var(--color-text-primary);">{a.label}</span>
          <span class="block text-[10px] mt-0.5" style="color: var(--color-text-tertiary);">{a.hint}</span>
        </button>
      {/each}
    </div>
    {#if config.audience === 'external'}
      <p class="text-[10px] mt-2 px-1" style="color: var(--color-warning);">
        Sensitive sections are locked off. Threat details, attack paths, and internal compliance gaps are never included in external reports.
      </p>
    {:else if config.audience === 'auditor'}
      <p class="text-[10px] mt-2 px-1" style="color: var(--color-text-tertiary);">
        Configured for ISO 21434 process audit. Full traceability included. Attack paths and CRA gaps excluded.
      </p>
    {/if}
  </div>

  <!-- Sections -->
  <div>
    <p class="text-xs font-semibold mb-2" style="color: var(--color-text-primary);">Sections</p>
    <div class="space-y-1.5">
      {#each SECTIONS as s}
        {@const locked = isLocked(s.key)}
        {@const reason = lockReason(s.key)}
        <label
          class="flex items-start gap-2.5 px-2 py-1.5 rounded-lg {locked ? 'cursor-not-allowed' : 'cursor-pointer'}"
          style="background: var(--color-bg-elevated); opacity: {locked ? '0.5' : '1'};"
          title={locked && reason ? `Excluded: ${reason}` : ''}
        >
          <input
            type="checkbox"
            checked={config.sections[s.key]}
            on:change={() => toggleSection(s.key)}
            disabled={locked}
            class="mt-0.5"
          />
          <span class="flex-1">
            <span class="block text-xs" style="color: var(--color-text-primary);">
              {s.label}
              {#if locked}
                <span class="ml-1 text-[10px] font-normal" style="color: var(--color-error);">locked</span>
              {/if}
            </span>
            <span class="block text-[10px]" style="color: var(--color-text-tertiary);">
              {locked && reason ? reason : s.wp}
            </span>
          </span>
        </label>
      {/each}
    </div>
  </div>

  <!-- Classification + metadata -->
  <div>
    <p class="text-xs font-semibold mb-2" style="color: var(--color-text-primary);">Document Control</p>
    <div class="space-y-2">
      <div class="flex items-center gap-2">
        <label for="classification" class="text-xs w-24" style="color: var(--color-text-secondary);">Classification</label>
        <select id="classification" bind:value={config.classification} on:change={onClassificationChange}
          class="flex-1 px-2 py-1.5 text-xs rounded-lg"
          style="background: var(--color-bg-elevated); color: var(--color-text-primary); border: 1px solid var(--color-border-default);">
          {#each CLASSIFICATIONS as c}
            <option value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
          {/each}
        </select>
      </div>
      <div class="flex items-center gap-2">
        <label for="author" class="text-xs w-24 flex items-center gap-1" style="color: var(--color-text-secondary);">
          Author
          {#if config.audience === 'external' || config.audience === 'auditor'}
            <span style="color: var(--color-error);">*</span>
          {/if}
        </label>
        <div class="flex-1 flex flex-col gap-0.5">
          <input id="author" type="text" bind:value={config.metadata.author}
            placeholder={config.audience === 'external' || config.audience === 'auditor' ? 'Required for external / auditor reports' : 'Optional'}
            required={config.audience === 'external' || config.audience === 'auditor'}
            class="w-full px-2 py-1.5 text-xs rounded-lg"
            style="background: var(--color-bg-elevated); color: var(--color-text-primary);
                   border: 1px solid {(config.audience === 'external' || config.audience === 'auditor') && !config.metadata.author ? 'var(--color-error)' : 'var(--color-border-default)'};" />
          {#if (config.audience === 'external' || config.audience === 'auditor') && !config.metadata.author}
            <span class="text-[10px]" style="color: var(--color-error);">Required — unsigned external documents are not credible</span>
          {/if}
        </div>
      </div>
      <div class="flex items-center gap-2">
        <label for="approver" class="text-xs w-24 flex items-center gap-1" style="color: var(--color-text-secondary);">
          Approver
          {#if config.audience === 'external' || config.audience === 'auditor'}
            <span style="color: var(--color-error);">*</span>
          {/if}
        </label>
        <div class="flex-1 flex flex-col gap-0.5">
          <input id="approver" type="text" bind:value={config.metadata.approver}
            placeholder={config.audience === 'external' || config.audience === 'auditor' ? 'Required for external / auditor reports' : 'Optional'}
            required={config.audience === 'external' || config.audience === 'auditor'}
            class="w-full px-2 py-1.5 text-xs rounded-lg"
            style="background: var(--color-bg-elevated); color: var(--color-text-primary);
                   border: 1px solid {(config.audience === 'external' || config.audience === 'auditor') && !config.metadata.approver ? 'var(--color-error)' : 'var(--color-border-default)'};" />
          {#if (config.audience === 'external' || config.audience === 'auditor') && !config.metadata.approver}
            <span class="text-[10px]" style="color: var(--color-error);">Required — report needs an approver before external release</span>
          {/if}
        </div>
      </div>
      <div class="flex items-center gap-2">
        <label for="reference" class="text-xs w-24" style="color: var(--color-text-secondary);">Reference</label>
        <input id="reference" type="text" bind:value={config.metadata.reference} placeholder="Optional document ID"
          class="flex-1 px-2 py-1.5 text-xs rounded-lg"
          style="background: var(--color-bg-elevated); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
      </div>
    </div>
  </div>
</div>
