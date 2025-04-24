<script lang="ts">
  import { onMount } from 'svelte';
  import DatabaseSettings from './DatabaseSettings.svelte';
</script>

<div>
  <!-- Settings sections -->
  <div class="space-y-8">
    <!-- Database Settings -->
    <div>
      <h2 class="text-xl font-semibold mb-4 text-gray-800">Database Configuration</h2>
      <div class="bg-white rounded-lg shadow p-6">
        <DatabaseSettings />
      </div>
    </div>
    
    <!-- General Settings -->
    <div>
      <h2 class="text-xl font-semibold mb-4 text-gray-800">General Settings</h2>
      <div class="bg-white rounded-lg shadow p-6">
        <p class="text-gray-500">General settings will be implemented in a future update.</p>
      </div>
    </div>
    
    <!-- Appearance Settings -->
    <div>
      <h2 class="text-xl font-semibold mb-4 text-gray-800">Appearance Settings</h2>
      <div class="bg-white rounded-lg shadow p-6">
        <p class="text-gray-500">Appearance settings will be implemented in a future update.</p>
      </div>
    </div>
  </div>
</div>
