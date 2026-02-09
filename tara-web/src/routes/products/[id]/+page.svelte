<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { selectedProduct } from '../../../lib/stores/productStore';
  import { notifications } from '../../../lib/stores/notificationStore';
  import { productPermissions } from '../../../lib/stores/productPermissions';
  import type { CreateProductRequest, Product, ProductPermissions } from '../../../lib/types/product';
  import { 
    ArrowLeft, 
    Edit, 
    Trash2, 
    Package, 
    Shield, 
    MapPin, 
    Calendar,
    User,
    Lock
  } from '@lucide/svelte';
  import { productApi } from '../../../lib/api/productApi';
  import { authStore } from '$lib/stores/auth';
  import { API_BASE_URL } from '$lib/config';
  import { get } from 'svelte/store';
  import ProductQuickActions from '../../../features/products/components/ProductQuickActions.svelte';
  import ProductDetailsGrid from '../../../features/products/components/ProductDetailsGrid.svelte';
  import { notifyProductsChanged } from '$lib/stores/productEvents';

  type OrganizationOption = {
    organizationId: string;
    name: string;
  };

  let product: Product | null = null;
  let loading = true;
  let error = '';
  let isEditing = false;
  let editedProduct: Partial<CreateProductRequest> = {};
  let isSaving = false;
  let permissions: ProductPermissions | null = null;

  let organizations: OrganizationOption[] = [];
  let selectedOrganizationId = '';
  let isLoadingOrganizations = false;

  $: productId = $page.params.id;

  onMount(async () => {
    await loadProduct();
  });

  const getAuthToken = (): string | null => {
    const auth = get(authStore);
    const tokenFromStorage = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null;
    return auth.token ?? tokenFromStorage;
  };

  const loadOrganizations = async (): Promise<void> => {
    isLoadingOrganizations = true;
    try {
      const auth = get(authStore);
      const isSuperuser = (auth.user as { is_superuser?: boolean } | null)?.is_superuser === true;
      const isToolAdmin = isSuperuser || authStore.hasRole('tool_admin');
      const orgsFromUser = auth.user?.organizations ?? [];
      if (!isToolAdmin) {
        organizations = orgsFromUser.map((o) => ({ organizationId: o.organization_id, name: o.name }));
      } else {
        const token = getAuthToken();
        const headers: HeadersInit = { 'Content-Type': 'application/json' };
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const response = await fetch(`${API_BASE_URL}/organizations`, { headers });
        if (response.ok) {
          const data = (await response.json()) as { organizations?: Array<{ organization_id: string; name: string }> };
          const orgList = data.organizations ?? [];
          organizations = orgList.map((o) => ({ organizationId: o.organization_id, name: o.name }));
        } else {
          organizations = [];
        }
      }
      if (!selectedOrganizationId && organizations.length === 1) {
        selectedOrganizationId = organizations[0]?.organizationId ?? '';
      }
    } catch {
      organizations = [];
    } finally {
      isLoadingOrganizations = false;
    }
  };

  async function loadProduct() {
    if (!productId) return;
    
    loading = true;
    error = '';
    
    try {
      product = await productApi.getById(productId);
      // Auto-select this product when viewing details
      selectedProduct.set(product);
      // Fetch permissions for this product
      permissions = await productPermissions.fetchPermissions(productId);
      selectedOrganizationId = product.organization_id ?? '';
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
      editedProduct = { ...(product ?? {}) };
      loadOrganizations();
    }
  }

  function cancelEdit() {
    isEditing = false;
    editedProduct = {};
    selectedOrganizationId = product?.organization_id ?? '';
  }

  async function saveProduct() {
    if (!productId) return;
    if (!selectedOrganizationId) {
      notifications.show('Department is required', 'error');
      return;
    }
    isSaving = true;
    try {
      const payload: Partial<CreateProductRequest> = {
        ...editedProduct,
        organization_id: selectedOrganizationId
      };
      const updatedProduct = await productApi.update(productId, payload);
      product = updatedProduct;
      selectedProduct.set(updatedProduct);
      notifyProductsChanged();
      isEditing = false;
      editedProduct = {};
      selectedOrganizationId = updatedProduct.organization_id ?? '';
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

  const formatCreatedAt = (createdAt: string | undefined): string => {
    if (!createdAt) return 'Unknown';
    return new Date(createdAt).toLocaleDateString();
  };

  const getOrganizationName = (organizationId: string | undefined): string => {
    if (!organizationId) return 'Unassigned';
    const auth = get(authStore);
    const orgs = auth.user?.organizations ?? [];
    const match = orgs.find((o) => o.organization_id === organizationId);
    return match?.name ?? 'Unassigned';
  };
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
    <div class="rounded-lg p-6 mb-6" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
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
            {#if !isEditing}
              <span class="px-2 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-700">
                {getOrganizationName(product.organization_id)}
              </span>
            {/if}
          </div>
          
          {#if isEditing}
            <textarea
              bind:value={editedProduct.description}
              class="w-full text-gray-600 mb-4 bg-transparent border border-gray-300 rounded-md p-2 focus:border-blue-500 outline-none resize-none"
              placeholder="Product description"
              rows="3"
            ></textarea>
            <div class="mb-4">
              <label for="department" class="block text-sm font-medium text-gray-700 mb-1">
                Department *
              </label>
              <select
                id="department"
                bind:value={selectedOrganizationId}
                required
                disabled={isLoadingOrganizations}
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="">{isLoadingOrganizations ? 'Loading departments...' : 'Select department'}</option>
                {#each organizations as org (org.organizationId)}
                  <option value={org.organizationId}>{org.name}</option>
                {/each}
              </select>
            </div>
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
                  <option value="ASIL A">ASIL A</option>
                  <option value="ASIL B">ASIL B</option>
                  <option value="ASIL C">ASIL C</option>
                  <option value="ASIL D">ASIL D</option>
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
              Created: {formatCreatedAt(product.created_at)}
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center space-x-2">
          {#if permissions?.role}
            <span class="px-2 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-700">
              Your role: {permissions.role}
            </span>
          {/if}
          
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
          {:else if permissions?.can_edit}
            <button
              on:click={handleEdit}
              class="flex items-center px-3 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              <Edit class="w-4 h-4 mr-2" />
              Edit
            </button>
          {:else}
            <div class="flex items-center px-3 py-2 text-gray-400 bg-gray-50 rounded-lg">
              <Lock class="w-4 h-4 mr-2" />
              View Only
            </div>
          {/if}
          
          {#if permissions?.can_delete}
            <button
              on:click={() => { /* TODO: implement delete */ }}
              class="flex items-center px-3 py-2 text-red-700 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
            >
              <Trash2 class="w-4 h-4 mr-2" />
              Delete
            </button>
          {/if}
        </div>
      </div>
    </div>

    <ProductDetailsGrid {product} />

    <ProductQuickActions />
  {:else}
    <div class="text-center py-12">
      <p class="text-gray-500">Product not found</p>
    </div>
  {/if}
</div>
