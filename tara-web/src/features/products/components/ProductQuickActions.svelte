<script lang="ts">
  import { Package, Shield, AlertTriangle, FileText, Zap, GitBranch, Scale } from '@lucide/svelte';

  export let assetCount: number = 0;
  export let damageCount: number = 0;
  export let threatCount: number = 0;

  const actions = [
    {
      href: '/assets',
      icon: Package,
      label: 'Manage Assets',
      hint: 'Add firmware, signals, calibration data',
      getStatus: () => assetCount > 0 ? `${assetCount} defined` : 'None yet — start here',
      urgent: () => assetCount === 0,
    },
    {
      href: '/damage-scenarios',
      icon: Shield,
      label: 'Damage Scenarios',
      hint: 'Define what could go wrong',
      getStatus: () => damageCount > 0 ? `${damageCount} defined` : 'Requires assets first',
      urgent: () => assetCount > 0 && damageCount === 0,
    },
    {
      href: '/threat-scenarios',
      icon: AlertTriangle,
      label: 'Threat Scenarios',
      hint: 'How attacks could happen',
      getStatus: () => threatCount > 0 ? `${threatCount} defined` : 'Requires damage scenarios',
      urgent: () => damageCount > 0 && threatCount === 0,
    },
    {
      href: '/attack-paths',
      icon: GitBranch,
      label: 'Attack Paths',
      hint: 'Map attacker routes',
      getStatus: () => threatCount > 0 ? 'Ready to assess' : 'Requires threat scenarios',
      urgent: () => false,
    },
    {
      href: '/risk-treatment',
      icon: Scale,
      label: 'Risk Treatment',
      hint: 'Decide treatment per risk',
      getStatus: () => 'Review and decide',
      urgent: () => false,
    },
    {
      href: '/reports',
      icon: FileText,
      label: 'Generate Report',
      hint: 'Export as PDF for OEM/auditor',
      getStatus: () => 'Internal, External or Auditor',
      urgent: () => false,
    },
  ];
</script>

<div class="mt-6 rounded-lg p-5" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
  <h3 class="text-sm font-semibold mb-3" style="color: var(--color-text-primary);">TARA Workflow</h3>
  <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
    {#each actions as action}
      {@const urgent = action.urgent()}
      <a
        href={action.href}
        class="flex items-center p-3 rounded-lg transition-colors"
        style="background: var(--color-bg-surface); border: 1px solid {urgent ? 'var(--color-accent-primary)' : 'var(--color-border-default)'};"
      >
        <svelte:component this={action.icon} class="w-4 h-4 mr-3 flex-shrink-0" style="color: {urgent ? 'var(--color-accent-primary)' : 'var(--color-text-secondary)'};" />
        <div class="min-w-0">
          <div class="text-xs font-medium truncate" style="color: var(--color-text-primary);">{action.label}</div>
          <div class="text-[10px] truncate" style="color: {urgent ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)'};">
            {action.getStatus()}
          </div>
        </div>
      </a>
    {/each}
  </div>
</div>
