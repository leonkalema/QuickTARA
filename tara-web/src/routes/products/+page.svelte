<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedProduct } from '../../lib/stores/productStore';
  import { API_BASE_URL } from '$lib/config';
  import { productApi } from '../../lib/api/productApi';
  import type { Product } from '../../lib/types/product';
  // Replace Lucide icons with SVG for SSR compatibility
  // import { Plus, Search, Filter, Package, Users, Calendar } from '@lucide/svelte';
  import ProductCard from '../../features/products/components/ProductCard.svelte';
  import CreateProductModal from '../../features/products/components/CreateProductModal.svelte';
  import ConfirmationModal from '../../components/ui/ConfirmationModal.svelte';

  let products: Product[] = [];
  let filteredProducts: Product[] = [];
  let isLoading = true;
  let error = '';
  let showCreateModal = false;
  let showDeleteModal = false;
  let productToDelete: Product | null = null;
  let isDeleting = false;
  let viewMode = 'grid'; // 'grid' or 'list'
  
  // Filters
  let searchQuery = '';

  onMount(() => {
    loadProducts();
  });

  async function loadProducts() {
    isLoading = true;
    error = '';
    
    try {
      const response = await fetch(`${API_BASE_URL}/products?skip=0&limit=100`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // The API returns { scopes: Product[], total: number }
      if (data.scopes && Array.isArray(data.scopes)) {
        products = data.scopes;
      } else {
        products = [];
      }
      
      applyFilters();
    } catch (err) {
      error = 'Failed to load products. Please check your connection and try again.';
      console.error('Error loading products:', err);
    } finally {
      isLoading = false;
    }
  }

  function applyFilters() {
    filteredProducts = products.filter(product => {
      const matchesSearch = !searchQuery || 
        product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.description?.toLowerCase().includes(searchQuery.toLowerCase());
      
      return matchesSearch;
    });
  }

  function handleFilterChange() {
    applyFilters();
  }

  function handleProductCreated(event: CustomEvent<Product>) {
    const newProduct = event.detail;
    products = [newProduct, ...products];
    applyFilters();
    showCreateModal = false;
  }

  function handleEditProduct(product: Product) {
    // TODO: Implement edit functionality
    console.log('Edit product:', product);
  }

  function handleDeleteProduct(product: Product) {
    productToDelete = product;
    showDeleteModal = true;
  }

  async function confirmDelete() {
    if (!productToDelete) return;

    isDeleting = true;
    try {
      const response = await fetch(`${API_BASE_URL}/products/${productToDelete.scope_id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Remove from local state
      products = products.filter(p => p.scope_id !== productToDelete?.scope_id);
      applyFilters();
      
      showDeleteModal = false;
      productToDelete = null;
    } catch (err) {
      error = 'Failed to delete product. Please try again.';
      console.error('Error deleting product:', err);
    } finally {
      isDeleting = false;
    }
  }

  function cancelDelete() {
    showDeleteModal = false;
    productToDelete = null;
  }

  function handleProductUpdated() {
    loadProducts();
  }

  function handleProductDeleted() {
    loadProducts();
  }

  function clearFilters() {
    searchQuery = '';
  }

  $: hasActiveFilters = searchQuery;

  $: if (searchQuery) {
    handleFilterChange();
  }
</script>

<svelte:head>
  <title>Products - QuickTARA</title>
</svelte:head>

<div class="space-y-6">
  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start space-y-4 lg:space-y-0">
    <div>
      <h1 class="text-3xl font-bold text-gray-900">Product Portfolio</h1>
      <p class="mt-2 text-gray-600 max-w-2xl">
        Manage your product ecosystem and threat analysis scope. Select a product to begin your security assessment workflow.
      </p>
    </div>
    <button
      class="bg-slate-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-slate-700 transition-colors flex items-center space-x-2 self-start"
      on:click={() => showCreateModal = true}
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
      </svg>
      <span>New Product</span>
    </button>
  </div>

  <!-- Filters and Controls -->
  <div class="bg-white rounded-lg border border-gray-200 p-4">
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
      <!-- Search and Filters -->
      <div class="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 flex-1">
        <!-- Search -->
        <div class="relative flex-1 max-w-md">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <input
            type="text"
            placeholder="Search products..."
            bind:value={searchQuery}
            class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-slate-500 focus:border-slate-500"
          />
        </div>


        <!-- Clear Filters -->
        {#if hasActiveFilters}
          <button
            on:click={clearFilters}
            class="text-slate-600 hover:text-slate-800 px-3 py-2 text-sm font-medium transition-colors"
          >
            Clear filters
          </button>
        {/if}
      </div>

      <!-- View Controls and Count -->
      <div class="flex items-center space-x-4">
        <!-- Results Count -->
        <div class="text-sm text-gray-500">
          {#if hasActiveFilters}
            Showing {filteredProducts.length} of {products.length} products
          {:else}
            {products.length} products total
          {/if}
        </div>

        <!-- View Mode Toggle -->
        <div class="flex items-center border border-gray-300 rounded-md">
          <button
            class="p-2 {viewMode === 'grid' ? 'bg-slate-100 text-slate-700' : 'text-gray-500 hover:text-gray-700'} transition-colors"
            on:click={() => viewMode = 'grid'}
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
            </svg>
          </button>
          <button
            class="p-2 {viewMode === 'list' ? 'bg-slate-100 text-slate-700' : 'text-gray-500 hover:text-gray-700'} transition-colors"
            on:click={() => viewMode = 'list'}
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Content -->
  {#if isLoading}
    <div class="flex flex-col justify-center items-center py-16">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600 mb-4"></div>
      <p class="text-gray-500">Loading products...</p>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-start">
        <svg class="w-6 h-6 text-red-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Error loading products</h3>
          <p class="text-sm text-red-700 mt-1">{error}</p>
          <button
            on:click={loadProducts}
            class="mt-3 bg-red-100 text-red-800 px-3 py-1 rounded text-sm hover:bg-red-200 transition-colors"
          >
            Try again
          </button>
        </div>
      </div>
    </div>
  {:else if filteredProducts.length === 0}
    <div class="text-center py-16">
      {#if products.length === 0}
        <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No products yet</h3>
        <p class="text-gray-500 mb-6 max-w-md mx-auto">
          Get started by creating your first product to analyze. Define your system boundaries and begin your security assessment.
        </p>
        <button
          class="bg-slate-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-slate-700 transition-colors inline-flex items-center space-x-2"
          on:click={() => showCreateModal = true}
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          <span>Create Your First Product</span>
        </button>
      {:else}
        <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No products match your filters</h3>
        <p class="text-gray-500 mb-6">
          Try adjusting your search criteria or clearing filters to see more results.
        </p>
        <button
          on:click={clearFilters}
          class="text-slate-600 hover:text-slate-800 font-medium"
        >
          Clear all filters
        </button>
      {/if}
    </div>
  {:else}
    <!-- Grid View -->
    {#if viewMode === 'grid'}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each filteredProducts as product (product.scope_id)}
          <ProductCard
            {product}
            isSelected={$selectedProduct?.scope_id === product.scope_id}
            on:select={() => selectedProduct.set(product)}
          />
        {/each}
      </div>
    {:else}
      <!-- List View -->
      <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div class="divide-y divide-gray-200">
          {#each filteredProducts as product (product.scope_id)}
            <div 
              class="p-4 hover:bg-gray-50 cursor-pointer transition-colors {$selectedProduct?.scope_id === product.scope_id ? 'bg-slate-50 border-l-4 border-slate-500' : ''}"
              on:click={() => selectedProduct.set(product)}
              role="button"
              tabindex="0"
              on:keydown={(e) => e.key === 'Enter' && selectedProduct.set(product)}
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4 flex-1">
                  <div class="flex-shrink-0">
                    <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center space-x-3">
                      <h3 class="text-lg font-medium text-gray-900 truncate">
                        {product.name}
                      </h3>
                      <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                        v{product.version}
                      </span>
                    </div>
                    <div class="flex items-center space-x-4 mt-1">
                      <span class="text-sm text-gray-500 capitalize">
                        {product.product_type}
                      </span>
                      {#if product.owner_team}
                        <span class="text-sm text-gray-500 flex items-center">
                          <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a4 4 0 11-8 0 4 4 0 018 0z"></path>
                          </svg>
                          {product.owner_team}
                        </span>
                      {/if}
                      {#if product.created_at}
                        <span class="text-sm text-gray-500 flex items-center">
                          <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                          </svg>
                          {new Date(product.created_at).toLocaleDateString()}
                        </span>
                      {/if}
                    </div>
                    {#if product.description}
                      <p class="text-sm text-gray-600 mt-2 line-clamp-2">
                        {product.description}
                      </p>
                    {/if}
                  </div>
                </div>
                <div class="flex items-center space-x-3">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {product.status === 'production' ? 'bg-green-100 text-green-800' : product.status === 'testing' ? 'bg-yellow-100 text-yellow-800' : product.status === 'development' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'}">
                    {product.status}
                  </span>
                  {#if $selectedProduct?.scope_id === product.scope_id}
                    <div class="w-3 h-3 bg-slate-600 rounded-full"></div>
                  {/if}
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  {/if}
</div>

<!-- Create Product Modal -->
{#if showCreateModal}
  <CreateProductModal 
    bind:isOpen={showCreateModal}
    on:create={handleProductCreated}
    on:close={() => showCreateModal = false}
  />
{/if}

{#if showDeleteModal && productToDelete}
  <ConfirmationModal
    bind:isOpen={showDeleteModal}
    title="Delete Product"
    message="Are you sure you want to delete '{productToDelete.name}'? This action cannot be undone."
    confirmText="Delete"
    cancelText="Cancel"
    variant="danger"
    isLoading={isDeleting}
    on:confirm={confirmDelete}
    on:cancel={cancelDelete}
  />
{/if}

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
