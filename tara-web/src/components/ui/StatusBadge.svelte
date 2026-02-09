<script lang="ts">
  /**
   * Workflow state indicator: draft / review / approved / released.
   * Uses design system status color tokens.
   */
  interface Props {
    status: 'draft' | 'review' | 'approved' | 'released' | string;
    size?: 'sm' | 'md';
  }

  const { status, size = 'sm' }: Props = $props();

  const STATUS_STYLES: Record<string, { bg: string; fg: string; label: string }> = {
    draft:    { bg: 'var(--color-status-draft-bg)',    fg: 'var(--color-status-draft)',    label: 'Draft' },
    review:   { bg: 'var(--color-status-review-bg)',   fg: 'var(--color-status-review)',   label: 'In Review' },
    approved: { bg: 'var(--color-status-approved-bg)', fg: 'var(--color-status-approved)', label: 'Approved' },
    released: { bg: 'var(--color-status-released-bg)', fg: 'var(--color-status-released)', label: 'Released' },
    accepted: { bg: 'var(--color-status-approved-bg)', fg: 'var(--color-status-approved)', label: 'Accepted' },
  };

  const normalised = $derived(status.toLowerCase());
  const style = $derived(STATUS_STYLES[normalised] ?? STATUS_STYLES['draft']);
  const sizeClass = $derived(size === 'md' ? 'px-2.5 py-1 text-xs' : 'px-2 py-0.5 text-[11px]');
</script>

<span
  class="inline-flex items-center gap-1.5 font-medium rounded-full whitespace-nowrap {sizeClass}"
  style="background: {style.bg}; color: {style.fg};"
>
  <span class="w-1.5 h-1.5 rounded-full" style="background: {style.fg};"></span>
  {style.label}
</span>
