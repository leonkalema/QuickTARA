<script lang="ts">
  import { onMount } from 'svelte';
  import DatabaseSettings from './DatabaseSettings.svelte';
  import RiskFrameworkManager from '../risk/RiskFrameworkManager.svelte';
  
  // Settings tabs
  const tabs = [
    { id: 'database', label: 'Database' },
    { id: 'risk', label: 'Risk Framework' },
    { id: 'general', label: 'General' },
    { id: 'appearance', label: 'Appearance' }
  ];
  
  // Active tab
  let activeTab = 'database';
</script>

<div>
  <!-- Tab navigation -->
  <div class="mb-6 border-b" style="border-color: var(--color-border);">
    <nav class="flex">
      {#each tabs as tab}
        <button 
          class="py-2 px-4 text-center {activeTab === tab.id ? 'border-b-2 font-medium' : ''}" 
          style="border-color: var(--color-primary);"
          on:click={() => activeTab = tab.id}
        >
          {tab.label}
        </button>
      {/each}
    </nav>
  </div>
  
  <!-- Settings content based on active tab -->
  <div class="py-4">
    {#if activeTab === 'database'}
      <!-- Database Settings -->
      <div>
        <h2 class="text-xl font-semibold mb-4" style="color: var(--color-primary);">Database Configuration</h2>
        <div style="background-color: var(--color-card-bg); border: 1px solid var(--color-border);" class="rounded-lg shadow-sm p-6">
          <DatabaseSettings />
        </div>
      </div>
    {:else if activeTab === 'risk'}
      <!-- Risk Framework Settings -->
      <div>
        <h2 class="text-xl font-semibold mb-4" style="color: var(--color-primary);">Risk Framework Configuration</h2>
        <div style="background-color: var(--color-card-bg); border: 1px solid var(--color-border);" class="rounded-lg shadow-sm p-6">
          <RiskFrameworkManager />
        </div>
      </div>
    {:else if activeTab === 'general'}
      <!-- General Settings -->
      <div>
        <h2 class="text-xl font-semibold mb-4" style="color: var(--color-primary);">General Settings</h2>
        <div style="background-color: var(--color-card-bg); border: 1px solid var(--color-border);" class="rounded-lg shadow-sm p-6">
          <p class="text-gray-500">General settings will be implemented in a future update.</p>
        </div>
      </div>
    {:else if activeTab === 'appearance'}
      <!-- Appearance Settings -->
      <div>
        <h2 class="text-xl font-semibold mb-4" style="color: var(--color-primary);">Appearance Settings</h2>
        <div style="background-color: var(--color-card-bg); border: 1px solid var(--color-border);" class="rounded-lg shadow-sm p-6">
          <p class="text-gray-500">Appearance settings will be implemented in a future update.</p>
        </div>
      </div>
    {/if}
  </div>
</div>
