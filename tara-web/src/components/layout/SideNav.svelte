<script lang="ts">
  import { page } from '$app/stores';
  import { selectedProduct } from '$lib/stores/productStore';
  import { isToolAdmin, isOrgAdmin, canPerformTARA, canManageRisk, hasRole } from '$lib/utils/permissions';
  import { UserRole } from '$lib/types/roles';
  import {
    LayoutDashboard,
    FileText,
    Package,
    Zap,
    AlertTriangle,
    Shield,
    ShieldCheck,
    Pill,
    BarChart3,
    ClipboardCheck,
    Settings,
    ChevronsLeft,
    ChevronsRight,
    Circle,
    CircleDot,
    CircleCheckBig
  } from '@lucide/svelte';

  let collapsed = $state(false);

  interface NavItem {
    id: string;
    label: string;
    icon: any;
    path: string;
    requiresProduct?: boolean;
    permission?: 'tara' | 'risk' | 'reports' | 'admin';
    group: 'overview' | 'analyze' | 'deliver' | 'admin';
    step?: number;
  }

  const navItems: NavItem[] = [
    { id: 'dashboard', label: 'Overview', icon: LayoutDashboard, path: '/', group: 'overview' },
    { id: 'products', label: 'Product Scope', icon: FileText, path: '/products', group: 'analyze', permission: 'tara', step: 1 },
    { id: 'assets', label: 'Assets', icon: Package, path: '/assets', group: 'analyze', permission: 'tara', requiresProduct: true, step: 2 },
    { id: 'damage', label: 'Damage Scenarios', icon: Zap, path: '/damage-scenarios', group: 'analyze', permission: 'tara', requiresProduct: true, step: 3 },
    { id: 'threats', label: 'Threat Scenarios', icon: AlertTriangle, path: '/threat-scenarios', group: 'analyze', permission: 'tara', requiresProduct: true, step: 4 },
    { id: 'risk', label: 'Risk Assessment', icon: Shield, path: '/risk-assessment', group: 'analyze', permission: 'tara', requiresProduct: true, step: 5 },
    { id: 'treatment', label: 'Risk Treatment', icon: Pill, path: '/risk-treatment', group: 'analyze', permission: 'tara', requiresProduct: true, step: 6 },
    { id: 'reports', label: 'Reports', icon: BarChart3, path: '/reports', group: 'deliver', permission: 'reports', requiresProduct: true },
    { id: 'cra', label: 'CRA Compliance', icon: ShieldCheck, path: '/cra', group: 'deliver', permission: 'reports' },
    { id: 'audit', label: 'Audit & Compliance', icon: ClipboardCheck, path: '/audit', group: 'deliver', permission: 'reports', requiresProduct: true },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/settings', group: 'admin', permission: 'admin' },
  ];

  function hasPermission(perm?: string): boolean {
    if (!perm) return true;
    switch (perm) {
      case 'tara': return canPerformTARA();
      case 'risk': return canManageRisk();
      case 'reports': return canPerformTARA() || canManageRisk() || hasRole(UserRole.AUDITOR) || hasRole(UserRole.VIEWER);
      case 'admin': return isToolAdmin() || isOrgAdmin();
      default: return true;
    }
  }

  function isAccessible(item: NavItem): boolean {
    if (!hasPermission(item.permission)) return false;
    if (item.requiresProduct && !$selectedProduct) return false;
    return true;
  }

  function isCurrent(item: NavItem): boolean {
    if (item.path === '/') return $page.url.pathname === '/';
    return $page.url.pathname.startsWith(item.path);
  }

  const groups = [
    { key: 'overview' as const, label: '' },
    { key: 'analyze' as const, label: 'Analyze' },
    { key: 'deliver' as const, label: 'Deliver' },
    { key: 'admin' as const, label: 'Admin' },
  ];
</script>

<aside
  class="flex flex-col border-r transition-all duration-200 select-none"
  style="width: {collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)'}; background: var(--color-bg-surface); border-color: var(--color-border-default);"
>
  <!-- Collapse toggle -->
  <button
    onclick={() => collapsed = !collapsed}
    class="flex items-center justify-center h-10 hover:opacity-80 transition-opacity cursor-pointer"
    style="color: var(--color-text-tertiary);"
    aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
  >
    {#if collapsed}
      <ChevronsRight class="w-4 h-4" />
    {:else}
      <ChevronsLeft class="w-4 h-4" />
    {/if}
  </button>

  <!-- Nav groups -->
  <nav class="flex-1 overflow-y-auto px-2 pb-4 space-y-4" aria-label="Main navigation">
    {#each groups as group}
      {@const items = navItems.filter(i => i.group === group.key && hasPermission(i.permission))}
      {#if items.length > 0}
        <div>
          {#if group.label && !collapsed}
            <div
              class="px-3 py-1 text-[10px] font-semibold uppercase tracking-wider"
              style="color: var(--color-text-tertiary);"
            >
              {group.label}
            </div>
          {:else if group.label && collapsed}
            <div class="border-t mx-2 my-1" style="border-color: var(--color-border-subtle);"></div>
          {/if}

          <div class="space-y-0.5">
            {#each items as item}
              {@const active = isCurrent(item)}
              {@const accessible = isAccessible(item)}
              {@const lockedReason = !accessible && item.requiresProduct ? 'Select a product first' : ''}
              <a
                href={accessible ? item.path : undefined}
                aria-current={active ? 'page' : undefined}
                aria-disabled={!accessible ? 'true' : undefined}
                class="group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all duration-150 focus-ring
                  {active ? '' : accessible ? 'cursor-pointer' : 'cursor-not-allowed opacity-35'}"
                style="
                  background: {active ? 'var(--color-accent-primary)' : 'transparent'};
                  color: {active ? 'var(--color-text-inverse)' : 'var(--color-text-secondary)'};
                "
                onmouseenter={(e) => { if (!active && accessible) { e.currentTarget.style.background = 'var(--color-bg-surface-hover)'; e.currentTarget.style.color = 'var(--color-text-primary)'; }}}
                onmouseleave={(e) => { if (!active) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--color-text-secondary)'; }}}
                title={collapsed ? item.label : lockedReason}
              >
                {#if item.step && !collapsed}
                  <span class="flex-shrink-0 w-[18px] h-[18px] rounded-full flex items-center justify-center text-[10px] font-bold"
                    style="background: {active ? 'rgba(255,255,255,0.25)' : accessible ? 'var(--color-bg-elevated)' : 'var(--color-bg-elevated)'}; color: {active ? '#fff' : 'var(--color-text-tertiary)'};">
                    {item.step}
                  </span>
                {:else}
                  <item.icon class="w-[18px] h-[18px] flex-shrink-0" />
                {/if}
                {#if !collapsed}
                  <span class="truncate flex-1">{item.label}</span>
                  {#if !accessible && item.requiresProduct}
                    <svg class="w-3 h-3 flex-shrink-0 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                    </svg>
                  {/if}
                {/if}
              </a>
            {/each}
          </div>
        </div>
      {/if}
    {/each}
  </nav>

  <!-- Product context (bottom) -->
  {#if !collapsed && $selectedProduct}
    <div
      class="px-3 py-3 border-t text-xs truncate"
      style="border-color: var(--color-border-default); color: var(--color-text-tertiary);"
      title={$selectedProduct.name}
    >
      <span style="color: var(--color-text-secondary);">Product:</span> {$selectedProduct.name}
    </div>
  {/if}
</aside>
