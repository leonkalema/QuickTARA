<script lang="ts">
  import type { Product } from '$lib/types/product';

  export let product: Product;
  export let assetCount: number = 0;
  export let damageScenarioCount: number = 0;
  export let threatScenarioCount: number = 0;

  interface CheckItem {
    label: string;
    done: boolean;
    required: boolean;
    hint: string;
  }

  $: checks = [
    { label: 'Product basics',       done: !!(product.name && product.safety_level && product.product_type), required: true,  hint: 'Name, safety level, product type' },
    { label: 'Description',          done: !!(product.description && product.description.length > 20),         required: false, hint: 'Enables auto-detect of interfaces' },
    { label: 'Interfaces',           done: !!(product.interfaces && product.interfaces.length > 0),            required: true,  hint: 'CAN-FD, UDS, OTA, etc.' },
    { label: 'Access points',        done: !!(product.access_points && product.access_points.length > 0),      required: true,  hint: 'OBD-II, JTAG, USB, etc.' },
    { label: 'Boundaries defined',   done: !!(product.boundaries && product.boundaries.length > 0),            required: false, hint: 'In-scope vs out-of-scope' },
    { label: 'Objectives defined',   done: !!(product.objectives && product.objectives.length > 0),            required: false, hint: 'Cybersecurity objectives' },
    { label: 'Assets added',         done: assetCount > 0,                                                     required: true,  hint: 'Firmware, signals, calibration data' },
    { label: 'Damage scenarios',     done: damageScenarioCount > 0,                                            required: true,  hint: 'Generate from assets' },
    { label: 'Threat scenarios',     done: threatScenarioCount > 0,                                            required: true,  hint: 'Generate from catalog' },
  ];

  $: requiredChecks = checks.filter(c => c.required);
  $: completedRequired = requiredChecks.filter(c => c.done).length;
  $: totalRequired = requiredChecks.length;
  $: pct = Math.round((completedRequired / totalRequired) * 100);
  $: missing = checks.filter(c => !c.done && c.required).map(c => c.label);

  $: barColor = pct < 40 ? 'var(--color-error)' : pct < 75 ? 'var(--color-warning)' : 'var(--color-success)';
</script>

<div class="rounded-lg p-5 mb-6" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
  <div class="flex items-center justify-between mb-3">
    <h2 class="text-sm font-semibold" style="color: var(--color-text-primary);">TARA Setup Completeness</h2>
    <span class="text-sm font-bold" style="color: {barColor};">{pct}%</span>
  </div>

  <!-- Progress bar -->
  <div class="h-1.5 rounded-full mb-3" style="background: var(--color-bg-inset);">
    <div class="h-1.5 rounded-full transition-all" style="width: {pct}%; background: {barColor};"></div>
  </div>

  <!-- Checklist -->
  <div class="grid grid-cols-2 md:grid-cols-3 gap-1.5">
    {#each checks as c}
      <div class="flex items-center gap-1.5 text-[10px]" title={c.hint}>
        {#if c.done}
          <span style="color: var(--color-success);">✓</span>
        {:else}
          <span style="color: {c.required ? 'var(--color-error)' : 'var(--color-text-tertiary)'};">○</span>
        {/if}
        <span style="color: {c.done ? 'var(--color-text-secondary)' : c.required ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)'};">
          {c.label}{c.required ? '' : ' (optional)'}
        </span>
      </div>
    {/each}
  </div>

  {#if missing.length > 0}
    <p class="text-[10px] mt-3" style="color: var(--color-text-tertiary);">
      Required to complete: {missing.join(', ')}
    </p>
  {/if}
</div>
