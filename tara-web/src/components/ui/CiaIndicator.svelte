<script lang="ts">
  /**
   * Three colored squares showing Confidentiality / Integrity / Availability impact.
   * Filled = impacted, outlined = not impacted.
   */
  interface Props {
    confidentiality: boolean;
    integrity: boolean;
    availability: boolean;
  }

  const { confidentiality, integrity, availability }: Props = $props();

  const items = $derived([
    { label: 'C', active: confidentiality, color: 'var(--color-cia-c)' },
    { label: 'I', active: integrity,       color: 'var(--color-cia-i)' },
    { label: 'A', active: availability,    color: 'var(--color-cia-a)' },
  ]);
</script>

<div class="inline-flex items-center gap-1" title="CIA Impact: C={confidentiality ? 'Yes' : 'No'}, I={integrity ? 'Yes' : 'No'}, A={availability ? 'Yes' : 'No'}">
  {#each items as item}
    <span
      class="w-5 h-5 rounded text-[9px] font-bold flex items-center justify-center"
      style="
        background: {item.active ? item.color : 'transparent'};
        color: {item.active ? 'var(--color-text-inverse)' : item.color};
        border: 1.5px solid {item.color};
        opacity: {item.active ? 1 : 0.4};
      "
    >
      {item.label}
    </span>
  {/each}
</div>
