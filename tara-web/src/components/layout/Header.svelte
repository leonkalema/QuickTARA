<script lang="ts">
  import { ChevronDown, Settings, User } from '@lucide/svelte';
  import ProductSelector from '../ui/ProductSelector.svelte';
</script>

<header class="bg-white border-b border-gray-200 px-6 py-4">
  <div class="flex items-center justify-between">
    <!-- Logo and Brand -->
    <div class="flex items-center space-x-6">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-sm">QT</span>
        </div>
        <div>
          <h1 class="text-xl font-bold text-gray-900">QuickTARA</h1>
        </div>
      </div>
      
      <!-- Product Selector -->
      <ProductSelector />
    </div>

    <!-- User Menu -->
    <div class="flex items-center space-x-4">
      <button class="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
        <Settings class="w-5 h-5" />
        <span class="hidden sm:inline">Settings</span>
      </button>
      
      <div class="flex items-center space-x-2">
        <button class="flex items-center space-x-2 bg-gray-50 hover:bg-gray-100 rounded-lg px-3 py-2">
          <User class="w-5 h-5 text-gray-600" />
          <span class="text-sm font-medium text-gray-700 hidden sm:inline">Admin</span>
          <ChevronDown class="w-4 h-4 text-gray-500" />
        </button>
      </div>
    </div>
  </div>
</header>
