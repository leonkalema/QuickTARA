<script lang="ts">
  /**
   * Live countdown clock for one CRA Art. 14 deadline phase.
   * Re-renders every second from the deadline_at timestamp; no API polling.
   */
  import { onDestroy, onMount } from 'svelte';
  import type { DeadlineInfo, DeadlineStatus } from '$lib/types/cra';
  import { Clock, AlertTriangle, Check } from '@lucide/svelte';

  interface Props {
    deadline: DeadlineInfo;
    label: string;
  }

  let { deadline, label }: Props = $props();

  let now = $state(Date.now());
  let interval: ReturnType<typeof setInterval> | undefined;

  onMount(() => {
    interval = setInterval(() => { now = Date.now(); }, 1000);
  });
  onDestroy(() => {
    if (interval) clearInterval(interval);
  });

  const liveStatus: DeadlineStatus = $derived.by(() => {
    if (deadline.status === 'submitted') return 'submitted';
    const remaining = (new Date(deadline.deadline_at).getTime() - now) / 1000;
    if (remaining < 0) return 'overdue';
    // Approaching threshold per phase, mirroring core/cra_incident_deadlines.py
    const approachingSec =
      deadline.phase === 'early_warning' ? 6 * 3600
      : deadline.phase === 'incident_report' ? 18 * 3600
      : 3 * 86400;
    return remaining <= approachingSec ? 'approaching' : 'on_track';
  });

  const remainingSec = $derived(
    Math.floor((new Date(deadline.deadline_at).getTime() - now) / 1000),
  );

  function formatRemaining(seconds: number): string {
    const abs = Math.abs(seconds);
    const days = Math.floor(abs / 86400);
    const hours = Math.floor((abs % 86400) / 3600);
    const minutes = Math.floor((abs % 3600) / 60);
    const secs = abs % 60;
    if (days > 0) return `${days}d ${hours}h ${minutes}m`;
    if (hours > 0) return `${hours}h ${minutes}m ${secs.toString().padStart(2, '0')}s`;
    if (minutes > 0) return `${minutes}m ${secs.toString().padStart(2, '0')}s`;
    return `${secs}s`;
  }

  const colors: Record<DeadlineStatus, { bg: string; fg: string; border: string }> = {
    on_track:    { bg: 'rgba(52,211,153,0.08)', fg: '#34d399', border: 'rgba(52,211,153,0.35)' },
    approaching: { bg: 'rgba(251,191,36,0.10)', fg: '#fbbf24', border: 'rgba(251,191,36,0.45)' },
    overdue:     { bg: 'rgba(239,68,68,0.10)',  fg: '#f87171', border: 'rgba(239,68,68,0.45)'  },
    submitted:   { bg: 'rgba(79,143,247,0.08)', fg: '#4f8ff7', border: 'rgba(79,143,247,0.35)' },
  };

  const palette = $derived(colors[liveStatus]);
</script>

<div
  class="rounded-md px-2.5 py-2 flex flex-col gap-0.5 min-w-[120px]"
  style="background: {palette.bg}; border: 1px solid {palette.border};"
>
  <div class="flex items-center gap-1 text-[10px] uppercase tracking-wider font-semibold" style="color: {palette.fg};">
    {#if liveStatus === 'submitted'}
      <Check class="w-3 h-3" />
    {:else if liveStatus === 'overdue'}
      <AlertTriangle class="w-3 h-3" />
    {:else}
      <Clock class="w-3 h-3" />
    {/if}
    {label}
  </div>
  <div class="text-sm font-mono font-bold tabular-nums" style="color: {palette.fg};">
    {#if liveStatus === 'submitted'}
      Submitted
    {:else if remainingSec >= 0}
      {formatRemaining(remainingSec)}
    {:else}
      −{formatRemaining(remainingSec)}
    {/if}
  </div>
</div>
