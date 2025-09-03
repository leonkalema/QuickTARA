<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { selectedProduct } from '../../../lib/stores/productStore';
  import { notifications } from '../../../lib/stores/notificationStore';
  import { 
    ArrowLeft, 
    Edit, 
    Trash2, 
    Package, 
    Shield, 
    MapPin, 
    Calendar,
    User,
    FileText
  } from '@lucide/svelte';
  import { productApi } from '../../../lib/api/productApi';

  let product: any = null;
  let loading = true;
  let error = '';
  let isEditing = false;
  let editedProduct: any = {};
  let isSaving = false;

  $: productId = $page.params.id;

  onMount(async () => {
    await loadProduct();
  });

  async function loadProduct() {
    if (!productId) return;
    
    loading = true;
    error = '';
    
    try {
      product = await productApi.getById(productId);
      // Auto-select this product when viewing details
      selectedProduct.set(product);
    } catch (err) {
      error = 'Failed to load product details';
      console.error('Error loading product:', err);
    } finally {
      loading = false;
    }
  }

  function handleEdit() {
    if (isEditing) {
      // Save changes
      saveProduct();
    } else {
      // Enter edit mode
      isEditing = true;
      editedProduct = { ...product };
    }
  }

  function cancelEdit() {
    isEditing = false;
    editedProduct = {};
  }

  async function saveProduct() {
    if (!productId) return;
    
    isSaving = true;
    try {
      const updatedProduct = await productApi.update(productId, editedProduct);
      product = updatedProduct;
      selectedProduct.set(updatedProduct);
      isEditing = false;
      editedProduct = {};
      notifications.show('Product updated successfully!', 'success');
    } catch (err) {
      notifications.show('Failed to update product', 'error');
      console.error('Error updating product:', err);
    } finally {
      isSaving = false;
    }
  }

  function goBack() {
    goto('/products');
  }

  function getStatusColor(status: string) {
    switch (status) {
      case 'production': return 'bg-green-100 text-green-800';
      case 'testing': return 'bg-yellow-100 text-yellow-800';
      case 'development': return 'bg-blue-100 text-blue-800';
      case 'deprecated': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  }
</script>

<svelte:head>
  <title>{product ? `${product.name} - QuickTARA` : 'Product Details - QuickTARA'}</title>
</svelte:head>

<div class="max-w-4xl mx-auto">
  <!-- Header with Back Button -->
  <div class="mb-6">
    <button
      on:click={goBack}
      class="flex items-center text-gray-600 hover:text-gray-900 mb-4"
    >
      <ArrowLeft class="w-4 h-4 mr-2" />
      Back to Products
    </button>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600">Loading product details...</span>
    </div>
  {:else if error}
    <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <p class="text-red-800">{error}</p>
      <button
        on:click={loadProduct}
        class="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
      >
        Try Again
      </button>
    </div>
  {:else if product}
    <!-- Product Header -->
    <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-center space-x-3 mb-2">
            <Package class="w-6 h-6 text-blue-600" />
            {#if isEditing}
              <input
                bind:value={editedProduct.name}
                class="text-2xl font-bold text-gray-900 bg-transparent border-b-2 border-blue-300 focus:border-blue-500 outline-none"
                placeholder="Product name"
              />
            {:else}
              <h1 class="text-2xl font-bold text-gray-900">{product.name}</h1>
            {/if}
            <span class="px-2 py-1 text-xs font-medium rounded-full {getStatusColor('production')}">
              {product.product_type}
            </span>
          </div>
          
          {#if isEditing}
            <textarea
              bind:value={editedProduct.description}
              class="w-full text-gray-600 mb-4 bg-transparent border border-gray-300 rounded-md p-2 focus:border-blue-500 outline-none resize-none"
              placeholder="Product description"
              rows="3"
            ></textarea>
          {:else if product.description}
            <p class="text-gray-600 mb-4">{product.description}</p>
          {/if}

          <div class="flex items-center space-x-6 text-sm text-gray-500">
            <div class="flex items-center">
              <Shield class="w-4 h-4 mr-1" />
              Safety Level: 
              {#if isEditing}
                <select
                  bind:value={editedProduct.safety_level}
                  class="ml-1 bg-transparent border border-gray-300 rounded px-2 py-1 focus:border-blue-500 outline-none"
                >
                  <option value="QM">QM</option>
                  <option value="ASIL-A">ASIL-A</option>
                  <option value="ASIL-B">ASIL-B</option>
                  <option value="ASIL-C">ASIL-C</option>
                  <option value="ASIL-D">ASIL-D</option>
                </select>
              {:else}
                {product.safety_level}
              {/if}
            </div>
            <div class="flex items-center">
              <MapPin class="w-4 h-4 mr-1" />
              Location: 
              {#if isEditing}
                <input
                  bind:value={editedProduct.location}
                  class="ml-1 bg-transparent border border-gray-300 rounded px-2 py-1 focus:border-blue-500 outline-none"
                  placeholder="Location"
                />
              {:else}
                {product.location || 'Not specified'}
              {/if}
            </div>
            <div class="flex items-center">
              <Calendar class="w-4 h-4 mr-1" />
              Created: {new Date(product.created_at).toLocaleDateString()}
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center space-x-2">
          {#if isEditing}
            <button
              on:click={cancelEdit}
              class="flex items-center px-3 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              on:click={handleEdit}
              disabled={isSaving}
              class="flex items-center px-3 py-2 text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg transition-colors"
            >
              {#if isSaving}
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Saving...
              {:else}
                Save
              {/if}
            </button>
          {:else}
            <button
              on:click={handleEdit}
              class="flex items-center px-3 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Edit class="w-4 h-4 mr-2" />
              Edit
            </button>
          {/if}
        </div>
      </div>
    </div>

    <!-- Product Details Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Technical Details -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Technical Details</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Product ID</label>
            <p class="text-sm text-gray-900 font-mono bg-gray-50 px-2 py-1 rounded">{product.scope_id}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Trust Zone</label>
            <p class="text-sm text-gray-900">{product.trust_zone || 'Standard'}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Version</label>
            <p class="text-sm text-gray-900">{product.version || 1}</p>
          </div>
        </div>
      </div>

      <!-- Configuration -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Configuration</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Interfaces</label>
            {#if product.interfaces && product.interfaces.length > 0}
              <div class="flex flex-wrap gap-2">
                {#each product.interfaces as productInterface}
                  <span class="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">{productInterface}</span>
                {/each}
              </div>
            {:else}
              <p class="text-sm text-gray-500">No interfaces defined</p>
            {/if}
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Access Points</label>
            {#if product.access_points && product.access_points.length > 0}
              <div class="flex flex-wrap gap-2">
                {#each product.access_points as point}
                  <span class="px-2 py-1 bg-green-50 text-green-700 text-xs rounded">{point}</span>
                {/each}
              </div>
            {:else}
              <p class="text-sm text-gray-500">No access points defined</p>
            {/if}
          </div>
        </div>
      </div>

      <!-- Analysis Scope -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Analysis Scope</h2>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Boundaries</label>
            {#if product.boundaries && product.boundaries.length > 0}
              <ul class="text-sm text-gray-900 space-y-1">
                {#each product.boundaries as boundary}
                  <li class="flex items-start">
                    <span class="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                    {boundary}
                  </li>
                {/each}
              </ul>
            {:else}
              <p class="text-sm text-gray-500">No boundaries defined</p>
            {/if}
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Objectives</label>
            {#if product.objectives && product.objectives.length > 0}
              <ul class="text-sm text-gray-900 space-y-1">
                {#each product.objectives as objective}
                  <li class="flex items-start">
                    <span class="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                    {objective}
                  </li>
                {/each}
              </ul>
            {:else}
              <p class="text-sm text-gray-500">No objectives defined</p>
            {/if}
          </div>
        </div>
      </div>

      <!-- Stakeholders -->
      <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Stakeholders</h2>
        
        {#if product.stakeholders && product.stakeholders.length > 0}
          <div class="space-y-2">
            {#each product.stakeholders as stakeholder}
              <div class="flex items-center">
                <User class="w-4 h-4 text-gray-400 mr-2" />
                <span class="text-sm text-gray-900">{stakeholder}</span>
              </div>
            {/each}
          </div>
        {:else}
          <p class="text-sm text-gray-500">No stakeholders defined</p>
        {/if}
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
      <h3 class="text-lg font-semibold text-blue-900 mb-4">Next Steps</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a
          href="/assets"
          class="flex items-center p-4 bg-white rounded-lg border border-blue-200 hover:border-blue-300 transition-colors"
        >
          <Package class="w-5 h-5 text-blue-600 mr-3" />
          <div>
            <div class="font-medium text-blue-900">Manage Assets</div>
            <div class="text-sm text-blue-700">Add system components</div>
          </div>
        </a>
        
        <a
          href="/damage-scenarios"
          class="flex items-center p-4 bg-white rounded-lg border border-blue-200 hover:border-blue-300 transition-colors"
        >
          <Shield class="w-5 h-5 text-blue-600 mr-3" />
          <div>
            <div class="font-medium text-blue-900">Damage Scenarios</div>
            <div class="text-sm text-blue-700">Define potential damages</div>
          </div>
        </a>
        
        <a
          href="/reports"
          class="flex items-center p-4 bg-white rounded-lg border border-blue-200 hover:border-blue-300 transition-colors"
        >
          <FileText class="w-5 h-5 text-blue-600 mr-3" />
          <div>
            <div class="font-medium text-blue-900">Generate Report</div>
            <div class="text-sm text-blue-700">Export analysis results</div>
          </div>
        </a>
      </div>
    </div>
  {:else}
    <div class="text-center py-12">
      <p class="text-gray-500">Product not found</p>
    </div>
  {/if}
</div>
