<script lang="ts">
  import { selectedProduct } from '../../lib/stores/productStore';
  
  // Placeholder for product selector - will implement when we build product feature
  let showProductSelector = false;
</script>

<header class="bg-white shadow-sm border-b border-gray-200">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-16">
      <!-- Logo and Title -->
      <div class="flex items-center space-x-4">
        <div class="flex-shrink-0">
          <h1 class="text-2xl font-bold text-slate-700">QuickTARA</h1>
        </div>
      </div>

      <!-- Navigation Menu -->
      <nav class="hidden md:flex space-x-8">
        <a href="/" class="text-gray-700 hover:text-slate-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
          Dashboard
        </a>
        <a href="/products" class="text-gray-700 hover:text-slate-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
          Products
        </a>
        <a href="/assets" class="text-gray-700 hover:text-slate-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
          Assets
        </a>
        <a href="/threats" class="text-gray-700 hover:text-slate-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
          Threats
        </a>
        <a href="/damage" class="text-gray-700 hover:text-slate-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
          Damage Scenarios
        </a>
        <a href="/reports" class="text-gray-700 hover:text-slate-600 px-3 py-2 rounded-md text-sm font-medium transition-colors">
          Reports
        </a>
      </nav>

      <!-- Product Selector -->
      <div class="flex items-center space-x-4">
        {#if $selectedProduct}
          <div class="flex items-center space-x-2 bg-slate-50 px-3 py-1 rounded-md">
            <div class="w-2 h-2 bg-slate-600 rounded-full"></div>
            <span class="text-sm font-medium text-slate-700">
              {$selectedProduct.name}
            </span>
            <button 
              class="text-slate-600 hover:text-slate-800 ml-2"
              on:click={() => showProductSelector = true}
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>
          </div>
        {:else}
          <button 
            class="bg-slate-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-slate-700 transition-colors"
            on:click={() => showProductSelector = true}
          >
            Select Product
          </button>
        {/if}

        <!-- Mobile menu button -->
        <button class="md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- Product Context Banner -->
  {#if $selectedProduct}
    <div class="bg-slate-50 border-t border-slate-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-2">
          <div class="flex items-center space-x-2 text-sm text-slate-700">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
            </svg>
            <span>Working on: <strong>{$selectedProduct.name}</strong></span>
            {#if $selectedProduct.description}
              <span class="text-slate-600">• {$selectedProduct.description}</span>
            {/if}
          </div>
        </div>
      </div>
    </div>
  {/if}
</header>
