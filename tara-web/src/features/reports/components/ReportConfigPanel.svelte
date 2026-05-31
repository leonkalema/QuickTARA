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
    { value: 'internal', label: 'Internal', hint: 'Full detail for the engineering team' },
    { value: 'external', label: 'External', hint: 'Curated for customers / OEMs' },
    { value: 'auditor', label: 'Auditor', hint: 'ISO 21434 / regulator submission' }
  ];

  const SECTIONS: { key: SectionKey; label: string; wp: string }[] = [
    { key: 'document_control', label: 'Document Control', wp: 'Clause 6 — management' },
    { key: 'iso_compliance', label: 'ISO 21434 Compliance Matrix', wp: 'Work products overview' },
    { key: 'cra_compliance', label: 'CRA Compliance', wp: 'Only if CRA assessment exists' },
    { key: 'risk_summary', label: 'Risk Register', wp: 'WP-08 risk determination' },
    { key: 'asset_inventory', label: 'Asset Inventory', wp: 'WP-04 item definition' },
    { key: 'damage_scenarios', label: 'Damage Scenarios', wp: 'WP-04 damage scenarios' },
    { key: 'cybersecurity_goals', label: 'Cybersecurity Goals', wp: 'WP-15 goals / claims' },
    { key: 'traceability', label: 'Traceability Matrix', wp: 'Asset → Goal trace' }
  ];

  const CLASSIFICATIONS: ReportClassification[] = ['public', 'internal', 'confidential'];

  function selectAudience(audience: ReportAudience): void {
    const next = defaultConfigForAudience(audience);
    // Preserve any metadata the user already typed.
    next.metadata = { ...config.metadata };
    config = next;
    dispatch('change', config);
  }

  function toggleSection(key: SectionKey): void {
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
  </div>

  <!-- Sections -->
  <div>
    <p class="text-xs font-semibold mb-2" style="color: var(--color-text-primary);">Sections</p>
    <div class="space-y-1.5">
      {#each SECTIONS as s}
        <label class="flex items-start gap-2.5 px-2 py-1.5 rounded-lg cursor-pointer"
          style="background: var(--color-bg-elevated);">
          <input
            type="checkbox"
            checked={config.sections[s.key]}
            on:change={() => toggleSection(s.key)}
            class="mt-0.5"
          />
          <span class="flex-1">
            <span class="block text-xs" style="color: var(--color-text-primary);">{s.label}</span>
            <span class="block text-[10px]" style="color: var(--color-text-tertiary);">{s.wp}</span>
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
        <label for="author" class="text-xs w-24" style="color: var(--color-text-secondary);">Author</label>
        <input id="author" type="text" bind:value={config.metadata.author} placeholder="Optional"
          class="flex-1 px-2 py-1.5 text-xs rounded-lg"
          style="background: var(--color-bg-elevated); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
      </div>
      <div class="flex items-center gap-2">
        <label for="approver" class="text-xs w-24" style="color: var(--color-text-secondary);">Approver</label>
        <input id="approver" type="text" bind:value={config.metadata.approver} placeholder="Optional"
          class="flex-1 px-2 py-1.5 text-xs rounded-lg"
          style="background: var(--color-bg-elevated); color: var(--color-text-primary); border: 1px solid var(--color-border-default);" />
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
