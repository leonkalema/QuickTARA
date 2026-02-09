<script lang="ts">
  /**
   * Compact metric display: large number + label + optional trend.
   * Used on dashboards and summary strips.
   */
  import { TrendingUp, TrendingDown, Minus } from '@lucide/svelte';

  interface Props {
    value: number | string;
    label: string;
    trend?: 'up' | 'down' | 'flat';
    trendLabel?: string;
    icon?: any;
    accent?: string;
  }

  const { value, label, trend, trendLabel, icon, accent }: Props = $props();

  const trendColor = $derived(
    trend === 'up' ? 'var(--color-risk-high)' :
    trend === 'down' ? 'var(--color-success)' :
    'var(--color-text-tertiary)'
  );
</script>

<div
  class="rounded-lg p-4 flex flex-col gap-1"
  style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);"
>
  <div class="flex items-center justify-between">
    <span class="text-xs font-medium uppercase tracking-wider" style="color: var(--color-text-tertiary);">
      {label}
    </span>
    {#if icon}
      {@const Icon = icon}
      <Icon class="w-4 h-4" style="color: {accent ?? 'var(--color-text-tertiary)'};" />
    {/if}
  </div>
  <div class="text-2xl font-bold tracking-tight" style="color: {accent ?? 'var(--color-text-primary)'};">
    {value}
  </div>
  {#if trend}
    <div class="flex items-center gap-1 text-xs" style="color: {trendColor};">
      {#if trend === 'up'}
        <TrendingUp class="w-3 h-3" />
      {:else if trend === 'down'}
        <TrendingDown class="w-3 h-3" />
      {:else}
        <Minus class="w-3 h-3" />
      {/if}
      {#if trendLabel}
        <span>{trendLabel}</span>
      {/if}
    </div>
  {/if}
</div>
