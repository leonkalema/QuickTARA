<script lang="ts">
  /**
   * Colored pill showing risk level: Critical / High / Medium / Low / Negligible.
   * Uses design system risk color tokens.
   */
  interface Props {
    level: 'critical' | 'high' | 'medium' | 'low' | 'negligible' | string;
    size?: 'sm' | 'md';
  }

  const { level, size = 'sm' }: Props = $props();

  const RISK_STYLES: Record<string, { bg: string; fg: string; label: string }> = {
    critical:   { bg: 'var(--color-risk-critical-bg)', fg: 'var(--color-risk-critical)',   label: 'Critical' },
    high:       { bg: 'var(--color-risk-high-bg)',     fg: 'var(--color-risk-high)',       label: 'High' },
    medium:     { bg: 'var(--color-risk-medium-bg)',    fg: 'var(--color-risk-medium)',     label: 'Medium' },
    low:        { bg: 'var(--color-risk-low-bg)',       fg: 'var(--color-risk-low)',        label: 'Low' },
    negligible: { bg: 'var(--color-risk-negligible-bg)', fg: 'var(--color-risk-negligible)', label: 'Negligible' },
  };

  const normalised = $derived(level.toLowerCase());
  const style = $derived(RISK_STYLES[normalised] ?? RISK_STYLES['negligible']);
  const sizeClass = $derived(size === 'md' ? 'px-2.5 py-1 text-xs' : 'px-2 py-0.5 text-[11px]');
</script>

<span
  class="inline-flex items-center font-semibold rounded-full whitespace-nowrap {sizeClass}"
  style="background: {style.bg}; color: {style.fg};"
>
  {style.label}
</span>
