<script lang="ts">
  /**
   * Domain-specific empty state with radar motif background.
   * Shows icon, title, description, and optional CTA.
   */
  import { Shield } from '@lucide/svelte';

  interface Props {
    title: string;
    description: string;
    icon?: any;
    ctaLabel?: string;
    ctaHref?: string;
    onAction?: () => void;
  }

  const { title, description, icon, ctaLabel, ctaHref, onAction }: Props = $props();
</script>

<div class="relative flex flex-col items-center justify-center py-16 text-center">
  <!-- Radar motif background -->
  <div class="absolute inset-0 radar-bg pointer-events-none"></div>

  <div class="relative z-10 flex flex-col items-center max-w-md">
    <div
      class="w-14 h-14 rounded-xl flex items-center justify-center mb-4"
      style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);"
    >
      {#if icon}
        {@const Icon = icon}
        <Icon class="w-7 h-7" style="color: var(--color-text-tertiary);" />
      {:else}
        <Shield class="w-7 h-7" style="color: var(--color-text-tertiary);" />
      {/if}
    </div>

    <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">
      {title}
    </h3>
    <p class="text-sm leading-relaxed mb-6" style="color: var(--color-text-secondary);">
      {description}
    </p>

    {#if ctaLabel && ctaHref}
      <a
        href={ctaHref}
        class="inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        onmouseenter={(e) => e.currentTarget.style.background = 'var(--color-accent-primary-hover)'}
        onmouseleave={(e) => e.currentTarget.style.background = 'var(--color-accent-primary)'}
      >
        {ctaLabel}
      </a>
    {:else if ctaLabel && onAction}
      <button
        onclick={onAction}
        class="inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        onmouseenter={(e) => e.currentTarget.style.background = 'var(--color-accent-primary-hover)'}
        onmouseleave={(e) => e.currentTarget.style.background = 'var(--color-accent-primary)'}
      >
        {ctaLabel}
      </button>
    {/if}
  </div>
</div>
