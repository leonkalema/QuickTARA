<script lang="ts">
  import { goto } from '$app/navigation';
  import MetricCard from '../../../components/ui/MetricCard.svelte';
  import { Users, Building2, Activity } from '@lucide/svelte';

  interface Props {
    totalUsers: number;
    totalOrganizations: number;
  }

  const { totalUsers, totalOrganizations }: Props = $props();

  const actions = [
    { label: 'Manage Users', desc: 'Create, edit, and manage user accounts', route: '/settings/users' },
    { label: 'Organizations', desc: 'Manage organization settings', route: '/settings/organizations' },
    { label: 'System Settings', desc: 'Configure system preferences', route: '/settings' },
  ];
</script>

<div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
  <MetricCard value={totalUsers} label="Users" icon={Users} accent="var(--color-accent-primary)" />
  <MetricCard value={totalOrganizations} label="Organizations" icon={Building2} accent="var(--color-success)" />
  <MetricCard value="Active" label="System Status" icon={Activity} accent="var(--color-success)" />
</div>

<div
  class="rounded-lg p-5"
  style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);"
>
  <h2 class="text-sm font-semibold uppercase tracking-wider mb-4" style="color: var(--color-text-secondary);">
    Quick Actions
  </h2>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
    {#each actions as action}
      <button
        onclick={() => goto(action.route)}
        class="text-left rounded-lg px-4 py-4 transition-all"
        style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-subtle);"
        onmouseenter={(e) => { e.currentTarget.style.borderColor = 'var(--color-accent-primary)'; e.currentTarget.style.background = 'var(--color-bg-surface-hover)'; }}
        onmouseleave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-subtle)'; e.currentTarget.style.background = 'var(--color-bg-elevated)'; }}
      >
        <div class="text-sm font-semibold" style="color: var(--color-text-primary);">{action.label}</div>
        <p class="text-xs mt-1" style="color: var(--color-text-tertiary);">{action.desc}</p>
      </button>
    {/each}
  </div>
</div>
