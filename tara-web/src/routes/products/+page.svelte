<script lang="ts">
  import { onMount } from 'svelte';
  import { selectedProduct } from '../../lib/stores/productStore';
  import { API_BASE_URL } from '$lib/config';
  import { productApi } from '../../lib/api/productApi';
  import type { Product } from '../../lib/types/product';
  import { goto } from '$app/navigation';
  // Replace Lucide icons with SVG for SSR compatibility
  // import { Plus, Search, Filter, Package, Users, Calendar } from '@lucide/svelte';
  import ProductCard from '../../features/products/components/ProductCard.svelte';
  import CreateProductModal from '../../features/products/components/CreateProductModal.svelte';
  import ConfirmationModal from '../../components/ui/ConfirmationModal.svelte';
  import { authStore } from '$lib/stores/auth';
  import { get } from 'svelte/store';
  import { canPerformTARA, isReadOnly } from '$lib/utils/permissions';

  let products: Product[] = [];
  let filteredProducts: Product[] = [];
  let isLoading = true;
  let error = '';
  let showCreateModal = false;
  let showDeleteModal = false;
  let productToDelete: Product | null = null;
  let isDeleting = false;
  let viewMode = 'grid'; // 'grid' or 'list'
  
  // Role-based UI control
  let canManageProducts = false;
  let canViewTARA = false;
  
  // Filters
  let searchQuery = '';

  // Reactive permission checks - wait for auth to be initialized
  $: if ($authStore.isInitialized) {
    canViewTARA = canPerformTARA();
    canManageProducts = canPerformTARA() && !isReadOnly();
    
    if ($authStore.isAuthenticated && !canViewTARA) {
      goto('/unauthorized');
    }
  }

  onMount(() => {
    loadProducts();
  });

  async function loadProducts() {
    isLoading = true;
    error = '';
    
    try {
      const auth = get(authStore);
      const headers: HeadersInit = {
        'Content-Type': 'application/json'
      };
      const tokenFromStorage = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null;
      const token = auth.token ?? tokenFromStorage;
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(`${API_BASE_URL}/products?skip=0&limit=100`, {
        headers
      });
      
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
    if (!canManageProducts) return;
    productToDelete = product;
    showDeleteModal = true;
  }

  async function confirmDelete() {
    if (!productToDelete) return;

    isDeleting = true;
    try {
      const auth = get(authStore);
      const headers: HeadersInit = {
        'Content-Type': 'application/json'
      };
      const tokenFromStorage = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null;
      const token = auth.token ?? tokenFromStorage;
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${API_BASE_URL}/products/${productToDelete.scope_id}`, {
        method: 'DELETE',
        headers
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

<div class="space-y-5">
  <!-- Header -->
  <div class="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-4">
    <div>
      <h1 class="text-xl font-bold tracking-tight" style="color: var(--color-text-primary);">Product Portfolio</h1>
      <p class="text-sm mt-1" style="color: var(--color-text-secondary);">
        Select a product to begin your TARA workflow.
      </p>
    </div>
    {#if canManageProducts}
      <button
        class="px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 self-start"
        style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        on:click={() => showCreateModal = true}
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
        New Product
      </button>
    {/if}
  </div>

  <!-- Filters -->
  <div class="rounded-lg p-3" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
      <div class="relative flex-1 max-w-md">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </div>
        <input
          type="text" placeholder="Search products..." bind:value={searchQuery}
          class="block w-full pl-9 pr-3 py-2 rounded-md text-sm border-0 focus:ring-1 focus:outline-none"
          style="background: var(--color-bg-inset); color: var(--color-text-primary); --tw-ring-color: var(--color-border-focus);"
        />
      </div>
      <div class="flex items-center gap-3">
        <span class="text-xs" style="color: var(--color-text-tertiary);">
          {#if hasActiveFilters}{filteredProducts.length} of {products.length}{:else}{products.length} total{/if}
        </span>
        {#if hasActiveFilters}
          <button on:click={clearFilters} class="text-xs font-medium" style="color: var(--color-text-link);">Clear</button>
        {/if}
        <div class="flex rounded-md overflow-hidden" style="border: 1px solid var(--color-border-default);">
          <button class="p-1.5 transition-colors" style="background: {viewMode === 'grid' ? 'var(--color-bg-elevated)' : 'transparent'}; color: var(--color-text-secondary);" on:click={() => viewMode = 'grid'}>
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
          </button>
          <button class="p-1.5 transition-colors" style="background: {viewMode === 'list' ? 'var(--color-bg-elevated)' : 'transparent'}; color: var(--color-text-secondary);" on:click={() => viewMode = 'list'}>
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Content -->
  {#if isLoading}
    <div class="flex flex-col items-center py-16">
      <div class="animate-spin rounded-full h-7 w-7 border-2 border-t-transparent mb-3" style="border-color: var(--color-accent-primary); border-top-color: transparent;"></div>
      <p class="text-sm" style="color: var(--color-text-tertiary);">Loading products...</p>
    </div>
  {:else if error}
    <div class="rounded-lg p-4" style="background: var(--color-error-bg); border: 1px solid var(--color-error);">
      <h3 class="text-sm font-medium" style="color: var(--color-error);">Error loading products</h3>
      <p class="text-sm mt-1" style="color: var(--color-text-secondary);">{error}</p>
      <button on:click={loadProducts} class="mt-2 px-3 py-1 rounded text-xs font-medium transition-colors" style="background: var(--color-error-bg); color: var(--color-error);">Try again</button>
    </div>
  {:else if filteredProducts.length === 0}
    {#if products.length === 0}
      <div class="relative flex flex-col items-center py-16 text-center">
        <div class="absolute inset-0 radar-bg pointer-events-none"></div>
        <div class="relative z-10 flex flex-col items-center max-w-md">
          <div class="w-14 h-14 rounded-xl flex items-center justify-center mb-4" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border-default);">
            <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-text-tertiary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
          </div>
          <h3 class="text-base font-semibold mb-2" style="color: var(--color-text-primary);">No products yet</h3>
          <p class="text-sm mb-6" style="color: var(--color-text-secondary);">Define your first product scope to begin threat analysis.</p>
          <button class="px-4 py-2 rounded-md text-sm font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);" on:click={() => showCreateModal = true}>Create Your First Product</button>
        </div>
      </div>
    {:else}
      <div class="text-center py-12">
        <h3 class="text-sm font-medium mb-1" style="color: var(--color-text-primary);">No products match your search</h3>
        <button on:click={clearFilters} class="text-xs font-medium" style="color: var(--color-text-link);">Clear filters</button>
      </div>
    {/if}
  {:else if viewMode === 'grid'}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each filteredProducts as product (product.scope_id)}
        <ProductCard {product} isSelected={$selectedProduct?.scope_id === product.scope_id} on:select={() => selectedProduct.set(product)} />
      {/each}
    </div>
  {:else}
    <div class="rounded-lg overflow-hidden" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
      {#each filteredProducts as product, i (product.scope_id)}
        <div
          class="flex items-center justify-between px-4 py-3 cursor-pointer transition-colors"
          style="border-top: {i > 0 ? '1px solid var(--color-border-subtle)' : 'none'}; background: {$selectedProduct?.scope_id === product.scope_id ? 'var(--color-info-bg)' : 'transparent'};"
          on:click={() => selectedProduct.set(product)}
          on:keydown={(e) => e.key === 'Enter' && selectedProduct.set(product)}
          role="button" tabindex="0"
        >
          <div class="flex items-center gap-3 min-w-0 flex-1">
            <div class="w-8 h-8 rounded-md flex items-center justify-center flex-shrink-0" style="background: var(--color-bg-elevated);">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color: var(--color-accent-primary);"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium truncate" style="color: var(--color-text-primary);">{product.name}</span>
                <span class="px-1.5 py-0.5 rounded text-[10px] font-medium" style="background: var(--color-bg-elevated); color: var(--color-text-tertiary);">v{product.version}</span>
              </div>
              <div class="text-xs" style="color: var(--color-text-tertiary);">
                {product.product_type}{#if product.owner_team} · {product.owner_team}{/if}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <span class="px-2 py-0.5 rounded-full text-[10px] font-medium"
              style="background: {product.status === 'production' ? 'var(--color-success-bg)' : product.status === 'development' ? 'var(--color-info-bg)' : 'var(--color-warning-bg)'}; color: {product.status === 'production' ? 'var(--color-success)' : product.status === 'development' ? 'var(--color-info)' : 'var(--color-warning)'};">
              {product.status}
            </span>
            {#if $selectedProduct?.scope_id === product.scope_id}
              <div class="w-2 h-2 rounded-full" style="background: var(--color-accent-primary);"></div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
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
