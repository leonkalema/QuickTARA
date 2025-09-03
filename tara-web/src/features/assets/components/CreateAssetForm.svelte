<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { notifications } from '../../../lib/stores/notificationStore';
  import { assetApi } from '../../../lib/api/assetApi';
  import { AssetType, SecurityLevel, type CreateAssetRequest } from '../../../lib/types/asset';

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

  function handleCancel() {
    resetForm();
    dispatch('cancel');
  }
</script>

<!-- Form -->
<form on:submit|preventDefault={handleSubmit} class="space-y-6">
  <!-- Basic Information -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Basic Information</h3>
      
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700 mb-1">
          Asset Name *
        </label>
        <input
          id="name"
          type="text"
          bind:value={formData.name}
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500"
          placeholder="e.g., ECU Firmware, CAN Bus Interface"
        />
      </div>

      <div>
        <label for="asset_type" class="block text-sm font-medium text-gray-700 mb-1">
          Asset Type *
        </label>
        <select
          id="asset_type"
          bind:value={formData.asset_type}
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500"
        >
          {#each Object.values(AssetType) as type}
            <option value={type}>{type}</option>
          {/each}
        </select>
      </div>

      <div>
        <label for="storage_location" class="block text-sm font-medium text-gray-700 mb-1">
          Storage Location
        </label>
        <input
          id="storage_location"
          type="text"
          bind:value={formData.storage_location}
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500"
          placeholder="e.g., Internal Flash, External EEPROM"
        />
      </div>
    </div>

    <div class="space-y-4">
      <h3 class="text-lg font-medium text-gray-900">Security Properties (CIA)</h3>
      
      <div class="grid grid-cols-1 gap-4">
        <div>
          <label for="confidentiality" class="block text-sm font-medium text-gray-700 mb-1">
            Confidentiality
          </label>
          <select
            id="confidentiality"
            bind:value={formData.confidentiality}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500"
          >
            {#each Object.values(SecurityLevel) as level}
              <option value={level}>{level}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="integrity" class="block text-sm font-medium text-gray-700 mb-1">
            Integrity
          </label>
          <select
            id="integrity"
            bind:value={formData.integrity}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500"
          >
            {#each Object.values(SecurityLevel) as level}
              <option value={level}>{level}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="availability" class="block text-sm font-medium text-gray-700 mb-1">
            Availability
          </label>
          <select
            id="availability"
            bind:value={formData.availability}
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500"
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
            class="h-4 w-4 text-slate-600 focus:ring-slate-500 border-gray-300 rounded"
          />
          <label for="authenticity_required" class="ml-2 block text-sm text-gray-700">
            Authenticity Required
          </label>
        </div>

        <div class="flex items-center">
          <input
            id="authorization_required"
            type="checkbox"
            bind:checked={formData.authorization_required}
            class="h-4 w-4 text-slate-600 focus:ring-slate-500 border-gray-300 rounded"
          />
          <label for="authorization_required" class="ml-2 block text-sm text-gray-700">
            Authorization Required
          </label>
        </div>
      </div>
    </div>
  </div>

  <!-- Description -->
  <div>
    <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
      Description
    </label>
    <textarea
      id="description"
      bind:value={formData.description}
      rows="3"
      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500"
      placeholder="Detailed description of the asset..."
    ></textarea>
  </div>

  <!-- Data Types -->
  <div class="space-y-4">
    <h3 class="text-lg font-medium text-gray-900">Data Types</h3>
    
    <div>
      <label for="data_type_input" class="block text-sm font-medium text-gray-700 mb-1">
        Add Data Types
      </label>
      <div class="flex space-x-2">
        <input
          id="data_type_input"
          type="text"
          bind:value={dataTypeInput}
          on:keypress={handleKeyPress}
          class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-slate-500 focus:border-slate-500"
          placeholder="e.g., Personal Data, Diagnostic Data"
        />
        <button
          type="button"
          on:click={addDataType}
          class="px-4 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700 transition-colors"
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

  <!-- Actions -->
  <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
    <button
      type="button"
      on:click={handleCancel}
      class="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
    >
      Cancel
    </button>
    <button
      type="submit"
      disabled={isLoading}
      class="px-4 py-2 bg-slate-600 text-white rounded-md hover:bg-slate-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
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
