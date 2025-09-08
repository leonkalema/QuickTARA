<script lang="ts">
  import { ChevronDown, Settings, User } from '@lucide/svelte';
  import ProductSelector from '../ui/ProductSelector.svelte';
  import UserMenu from '$lib/components/UserMenu.svelte';
  import { authStore } from '$lib/stores/auth';
  import { get } from 'svelte/store';
  import { goto } from '$app/navigation';

  function handleLogout() {
    goto('/auth');
  }

  // Only admins should see Settings (superuser, tool_admin, org_admin, or admin email)
  let canSeeSettings = false;
  $: {
    const state: any = $authStore;
    const isSuperuser: boolean = !!state?.user?.is_superuser;
    const isAdminEmail: boolean = state?.user?.email === 'admin@quicktara.local';
    canSeeSettings = isSuperuser || authStore.hasRole('tool_admin') || authStore.hasRole('org_admin') || isAdminEmail;
  }
</script>

<header class="bg-white border-b border-gray-200 px-6 py-4">
  <div class="flex items-center justify-between">
    <!-- Logo and Brand -->
    <div class="flex items-center space-x-6">
      <a href="/products" class="flex items-center space-x-2 hover:opacity-80 transition-opacity">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-sm">QT</span>
        </div>
        <div>
          <h1 class="text-xl font-bold text-gray-900">QuickTARA</h1>
        </div>
      </a>
      
      <!-- Product Selector -->
      <ProductSelector />
    </div>

    <!-- User Menu -->
    <div class="flex items-center space-x-4">
      {#if canSeeSettings}
        <a href="/settings" class="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
          <Settings class="w-5 h-5" />
          <span class="hidden sm:inline">Settings</span>
        </a>
      {/if}
      
      {#if $authStore.user}
        <UserMenu user={$authStore.user} on:logout={handleLogout} />
      {/if}
    </div>
  </div>
</header>
