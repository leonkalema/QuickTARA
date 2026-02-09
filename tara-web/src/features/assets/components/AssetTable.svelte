<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { assetApi } from '../../../lib/api/assetApi';
  import { notifications } from '../../../lib/stores/notificationStore';
  import { AssetType, SecurityLevel, type Asset, type CreateAssetRequest } from '../../../lib/types/asset';
  import ConfirmDialog from '../../../components/ConfirmDialog.svelte';
  import { authStore } from '$lib/stores/auth';
  import { canPerformTARA, isReadOnly } from '$lib/utils/permissions';

  export let assets: Asset[] = [];
  export let productId: string;

  const dispatch = createEventDispatcher();

  let editingCell: { assetId: string; field: string } | null = null;
  let editingValue = '';
  let newAsset: Partial<CreateAssetRequest> = {
    name: '',
    asset_type: AssetType.SOFTWARE,
    confidentiality: SecurityLevel.MEDIUM,
    integrity: SecurityLevel.MEDIUM,
    availability: SecurityLevel.MEDIUM,
    scope_id: productId
  };
  let isAddingNew = false;
  let isSaving = false;
  let showDeleteDialog = false;
  let assetToDelete: Asset | null = null;
  let isDeleting = false;

  // Role-based capabilities
  let canManageAssets = false;
  $: canManageAssets = canPerformTARA() && !isReadOnly();

  $: newAsset.scope_id = productId;

  function startEdit(asset: Asset, field: string) {
    if (!canManageAssets) return;
    editingCell = { assetId: asset.asset_id, field };
    editingValue = getFieldValue(asset, field);
  }

  function getFieldValue(asset: Asset, field: string): string {
    switch (field) {
      case 'name': return asset.name;
      case 'asset_type': return asset.asset_type;
      case 'confidentiality': return asset.confidentiality;
      case 'integrity': return asset.integrity;
      case 'availability': return asset.availability;
      case 'storage_location': return asset.storage_location || '';
      case 'description': return asset.description || '';
      default: return '';
    }
  }

  async function saveEdit(asset: Asset, field: string) {
    if (!editingCell || editingValue === getFieldValue(asset, field)) {
      cancelEdit();
      return;
    }

    if (!canManageAssets) { cancelEdit(); return; }
    isSaving = true;
    try {
      const updateData: any = { [field]: editingValue };
      const updatedAsset = await assetApi.update(asset.asset_id, updateData);
      
      // Update local asset
      const index = assets.findIndex(a => a.asset_id === asset.asset_id);
      if (index !== -1) {
        assets[index] = updatedAsset;
        assets = [...assets];
      }
      
      dispatch('assetUpdated', updatedAsset);
      notifications.show('Asset updated successfully', 'success');
    } catch (error) {
      console.error('Error updating asset:', error);
      notifications.show('Failed to update asset', 'error');
    } finally {
      isSaving = false;
      cancelEdit();
    }
  }

  function cancelEdit() {
    editingCell = null;
    editingValue = '';
  }

  function handleKeyPress(event: KeyboardEvent, asset: Asset, field: string) {
    if (event.key === 'Enter') {
      saveEdit(asset, field);
    } else if (event.key === 'Escape') {
      cancelEdit();
    }
  }

  async function addNewAsset() {
    if (!canManageAssets) return;
    if (!newAsset.name?.trim()) {
      notifications.show('Asset name is required', 'error');
      return;
    }

    isSaving = true;
    try {
      const assetData: CreateAssetRequest = {
        name: newAsset.name,
        description: newAsset.description || '',
        asset_type: newAsset.asset_type || AssetType.SOFTWARE,
        data_types: [],
        storage_location: newAsset.storage_location || '',
        scope_id: productId,
        confidentiality: newAsset.confidentiality || SecurityLevel.MEDIUM,
        integrity: newAsset.integrity || SecurityLevel.MEDIUM,
        availability: newAsset.availability || SecurityLevel.MEDIUM,
        authenticity_required: false,
        authorization_required: false
      };

      const createdAsset = await assetApi.create(assetData);
      assets = [...assets, createdAsset];
      
      // Reset new asset form
      newAsset = {
        name: '',
        asset_type: AssetType.SOFTWARE,
        confidentiality: SecurityLevel.MEDIUM,
        integrity: SecurityLevel.MEDIUM,
        availability: SecurityLevel.MEDIUM,
        scope_id: productId
      };
      
      dispatch('assetCreated', createdAsset);
      notifications.show('Asset created successfully', 'success');
      isAddingNew = false;
    } catch (error) {
      console.error('Error creating asset:', error);
      notifications.show('Failed to create asset', 'error');
    } finally {
      isSaving = false;
    }
  }

  function cancelNewAsset() {
    newAsset = {
      name: '',
      asset_type: AssetType.SOFTWARE,
      confidentiality: SecurityLevel.MEDIUM,
      integrity: SecurityLevel.MEDIUM,
      availability: SecurityLevel.MEDIUM,
      scope_id: productId
    };
    isAddingNew = false;
  }

  function getSecurityLevelStyle(level: SecurityLevel): string {
    switch (level) {
      case SecurityLevel.HIGH: return 'background: var(--color-risk-high-bg); color: var(--color-risk-high);';
      case SecurityLevel.MEDIUM: return 'background: var(--color-risk-medium-bg); color: var(--color-risk-medium);';
      case SecurityLevel.LOW: return 'background: var(--color-risk-low-bg); color: var(--color-risk-low);';
      default: return 'background: var(--color-bg-elevated); color: var(--color-text-tertiary);';
    }
  }

  function getAssetTypeIcon(type: AssetType): string {
    switch (type) {
      case AssetType.SOFTWARE: return '💻';
      case AssetType.HARDWARE: return '🔧';
      case AssetType.DATA: return '📊';
      case AssetType.COMMUNICATION: return '🌐';
      case AssetType.INTERFACE: return '⚙️';
      default: return '📦';
    }
  }

  function confirmDelete(asset: Asset) {
    if (!canManageAssets) return;
    assetToDelete = asset;
    showDeleteDialog = true;
  }

  async function deleteAsset() {
    if (!canManageAssets) return;
    if (!assetToDelete) return;
    
    isDeleting = true;
    try {
      await assetApi.delete(assetToDelete.asset_id);
      assets = assets.filter(a => a.asset_id !== assetToDelete!.asset_id);
      dispatch('assetDeleted', assetToDelete);
      notifications.show('Asset deleted successfully', 'success');
      
      showDeleteDialog = false;
      assetToDelete = null;
    } catch (error) {
      console.error('Error deleting asset:', error);
      notifications.show('Failed to delete asset', 'error');
    } finally {
      isDeleting = false;
    }
  }

  function handleDeleteCancel() {
    showDeleteDialog = false;
    assetToDelete = null;
    isDeleting = false;
  }
