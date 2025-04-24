<script lang="ts">
  import { onMount } from 'svelte';
  import ComponentManager from './components/ComponentManager.svelte';
  import SettingsManager from './components/settings/SettingsManager.svelte';
  import Navbar from './components/Navbar.svelte';
  
  // Active page state
  let activePage = 'components';
</script>

<main class="min-h-screen bg-gray-100">
  <Navbar bind:activePage={activePage} />
  
  <!-- Section header for each page - visually connects with the navbar -->
  <div class="bg-white border-b border-gray-200 shadow-sm mb-6">
    <div class="container mx-auto px-4 py-5 max-w-7xl">
      <h1 class="text-2xl font-bold text-gray-900">
        {#if activePage === 'components'}
          Components Dashboard
        {:else if activePage === 'analysis'}
          Analysis Dashboard
        {:else if activePage === 'review'}
          Risk Review Dashboard
        {:else if activePage === 'reports'}
          Reports Dashboard
        {:else if activePage === 'settings'}
          Settings
        {/if}
      </h1>
    </div>
  </div>
  
  <!-- Main content -->
  <div class="container mx-auto px-4 max-w-7xl pb-8">
    {#if activePage === 'components'}
      <ComponentManager />
    {:else if activePage === 'settings'}
      <SettingsManager />
    {:else}
      <div class="bg-white shadow-md rounded p-6">
        <div class="flex justify-center items-center py-12">
          <div class="text-center">
            <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <h2 class="text-xl font-semibold mb-2">{activePage.charAt(0).toUpperCase() + activePage.slice(1)}</h2>
            <p class="text-gray-500 mb-4">
              This feature is under development and will be available in a future update.
            </p>
            <button 
              on:click={() => activePage = 'components'}
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
              Go to Components
            </button>
          </div>
        </div>
      </div>
    {/if}
  </div>
</main>
