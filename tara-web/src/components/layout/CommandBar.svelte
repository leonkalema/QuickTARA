<script lang="ts">
  import { Settings, Bell, Shield } from '@lucide/svelte';
  import ProductSelector from '../ui/ProductSelector.svelte';
  import UserMenu from '$lib/components/UserMenu.svelte';
  import { authStore } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';

  function handleLogout(): void {
    goto('/auth');
  }

  let isSettingsPage = $derived($page.url.pathname.startsWith('/settings'));

  let canSeeSettings = $derived.by(() => {
    const state: any = $authStore;
    const isSuperuser: boolean = !!state?.user?.is_superuser;
    const isAdminEmail: boolean = state?.user?.email === 'admin@quicktara.local';
    return isSuperuser || authStore.hasRole('tool_admin') || authStore.hasRole('org_admin') || isAdminEmail;
  });
</script>

<header
  class="flex items-center justify-between px-5 py-2.5 border-b shrink-0"
  style="background: var(--color-bg-surface); border-color: var(--color-border-default);"
>
  <!-- Left: Logo + Product Selector -->
  <div class="flex items-center gap-5">
    <a href="/" class="flex items-center gap-2.5 hover:opacity-90 transition-opacity">
      <div
        class="w-7 h-7 rounded-md flex items-center justify-center"
        style="background: var(--color-accent-primary);"
      >
        <Shield class="w-4 h-4" style="color: var(--color-text-inverse);" />
      </div>
      <span class="text-sm font-semibold tracking-tight" style="color: var(--color-text-primary);">
        QuickTARA
      </span>
    </a>

    {#if !isSettingsPage}
      <div
        class="h-5 w-px"
        style="background: var(--color-border-default);"
      ></div>
      <ProductSelector />
    {/if}
  </div>

  <!-- Right: Actions + User -->
  <div class="flex items-center gap-3">
    {#if canSeeSettings}
      <a
        href="/settings"
        class="p-1.5 rounded-md transition-colors focus-ring"
        style="color: var(--color-text-tertiary);"
        onmouseenter={(e) => { e.currentTarget.style.color = 'var(--color-text-primary)'; e.currentTarget.style.background = 'var(--color-bg-surface-hover)'; }}
        onmouseleave={(e) => { e.currentTarget.style.color = 'var(--color-text-tertiary)'; e.currentTarget.style.background = 'transparent'; }}
        title="Settings"
      >
        <Settings class="w-4 h-4" />
      </a>
    {/if}

    {#if $authStore.user}
      <UserMenu user={$authStore.user} on:logout={handleLogout} />
    {/if}
  </div>
</header>
