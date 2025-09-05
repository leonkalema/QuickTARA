<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { assetApi } from '../../../lib/api/assetApi';
  import { notifications } from '../../../lib/stores/notificationStore';
  import { AssetType, SecurityLevel, type Asset, type CreateAssetRequest } from '../../../lib/types/asset';
  import ConfirmDialog from '../../../components/ConfirmDialog.svelte';

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

  $: newAsset.scope_id = productId;

  function startEdit(asset: Asset, field: string) {
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

  function getSecurityLevelColor(level: SecurityLevel): string {
    switch (level) {
      case SecurityLevel.HIGH: return 'text-red-600 bg-red-50';
      case SecurityLevel.MEDIUM: return 'text-yellow-600 bg-yellow-50';
      case SecurityLevel.LOW: return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
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
    assetToDelete = asset;
    showDeleteDialog = true;
  }

  async function deleteAsset() {
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

<div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
  <!-- Table Header -->
  <div class="bg-gray-50 px-6 py-3 border-b border-gray-200">
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-medium text-gray-900">Assets</h3>
      <button
        on:click={() => isAddingNew = true}
        class="px-3 py-1.5 bg-slate-600 text-white text-sm rounded-md hover:bg-slate-700 transition-colors"
      >
        + Add Asset
      </button>
    </div>
  </div>

  <!-- Table -->
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-8">
            Type
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-48">
            Name
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-32">
            Asset Type
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-24">
            C
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-24">
            I
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-24">
            A
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-40">
            Storage Location
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-64">
            Description
          </th>
          <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
            Actions
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <!-- Existing Assets -->
        {#each assets as asset (asset.asset_id)}
          <tr class="hover:bg-gray-50">
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
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  disabled={isSaving}
                  autofocus
                />
              {:else}
                <button
                  on:click={() => startEdit(asset, 'name')}
                  class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors font-medium text-gray-900"
                >
                  {asset.name}
                </button>
              {/if}
            </td>

            <!-- Asset Type -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'asset_type'}
                <select
                  bind:value={editingValue}
                  on:change={() => saveEdit(asset, 'asset_type')}
                  on:blur={() => saveEdit(asset, 'asset_type')}
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  disabled={isSaving}
                  autofocus
                >
                  {#each Object.values(AssetType) as type}
                    <option value={type}>{type}</option>
                  {/each}
                </select>
              {:else}
                <button
                  on:click={() => startEdit(asset, 'asset_type')}
                  class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors text-sm"
                >
                  {asset.asset_type}
                </button>
              {/if}
            </td>

            <!-- Confidentiality -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'confidentiality'}
                <select
                  bind:value={editingValue}
                  on:change={() => saveEdit(asset, 'confidentiality')}
                  on:blur={() => saveEdit(asset, 'confidentiality')}
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  disabled={isSaving}
                  autofocus
                >
                  {#each Object.values(SecurityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              {:else}
                <button
                  on:click={() => startEdit(asset, 'confidentiality')}
                  class="w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors"
                >
                  <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full {getSecurityLevelColor(asset.confidentiality)}">
                    {asset.confidentiality}
                  </span>
                </button>
              {/if}
            </td>

            <!-- Integrity -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'integrity'}
                <select
                  bind:value={editingValue}
                  on:change={() => saveEdit(asset, 'integrity')}
                  on:blur={() => saveEdit(asset, 'integrity')}
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  disabled={isSaving}
                  autofocus
                >
                  {#each Object.values(SecurityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              {:else}
                <button
                  on:click={() => startEdit(asset, 'integrity')}
                  class="w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors"
                >
                  <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full {getSecurityLevelColor(asset.integrity)}">
                    {asset.integrity}
                  </span>
                </button>
              {/if}
            </td>

            <!-- Availability -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'availability'}
                <select
                  bind:value={editingValue}
                  on:change={() => saveEdit(asset, 'availability')}
                  on:blur={() => saveEdit(asset, 'availability')}
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  disabled={isSaving}
                  autofocus
                >
                  {#each Object.values(SecurityLevel) as level}
                    <option value={level}>{level}</option>
                  {/each}
                </select>
              {:else}
                <button
                  on:click={() => startEdit(asset, 'availability')}
                  class="w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors"
                >
                  <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full {getSecurityLevelColor(asset.availability)}">
                    {asset.availability}
                  </span>
                </button>
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
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                  disabled={isSaving}
                  autofocus
                />
              {:else}
                <button
                  on:click={() => startEdit(asset, 'storage_location')}
                  class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors text-sm text-gray-600"
                >
                  {asset.storage_location || 'Click to add...'}
                </button>
              {/if}
            </td>

            <!-- Description -->
            <td class="px-4 py-3">
              {#if editingCell?.assetId === asset.asset_id && editingCell?.field === 'description'}
                <textarea
                  bind:value={editingValue}
                  on:keydown={(e) => e.key === 'Enter' && e.ctrlKey && saveEdit(asset, 'description')}
                  on:blur={() => saveEdit(asset, 'description')}
                  class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                  rows="2"
                  disabled={isSaving}
                  autofocus
                ></textarea>
              {:else}
                <button
                  on:click={() => startEdit(asset, 'description')}
                  class="text-left w-full px-2 py-1 hover:bg-blue-50 rounded transition-colors text-sm text-gray-600"
                >
                  {asset.description || 'Click to add...'}
                </button>
              {/if}
            </td>

            <!-- Actions -->
            <td class="px-4 py-3">
              <button
                  on:click={() => confirmDelete(asset)}
                class="text-red-600 hover:text-red-900 text-sm font-medium"
                disabled={isSaving}
              >
                Delete
              </button>
            </td>
          </tr>
        {/each}

        <!-- Add New Asset Row -->
        {#if isAddingNew}
          <tr class="bg-blue-50 border-2 border-blue-200">
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
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                autofocus
              />
            </td>

            <!-- Asset Type -->
            <td class="px-4 py-3">
              <select
                bind:value={newAsset.asset_type}
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
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
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
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
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
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
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
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
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </td>

            <!-- Description -->
            <td class="px-4 py-3">
              <textarea
                bind:value={newAsset.description}
                placeholder="Description..."
                class="w-full px-2 py-1 border border-blue-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                rows="2"
              ></textarea>
            </td>

            <!-- Actions (empty for new row) -->
            <td class="px-4 py-3"></td>
          </tr>
          
          <!-- Action Row -->
          <tr class="bg-blue-50">
            <td colspan="9" class="px-4 py-3">
              <div class="flex justify-end space-x-2">
                <button
                  on:click={cancelNewAsset}
                  class="px-3 py-1.5 text-gray-600 bg-gray-100 hover:bg-gray-200 rounded text-sm transition-colors"
                  disabled={isSaving}
                >
                  Cancel
                </button>
                <button
                  on:click={addNewAsset}
                  disabled={isSaving || !newAsset.name?.trim()}
                  class="px-3 py-1.5 bg-slate-600 text-white rounded text-sm hover:bg-slate-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
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
      <div class="text-gray-400 text-6xl mb-4">📦</div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No assets yet</h3>
      <p class="text-gray-500 mb-4">Start by adding your first asset to this product.</p>
      <button
        on:click={() => isAddingNew = true}
        class="px-4 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700 transition-colors"
      >
        Add First Asset
      </button>
    </div>
  {/if}
</div>
