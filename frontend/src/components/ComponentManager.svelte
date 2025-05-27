<script lang="ts">
  import { onMount } from 'svelte';
  import AssetManager from './AssetManager.svelte';
  import { productApi } from '../api/products';
  import { safeApiCall } from '../utils/error-handler';
  
  // State variables
  let selectedProduct: string | null = null;
  
  // Load products on mount to populate dropdown
  let products: any[] = [];
  
  onMount(async () => {
    await loadProducts();
  });
  
  // Load products from API
  async function loadProducts() {
    const result = await safeApiCall(() => productApi.getAll());
    if (result) {
      products = result.scopes;
    }
  }
  
  // Function to handle product selection
  function handleProductChange(event: Event) {
    const selectElement = event.target as HTMLSelectElement;
    selectedProduct = selectElement.value || null;
  }
</script>

<div>
  <!-- Header with product filter -->
  <div class="flex justify-between items-end mb-6">
    <h2 class="text-xl font-semibold" style="color: var(--color-text-main);">Asset Identification</h2>
    <div class="w-1/3">
      <label for="product-selector" class="block text-sm font-medium text-gray-700 mb-1">Filter by Product</label>
      <select
        id="product-selector"
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary focus:border-primary"
        on:change={handleProductChange}
      >
        <option value="">All Products</option>
        {#each products as product}
          <option value={product.scope_id}>{product.name} ({product.product_type})</option>
        {/each}
      </select>
    </div>
  </div>

  <!-- Asset Manager Component -->
  <AssetManager productId={selectedProduct} />
</div>
