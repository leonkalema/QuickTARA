<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { Search, Package, ChevronRight, BarChart3 } from '@lucide/svelte';
  import { productApi } from '../../api/products';
  import { damageScenarioApi } from '../../api/damage-scenarios';
  import { safeApiCall } from '../../utils/error-handler';

  export let selectedProductId: string | null = null;

  const dispatch = createEventDispatcher();

  let products: Array<{
    component_id: string;
    name: string;
    type: string;
    description?: string;
    scenarioCount: number;
  }> = [];
  let filteredProducts: typeof products = [];
  let searchTerm = '';
  let isLoading = true;
  let error = '';

  onMount(async () => {
    await loadProducts();
  });

  async function loadProducts() {
    isLoading = true;
    error = '';
    
    try {
      const [productsResult, scenariosResult] = await Promise.all([
        safeApiCall(() => productApi.getAll()),
        safeApiCall(() => damageScenarioApi.getAll())
      ]);

      if (productsResult && scenariosResult) {
        // Get products from the scopes array (API returns products as "scopes")
        const allProducts = productsResult.scopes || [];

        // Count scenarios per product
        const scenarios = scenariosResult.scenarios || [];
        products = allProducts.map((product: any) => ({
          component_id: product.scope_id, // Map scope_id to component_id for consistency
          name: product.name,
          type: product.product_type,
          description: product.description,
          ...product,
          scenarioCount: scenarios.filter(s => 
            s.scope_id === product.scope_id
          ).length
        }));

        filteredProducts = products;
      }
    } catch (err) {
      console.error('Error loading products:', err);
      error = 'Failed to load products. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  function handleSearch() {
    if (!searchTerm.trim()) {
      filteredProducts = products;
      return;
    }

    const term = searchTerm.toLowerCase();
    filteredProducts = products.filter(product =>
      product.name.toLowerCase().includes(term) ||
      product.type.toLowerCase().includes(term) ||
      product.description?.toLowerCase().includes(term)
    );
  }

  function selectProduct(product: typeof products[0]) {
    selectedProductId = product.component_id;
    dispatch('productSelected', {
      productId: product.component_id,
      productName: product.name,
      productType: product.type
    });
  }

  $: handleSearch();
</script>

<div class="space-y-6">
  <!-- Header -->
  <div class="text-center">
    <Package class="mx-auto h-12 w-12 text-blue-600 mb-4" />
    <h2 class="text-2xl font-bold text-gray-900">Select Product</h2>
    <p class="text-gray-600 mt-2">Choose a product to view and manage its damage scenarios</p>
  </div>

  <!-- Search -->
  <div class="relative max-w-md mx-auto">
    <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
    <input
      type="text"
      bind:value={searchTerm}
      placeholder="Search products..."
      class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    />
  </div>

  <!-- Loading State -->
  {#if isLoading}
    <div class="text-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-gray-600 mt-2">Loading products...</p>
    </div>
  {:else if error}
    <!-- Error State -->
    <div class="text-center py-12">
      <div class="bg-red-50 border border-red-200 rounded-lg p-4 max-w-md mx-auto">
        <p class="text-red-700">{error}</p>
        <button 
          on:click={loadProducts}
          class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    </div>
  {:else if filteredProducts.length === 0}
    <!-- Empty State -->
    <div class="text-center py-12">
      <Package class="mx-auto h-16 w-16 text-gray-300 mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No products found</h3>
      <p class="text-gray-600">
        {searchTerm ? 'Try adjusting your search terms.' : 'No products available.'}
      </p>
    </div>
  {:else}
    <!-- Products Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-6xl mx-auto">
      {#each filteredProducts as product}
        <button
          on:click={() => selectProduct(product)}
          class="bg-white border border-gray-200 rounded-lg p-6 hover:border-blue-300 hover:shadow-md transition-all duration-200 text-left group"
          data-testid="product-card-{product.component_id}"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                {product.name}
              </h3>
              <p class="text-sm text-gray-500 mt-1">{product.type}</p>
            </div>
            <ChevronRight class="h-5 w-5 text-gray-400 group-hover:text-blue-600 transition-colors" />
          </div>

          {#if product.description}
            <p class="text-sm text-gray-600 mb-3 line-clamp-2">{product.description}</p>
          {/if}

          <div class="flex items-center justify-between">
            <div class="flex items-center text-sm text-gray-500">
              <BarChart3 class="h-4 w-4 mr-1" />
              <span>{product.scenarioCount} scenarios</span>
            </div>
            
            {#if product.scenarioCount > 0}
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Active
              </span>
            {:else}
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                New
              </span>
            {/if}
          </div>
        </button>
      {/each}
    </div>
  {/if}

  <!-- Quick Stats -->
  {#if !isLoading && !error && filteredProducts.length > 0}
    <div class="bg-gray-50 rounded-lg p-4 max-w-2xl mx-auto">
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <div class="text-2xl font-bold text-gray-900">{filteredProducts.length}</div>
          <div class="text-sm text-gray-600">Products</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-gray-900">
            {filteredProducts.reduce((sum, p) => sum + p.scenarioCount, 0)}
          </div>
          <div class="text-sm text-gray-600">Total Scenarios</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-gray-900">
            {filteredProducts.filter(p => p.scenarioCount > 0).length}
          </div>
          <div class="text-sm text-gray-600">Active Products</div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