</script>

<div class="rounded-lg overflow-hidden" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
  <div class="px-4 py-3 flex items-center justify-between" style="background: var(--color-bg-elevated); border-bottom: 1px solid var(--color-border-subtle);">
    <h3 class="text-sm font-semibold" style="color: var(--color-text-primary);">Assets</h3>
    {#if canManageAssets}
      <button on:click={() => isAddingNew = true} class="px-3 py-1.5 text-xs font-medium rounded-md" style="background: var(--color-accent-primary); color: var(--color-text-inverse);">
        + Add Asset
      </button>
    {/if}
  </div>

  <!-- Table -->
  <div class="overflow-x-auto">
    <table class="min-w-full">
      <thead style="background: var(--color-bg-elevated);">
        <tr>
          <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider w-8" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Type</th>
          <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider min-w-48" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Name</th>
          <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider min-w-32" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Asset Type</th>
          <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider min-w-24" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">C</th>
          <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider min-w-24" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">I</th>
          <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider min-w-24" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">A</th>
          <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider min-w-40" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Storage</th>
          <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider min-w-64" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Description</th>
          <th class="px-4 py-2.5 text-left text-[11px] font-medium uppercase tracking-wider w-20" style="color: var(--color-text-tertiary); border-bottom: 1px solid var(--color-border-subtle);">Actions</th>
        </tr>
      </thead>
      <tbody>
        <!-- Existing Assets -->
        {#each assets as asset (asset.asset_id)}
          <tr style="border-bottom: 1px solid var(--color-border-subtle);">
            <!-- Type Icon -->
            <td class="px-4 py-3 text-center">
              <span class="text-lg">{getAssetTypeIcon(asset.asset_type)}</span>
            </td>
            
            <!-- Name -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'name'}
                <input
                  type="text"
                  bind:value={editingValue}
                  on:keydown={(e) => handleKeyPress(e, asset, 'name')}
                  on:blur={() => saveEdit(asset, 'name')}
                  class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);"
                  disabled={isSaving}
                  autofocus
                />
              {:else}
                {#if canManageAssets}
                  <button
                    on:click={() => startEdit(asset, 'name')}
                    class="text-left w-full px-2 py-1 rounded transition-colors text-xs font-medium" style="color: var(--color-text-primary);"
                  >
                    {asset.name}
                  </button>
                {:else}
                  <div class="px-2 py-1 text-xs font-medium" style="color: var(--color-text-primary);">{asset.name}</div>
                {/if}
              {/if}
            </td>

            <!-- Asset Type -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'asset_type'}
                <select
                  bind:value={editingValue}
                  on:change={() => saveEdit(asset, 'asset_type')}
                  on:blur={() => saveEdit(asset, 'asset_type')}
                  class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);"
                  disabled={isSaving}
                  autofocus
                >
                  {#each Object.values(AssetType) as type}
                    <option value={type}>{type}</option>
                  {/each}
                </select>
              {:else}
                {#if canManageAssets}
                  <button
                    on:click={() => startEdit(asset, 'asset_type')}
                    class="text-left w-full px-2 py-1 rounded transition-colors text-xs" style="color: var(--color-text-secondary);"
                  >
                    {asset.asset_type}
                  </button>
                {:else}
                  <div class="px-2 py-1 text-xs" style="color: var(--color-text-secondary);">{asset.asset_type}</div>
                {/if}
              {/if}
            </td>

            <!-- Confidentiality -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'confidentiality'}
                <select
                  bind:value={editingValue}
                  on:change={() => saveEdit(asset, 'confidentiality')}
                  on:blur={() => saveEdit(asset, 'confidentiality')}
                  class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);"
                  disabled={isSaving}
                  autofocus
                >
                  {#each Object.values(SecurityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              {:else}
                {#if canManageAssets}
                  <button
                    on:click={() => startEdit(asset, 'confidentiality')}
                    class="w-full px-2 py-1 rounded transition-colors"
                  >
                    <span class="inline-flex px-2 py-1 text-[10px] font-medium rounded-full" style="{getSecurityLevelStyle(asset.confidentiality)}">
                      {asset.confidentiality}
                    </span>
                  </button>
                {:else}
                  <span class="inline-flex px-2 py-1 text-[10px] font-medium rounded-full" style="{getSecurityLevelStyle(asset.confidentiality)}">
                    {asset.confidentiality}
                  </span>
                {/if}
              {/if}
            </td>

            <!-- Integrity -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'integrity'}
                <select
                  bind:value={editingValue}
                  on:change={() => saveEdit(asset, 'integrity')}
                  on:blur={() => saveEdit(asset, 'integrity')}
                  class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);"
                  disabled={isSaving}
                  autofocus
                >
                  {#each Object.values(SecurityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              {:else}
                {#if canManageAssets}
                  <button
                    on:click={() => startEdit(asset, 'integrity')}
                    class="w-full px-2 py-1 rounded transition-colors"
                  >
                    <span class="inline-flex px-2 py-1 text-[10px] font-medium rounded-full" style="{getSecurityLevelStyle(asset.integrity)}">
                      {asset.integrity}
                    </span>
                  </button>
                {:else}
                  <span class="inline-flex px-2 py-1 text-[10px] font-medium rounded-full" style="{getSecurityLevelStyle(asset.integrity)}">
                    {asset.integrity}
                  </span>
                {/if}
              {/if}
            </td>

            <!-- Availability -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'availability'}
                <select
                  bind:value={editingValue}
                  on:change={() => saveEdit(asset, 'availability')}
                  on:blur={() => saveEdit(asset, 'availability')}
                  class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);"
                  disabled={isSaving}
                  autofocus
                >
                  {#each Object.values(SecurityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              {:else}
                {#if canManageAssets}
                  <button
                    on:click={() => startEdit(asset, 'availability')}
                    class="w-full px-2 py-1 rounded transition-colors"
                  >
                    <span class="inline-flex px-2 py-1 text-[10px] font-medium rounded-full" style="{getSecurityLevelStyle(asset.availability)}">
                      {asset.availability}
                    </span>
                  </button>
                {:else}
                  <span class="inline-flex px-2 py-1 text-[10px] font-medium rounded-full" style="{getSecurityLevelStyle(asset.availability)}">
                    {asset.availability}
                  </span>
                {/if}
              {/if}
            </td>

            <!-- Storage Location -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'storage_location'}
                <input
                  type="text"
                  bind:value={editingValue}
                  on:keydown={(e) => handleKeyPress(e, asset, 'storage_location')}
                  on:blur={() => saveEdit(asset, 'storage_location')}
                  class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);"
                  disabled={isSaving}
                  autofocus
                />
              {:else}
                {#if canManageAssets}
                  <button
                    on:click={() => startEdit(asset, 'storage_location')}
                    class="text-left w-full px-2 py-1 rounded transition-colors text-xs" style="color: var(--color-text-secondary);"
                  >
                    {asset.storage_location || 'Click to add...'}
                  </button>
                {:else}
                  <div class="text-xs px-2 py-1" style="color: var(--color-text-secondary);">{asset.storage_location || '-'}</div>
                {/if}
              {/if}
            </td>

            <!-- Description -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'description'}
                <textarea
                  bind:value={editingValue}
                  on:keydown={(e) => e.key === 'Enter' && e.ctrlKey && saveEdit(asset, 'description')}
                  on:blur={() => saveEdit(asset, 'description')}
                  class="w-full px-2 py-1 rounded text-xs resize-none" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-accent-primary);"
                  rows="2"
                  disabled={isSaving}
                  autofocus
                ></textarea>
              {:else}
                {#if canManageAssets}
                  <button
                    on:click={() => startEdit(asset, 'description')}
                    class="text-left w-full px-2 py-1 rounded transition-colors text-xs" style="color: var(--color-text-secondary);"
                  >
                    {asset.description || 'Click to add...'}
                  </button>
                {:else}
                  <div class="text-xs px-2 py-1" style="color: var(--color-text-secondary);">{asset.description || '-'}</div>
                {/if}
              {/if}
            </td>

            <!-- Actions -->
            <td class="px-4 py-3">
              {#if canManageAssets}
                <button
                    on:click={() => confirmDelete(asset)}
                  class="text-xs font-medium" style="color: var(--color-error);"
                  disabled={isSaving}
                >
                  Delete
                </button>
              {/if}
            </td>
          </tr>
        {/each}

        <!-- Add New Asset Row -->
        {#if isAddingNew && canManageAssets}
          <tr style="background: var(--color-bg-elevated); border-bottom: 1px solid var(--color-border-default);">
            <!-- Type Icon -->
            <td class="px-4 py-3 text-center">
              <span class="text-lg">{getAssetTypeIcon(newAsset.asset_type || AssetType.SOFTWARE)}</span>
            </td>
            
            <!-- Name -->
            <td class="px-4 py-3">
              <input
                type="text"
                bind:value={newAsset.name}
                placeholder="Asset name..."
                class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
                autofocus
              />
            </td>

            <!-- Asset Type -->
            <td class="px-4 py-3">
              <select
                bind:value={newAsset.asset_type}
                class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              >
                {#each Object.values(AssetType) as type}
                  <option value={type}>{type}</option>
                {/each}
              </select>
            </td>

            <!-- Confidentiality -->
            <td class="px-4 py-3">
              <select
                bind:value={newAsset.confidentiality}
                class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              >
                {#each Object.values(SecurityLevel) as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </td>

            <!-- Integrity -->
            <td class="px-4 py-3">
              <select
                bind:value={newAsset.integrity}
                class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              >
                {#each Object.values(SecurityLevel) as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </td>

            <!-- Availability -->
            <td class="px-4 py-3">
              <select
                bind:value={newAsset.availability}
                class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              >
                {#each Object.values(SecurityLevel) as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </td>

            <!-- Storage Location -->
            <td class="px-4 py-3">
              <input
                type="text"
                bind:value={newAsset.storage_location}
                placeholder="Storage location..."
                class="w-full px-2 py-1 rounded text-xs" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              />
            </td>

            <!-- Description -->
            <td class="px-4 py-3">
              <textarea
                bind:value={newAsset.description}
                placeholder="Description..."
                class="w-full px-2 py-1 rounded text-xs resize-none" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
                rows="2"
              ></textarea>
            </td>

            <!-- Actions (empty for new row) -->
            <td class="px-4 py-3"></td>
          </tr>
          
          <!-- Action Row -->
          <tr style="background: var(--color-bg-elevated);">
            <td colspan="9" class="px-4 py-3">
              <div class="flex justify-end space-x-2">
                <button
                  on:click={cancelNewAsset}
                  class="px-3 py-1.5 rounded text-xs transition-colors" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
                  disabled={isSaving}
                >
                  Cancel
                </button>
                <button
                  on:click={addNewAsset}
                  disabled={isSaving || !newAsset.name?.trim()}
                  class="px-3 py-1.5 rounded text-xs disabled:opacity-50 transition-colors flex items-center space-x-2" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
                >
                  {#if isSaving}
                    <div class="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                    <span>Saving...</span>
                  {:else}
                    <span>Save Asset</span>
                  {/if}
                </button>
              </div>
            </td>
          </tr>
        {/if}
      </tbody>
    </table>
  </div>

  <!-- Delete Confirmation Dialog -->
<ConfirmDialog
  bind:isOpen={showDeleteDialog}
  title="Delete Asset"
  message="Are you sure you want to delete '{assetToDelete?.name}'? This action cannot be undone."
  confirmText="Delete"
  cancelText="Cancel"
  variant="danger"
  loading={isDeleting}
  on:confirm={deleteAsset}
  on:cancel={handleDeleteCancel}
/>

  <!-- Empty State -->
  {#if assets.length === 0 && !isAddingNew}
    <div class="text-center py-12">
      <div class="text-4xl mb-3">📦</div>
      <h3 class="text-sm font-semibold mb-1" style="color: var(--color-text-primary);">No assets yet</h3>
      <p class="text-xs mb-4" style="color: var(--color-text-tertiary);">Add your first asset to this product.</p>
      {#if canManageAssets}
        <button
          on:click={() => isAddingNew = true}
          class="px-3 py-2 rounded-md text-xs font-medium" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
        >
          Add First Asset
        </button>
      {/if}
    </div>
  {/if}
</div>
