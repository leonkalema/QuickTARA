<script lang="ts">
  import { ChevronDown, Plus } from '@lucide/svelte';
  import { selectedProduct } from '../../lib/stores/productStore';
  import { goto } from '$app/navigation';

  let showDropdown = false;

  function selectProduct() {
    showDropdown = false;
    goto('/products');
  }

  function manageProducts() {
    showDropdown = false;
    goto('/products');
  }
</script>

<!-- Product Selector Component -->
<div class="relative">
  {#if $selectedProduct}
    <!-- Selected Product Display -->
    <button 
      class="flex items-center space-x-2 bg-blue-50 border border-blue-200 px-3 py-2 rounded-lg hover:bg-blue-100 transition-colors"
      on:click={() => showDropdown = !showDropdown}
    >
      <div class="w-2 h-2 bg-blue-600 rounded-full"></div>
      <span class="text-sm font-medium text-blue-900">
        {$selectedProduct.name}
      </span>
      <ChevronDown class="w-4 h-4 text-blue-700" />
    </button>
  {:else}
    <!-- No Product Selected -->
    <button 
      class="flex items-center space-x-2 bg-gray-100 border border-gray-300 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors"
      on:click={() => showDropdown = !showDropdown}
    >
      <span class="text-sm font-medium text-gray-700">Select Product</span>
      <ChevronDown class="w-4 h-4 text-gray-600" />
    </button>
  {/if}

  <!-- Dropdown Menu -->
  {#if showDropdown}
    <div class="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
      <div class="p-2">
        {#if $selectedProduct}
          <div class="px-3 py-2 text-xs font-medium text-gray-500 uppercase tracking-wide">
            Current Product
          </div>
          <div class="px-3 py-2 bg-blue-50 rounded-md mb-2">
            <div class="font-medium text-blue-900">{$selectedProduct.name}</div>
            <div class="text-sm text-blue-700">{$selectedProduct.product_type}</div>
            {#if $selectedProduct.description}
              <div class="text-xs text-blue-600 mt-1">{$selectedProduct.description}</div>
            {/if}
          </div>
        {/if}

        <div class="border-t border-gray-100 pt-2">
          <button
            class="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md"
            on:click={selectProduct}
          >
            <Plus class="w-4 h-4 mr-2" />
            Change Product
          </button>
          
          <button
            class="w-full flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md"
            on:click={manageProducts}
          >
            Manage Products
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<!-- Click outside to close -->
{#if showDropdown}
  <div 
    class="fixed inset-0 z-40" 
    on:click={() => showDropdown = false}
  ></div>
{/if}
