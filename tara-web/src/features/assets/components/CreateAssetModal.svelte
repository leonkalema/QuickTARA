<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { notifications } from '../../../lib/stores/notificationStore';
  import { assetApi } from '../../../lib/api/assetApi';
  import { AssetType, SecurityLevel, type CreateAssetRequest } from '../../../lib/types/asset';

  export let isOpen = false;
  export let productId: string;

  const dispatch = createEventDispatcher();

  let isLoading = false;
  let formData: CreateAssetRequest = {
    name: '',
    description: '',
    asset_type: AssetType.SOFTWARE,
    data_types: [],
    storage_location: '',
    scope_id: productId,
    confidentiality: SecurityLevel.MEDIUM,
    integrity: SecurityLevel.MEDIUM,
    availability: SecurityLevel.MEDIUM,
    authenticity_required: false,
    authorization_required: false
  };

  let dataTypeInput = '';

  $: formData.scope_id = productId;

  function addDataType() {
    if (dataTypeInput.trim() && !formData.data_types.includes(dataTypeInput.trim())) {
      formData.data_types = [...formData.data_types, dataTypeInput.trim()];
      dataTypeInput = '';
    }
  }

  function removeDataType(index: number) {
    formData.data_types = formData.data_types.filter((_, i) => i !== index);
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      event.preventDefault();
      addDataType();
    }
  }

  async function handleSubmit() {
    if (!formData.name.trim()) {
      notifications.show('Asset name is required', 'error');
      return;
    }

    isLoading = true;
    try {
      const newAsset = await assetApi.create(formData);
      dispatch('create', newAsset);
      resetForm();
    } catch (error) {
      console.error('Error creating asset:', error);
      notifications.show('Failed to create asset', 'error');
    } finally {
      isLoading = false;
    }
  }

  function resetForm() {
    formData = {
      name: '',
      description: '',
      asset_type: AssetType.SOFTWARE,
      data_types: [],
      storage_location: '',
      scope_id: productId,
      confidentiality: SecurityLevel.MEDIUM,
      integrity: SecurityLevel.MEDIUM,
      availability: SecurityLevel.MEDIUM,
      authenticity_required: false,
      authorization_required: false
    };
    dataTypeInput = '';
  }

  function handleClose() {
    resetForm();
    dispatch('close');
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" style="background: var(--color-bg-surface); border: 1px solid var(--color-border-default);">
      <!-- Header -->
      <div class="flex items-center justify-between p-5" style="border-bottom: 1px solid var(--color-border-default);">
        <h2 class="text-sm font-semibold" style="color: var(--color-text-primary);">Create New Asset</h2>
        <button
          on:click={handleClose}
          class="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form on:submit|preventDefault={handleSubmit} class="p-6 space-y-6">
        <!-- Basic Information -->
        <div class="space-y-4">
          <h3 class="text-xs font-semibold" style="color: var(--color-text-primary);">Basic Information</h3>
          
          <div>
            <label for="name" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
              Asset Name *
            </label>
            <input
              id="name"
              type="text"
              bind:value={formData.name}
              required
              class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              placeholder="e.g., ECU Firmware, CAN Bus Interface"
            />
          </div>

          <div>
            <label for="description" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
              Description
            </label>
            <textarea
              id="description"
              bind:value={formData.description}
              rows="3"
              class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              placeholder="Detailed description of the asset..."
            ></textarea>
          </div>

          <div>
            <label for="asset_type" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
              Asset Type *
            </label>
            <select
              id="asset_type"
              bind:value={formData.asset_type}
              required
              class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
            >
              {#each Object.values(AssetType) as type}
                <option value={type}>{type}</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="storage_location" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
              Storage Location
            </label>
            <input
              id="storage_location"
              type="text"
              bind:value={formData.storage_location}
              class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              placeholder="e.g., Internal Flash, External EEPROM, Cloud Storage"
            />
          </div>
        </div>

        <!-- Data Types -->
        <div class="space-y-4">
          <h3 class="text-xs font-semibold" style="color: var(--color-text-primary);">Data Types</h3>
          
          <div>
            <label for="data_type_input" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
              Add Data Types
            </label>
            <div class="flex space-x-2">
              <input
                id="data_type_input"
                type="text"
                bind:value={dataTypeInput}
                on:keypress={handleKeyPress}
                class="flex-1 px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
                placeholder="e.g., Personal Data, Diagnostic Data, Configuration Data"
              />
              <button
                type="button"
                on:click={addDataType}
                class="px-4 py-2 text-xs rounded-md transition-colors" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
              >
                Add
              </button>
            </div>
          </div>

          {#if formData.data_types.length > 0}
            <div class="flex flex-wrap gap-2">
              {#each formData.data_types as dataType, index}
                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-slate-100 text-slate-700">
                  {dataType}
                  <button
                    type="button"
                    on:click={() => removeDataType(index)}
                    class="ml-2 text-slate-500 hover:text-slate-700"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </button>
                </span>
              {/each}
            </div>
          {/if}
        </div>

        <!-- Security Properties -->
        <div class="space-y-4">
          <h3 class="text-xs font-semibold" style="color: var(--color-text-primary);">Security Properties (CIA)</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label for="confidentiality" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
                Confidentiality
              </label>
              <select
                id="confidentiality"
                bind:value={formData.confidentiality}
                class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              >
                {#each Object.values(SecurityLevel) as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </div>

            <div>
              <label for="integrity" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
                Integrity
              </label>
              <select
                id="integrity"
                bind:value={formData.integrity}
                class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              >
                {#each Object.values(SecurityLevel) as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </div>

            <div>
              <label for="availability" class="block text-xs font-medium mb-1" style="color: var(--color-text-secondary);">
                Availability
              </label>
              <select
                id="availability"
                bind:value={formData.availability}
                class="w-full px-3 py-2 text-xs rounded-md" style="background: var(--color-bg-inset); color: var(--color-text-primary); border: 1px solid var(--color-border-default);"
              >
                {#each Object.values(SecurityLevel) as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </div>
          </div>

          <!-- Additional Security Requirements -->
          <div class="space-y-3">
            <div class="flex items-center">
              <input
                id="authenticity_required"
                type="checkbox"
                bind:checked={formData.authenticity_required}
                class="h-4 w-4 rounded"
              />
              <label for="authenticity_required" class="ml-2 block text-xs" style="color: var(--color-text-secondary);">
                Authenticity Required
              </label>
            </div>

            <div class="flex items-center">
              <input
                id="authorization_required"
                type="checkbox"
                bind:checked={formData.authorization_required}
                class="h-4 w-4 rounded"
              />
              <label for="authorization_required" class="ml-2 block text-xs" style="color: var(--color-text-secondary);">
                Authorization Required
              </label>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-3 pt-5" style="border-top: 1px solid var(--color-border-default);">
          <button
            type="button"
            on:click={handleClose}
            class="px-4 py-2 text-xs rounded-md transition-colors" style="color: var(--color-text-secondary); border: 1px solid var(--color-border-default);"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            class="px-4 py-2 text-xs rounded-md disabled:opacity-50 transition-colors flex items-center space-x-2" style="background: var(--color-accent-primary); color: var(--color-text-inverse);"
          >
            {#if isLoading}
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Creating...</span>
            {:else}
              <span>Create Asset</span>
            {/if}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}
