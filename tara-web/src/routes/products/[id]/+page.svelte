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

  function getStatusStyle(status: string): string {
    switch (status) {
      case 'production': return 'background: color-mix(in srgb, var(--color-status-accepted-text, #10b981) 15%, transparent); color: var(--color-status-accepted-text, #10b981);';
      case 'testing': return 'background: color-mix(in srgb, var(--color-status-draft-text, #f59e0b) 15%, transparent); color: var(--color-status-draft-text, #f59e0b);';
      case 'development': return 'background: color-mix(in srgb, var(--color-accent-primary) 15%, transparent); color: var(--color-accent-primary);';
      case 'deprecated': return 'background: color-mix(in srgb, var(--color-error) 15%, transparent); color: var(--color-error);';
      default: return 'background: var(--color-bg-elevated); color: var(--color-text-secondary);';
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
      class="flex items-center text-xs mb-4 transition-colors" style="color: var(--color-text-secondary);"
    >
      <ArrowLeft class="w-3.5 h-3.5 mr-2" />
      Back to Products
    </button>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-6 w-6 border-2 border-t-transparent" style="border-color: var(--color-accent-primary);"></div>
      <span class="ml-3 text-xs" style="color: var(--color-text-tertiary);">Loading product details...</span>
    </div>
  {:else if error}
    <div class="rounded-lg p-6 text-center" style="background: color-mix(in srgb, var(--color-error) 10%, var(--color-bg-surface)); border: 1px solid color-mix(in srgb, var(--color-error) 30%, transparent);">
      <p class="text-xs" style="color: var(--color-error);">{error}</p>
      <button
        on:click={loadProduct}
        class="mt-4 px-4 py-2 text-xs font-medium rounded-lg transition-colors" style="background: var(--color-error); color: var(--color-text-inverse);"
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
            <Package class="w-5 h-5" style="color: var(--color-accent-primary);" />
            {#if isEditing}
              <input
                bind:value={editedProduct.name}
                class="text-lg font-bold bg-transparent outline-none" style="color: var(--color-text-primary); border-bottom: 2px solid var(--color-accent-primary);"
                placeholder="Product name"
              />
            {:else}
              <h1 class="text-lg font-bold" style="color: var(--color-text-primary);">{product.name}</h1>
            {/if}
            <span class="px-2 py-0.5 text-[10px] font-medium rounded-full" style="{getStatusStyle('production')}">
              {product.product_type}
            </span>
            {#if !isEditing}
              <span class="px-2 py-0.5 text-[10px] font-medium rounded-full" style="background: var(--color-bg-elevated); color: var(--color-text-secondary);">
                {getOrganizationName(product.organization_id)}
              </span>
            {/if}
          </div>
          
          {#if isEditing}
            <textarea
              bind:value={editedProduct.description}
              class="w-full mb-4 rounded-md p-2 outline-none resize-none text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              placeholder="Product description"
              rows="3"
            ></textarea>
            <div class="mb-4">
              <label for="department" class="block text-[10px] font-medium mb-1" style="color: var(--color-text-tertiary);">
                Department *
              </label>
              <select
                id="department"
                bind:value={selectedOrganizationId}
                required
                disabled={isLoadingOrganizations}
                class="mt-1 block w-full rounded-md text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              >
                <option value="">{isLoadingOrganizations ? 'Loading departments...' : 'Select department'}</option>
                {#each organizations as org (org.organizationId)}
                  <option value={org.organizationId}>{org.name}</option>
                {/each}
              </select>
            </div>
          {:else if product.description}
            <p class="text-xs mb-4" style="color: var(--color-text-secondary);">{product.description}</p>
          {/if}

          <div class="flex items-center space-x-6 text-xs" style="color: var(--color-text-tertiary);">
            <div class="flex items-center">
              <Shield class="w-4 h-4 mr-1" />
              Safety Level: 
              {#if isEditing}
                <select
                  bind:value={editedProduct.safety_level}
                  class="ml-1 rounded px-2 py-1 outline-none text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
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
                  class="ml-1 rounded px-2 py-1 outline-none text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
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
            <span class="px-2 py-0.5 text-[10px] font-medium rounded-full" style="background: var(--color-bg-elevated); color: var(--color-text-secondary);">
              Your role: {permissions.role}
            </span>
          {/if}
          
          {#if isEditing}
            <button
              on:click={cancelEdit}
              class="flex items-center px-3 py-2 text-xs rounded-lg transition-colors" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
            >
              Cancel
            </button>
            <button
              on:click={handleEdit}
              disabled={isSaving}
              class="flex items-center px-3 py-2 text-xs font-medium disabled:opacity-50 rounded-lg transition-colors" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
            >
              {#if isSaving}
                <div class="animate-spin rounded-full h-4 w-4 border-2 border-t-transparent mr-2" style="border-color: var(--color-text-inverse);"></div>
                Saving...
              {:else}
                Save
              {/if}
            </button>
          {:else if permissions?.can_edit}
            <button
              on:click={handleEdit}
              class="flex items-center px-3 py-2 text-xs rounded-lg transition-colors" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
            >
              <Edit class="w-3.5 h-3.5 mr-2" />
              Edit
            </button>
          {:else}
            <div class="flex items-center px-3 py-2 text-xs rounded-lg" style="color: var(--color-text-tertiary); background: var(--color-bg-elevated);">
              <Lock class="w-3.5 h-3.5 mr-2" />
              View Only
            </div>
          {/if}
          
          {#if permissions?.can_delete}
            <button
              on:click={() => { /* TODO: implement delete */ }}
              class="flex items-center px-3 py-2 text-xs rounded-lg transition-colors" style="color: var(--color-error); border: 1px solid color-mix(in srgb, var(--color-error) 30%, transparent);"
            >
              <Trash2 class="w-3.5 h-3.5 mr-2" />
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
      <p class="text-xs" style="color: var(--color-text-tertiary);">Product not found</p>
    </div>
  {/if}
</div>
